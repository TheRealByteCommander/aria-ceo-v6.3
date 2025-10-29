"""
Aria CEO - Version 7.0 (Config-Driven Agent Network)

Ziele v7:
- Agenten, Skills und Tool-Zuordnung sind vollständig konfigurationsgetrieben (YAML)
- Minimale Codeänderungen nötig für neue Fähigkeiten/Teams
- Weiterhin AutoGen-basiert, mit freier Kommunikation und optionalen Integrationen
"""

import os
import asyncio
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import yaml
from loguru import logger
import websockets

from autogen import AssistantAgent, GroupChat, GroupChatManager, ConversableAgent
from autogen.agentchat.contrib.agent_with_tool_calling import AgentWithToolCalling

from memory_manager import MemoryManager
import tools as builtin_tools


def _safe_get(dct: Dict[str, Any], path: str, default=None):
    cur = dct
    for key in path.split('.'):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


class ToolRegistry:
    """Registriert Tool-Funktionen aus tools.py und setzt benötigte Umgebungsvariablen aus YAML."""

    def __init__(self, base_config: Dict[str, Any], tools_yaml: Dict[str, Any]):
        self.base_config = base_config or {}
        self.tools_yaml = tools_yaml or {}
        self._available: Dict[str, Any] = {}
        self._load_builtin()

    def _load_builtin(self):
        for attr in dir(builtin_tools):
            func = getattr(builtin_tools, attr)
            if callable(func):
                self._available[attr] = func

    def resolve_env_value(self, value: Any):
        # Erlaubt ${...} Verweise auf config.yaml in ganzen Strings oder eingebettet
        if not isinstance(value, str):
            return value
        out = ""
        i = 0
        while i < len(value):
            if value[i:i+2] == '${':
                j = value.find('}', i+2)
                if j != -1:
                    path = value[i+2:j]
                    out += str(_safe_get(self.base_config, path, ''))
                    i = j + 1
                    continue
            out += value[i]
            i += 1
        return out

    def apply_env(self, tool_def: Dict[str, Any]):
        env = tool_def.get('env') or {}
        for k, v in env.items():
            os.environ[k] = str(self.resolve_env_value(v))

    def get(self, name: str):
        # Optional: env aus tools_v7.yaml anwenden
        for entry in self.tools_yaml.get('tools', []):
            if entry.get('name') == name:
                self.apply_env(entry)
                break
        return self._available.get(name)


class AriaCEOv7:
    def __init__(self, slack_client=None):
        self.version = '7.0-config-driven'
        self.slack_client = slack_client
        self.current_channel = None
        self.memory_manager = MemoryManager()

        self.base_config = self._load_yaml(Path('/opt/aria-system/config/config.yaml'))
        self.agents_cfg = self._load_yaml(self._prefer_system('config/agents_v7.yaml'))
        self.tools_cfg = self._load_yaml(self._prefer_system('config/tools_v7.yaml'))

        self.tool_registry = ToolRegistry(self.base_config, self.tools_cfg)

        self.ws_url = _safe_get(self.base_config, 'dashboard.websocket_url', 'ws://192.168.178.150:8090/ws')
        self.ws_connection = None

        self.agents: Dict[str, ConversableAgent] = {}
        self._validate_configs()
        self._create_agents()
        self._create_group_chat()

        logger.info(f"Aria CEO initialized - Version {self.version}")

    def _prefer_system(self, rel: str) -> Path:
        system = Path('/opt/aria-system') / rel
        local = Path(rel)
        return system if system.exists() else local

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        logger.warning(f"YAML nicht gefunden: {path}")
        return {}

    def _get_llm_config(self, profile: str) -> Dict[str, Any]:
        # profile-String wie "mac_mini.aria" → liefert Model + Endpoint aus config.yaml
        parts = (profile or '').split('.')
        if len(parts) != 2:
            return {"config_list": [], "timeout": 600, "temperature": 0.7}
        host_root, model_key = parts
        llm = self.base_config.get('llm', {})
        host_conf = llm.get(host_root, {})
        model_map = host_conf.get('models', {})
        model_name = model_map.get(model_key, 'llama3.1:8b')
        base_url = f"http://{host_conf.get('host', '127.0.0.1')}:{host_conf.get('port', 11434)}/v1"
        return {
            "config_list": [
                {"model": model_name, "base_url": base_url, "api_key": "ollama"}
            ],
            "timeout": 600,
            "temperature": 0.7,
        }

    def _validate_configs(self):
        errors: List[str] = []
        agents = self.agents_cfg.get('agents')
        if not isinstance(agents, list) or not agents:
            errors.append("agents_v7.yaml: 'agents' muss eine nicht-leere Liste sein")
        else:
            for idx, agent in enumerate(agents):
                name = agent.get('name')
                if not name:
                    errors.append(f"agents_v7.yaml: Agent #{idx} ohne 'name'")
                profile = agent.get('llm_profile')
                if not profile:
                    errors.append(f"agents_v7.yaml: Agent '{name}' ohne 'llm_profile'")
                # grobe Prüfung, ob das Profil in config.yaml verankert werden kann
                parts = (profile or '').split('.')
                if len(parts) == 2:
                    host_root, model_key = parts
                    if host_root not in (self.base_config.get('llm') or {}):
                        errors.append(f"config.yaml: llm.'{host_root}' fehlt für Agent '{name}'")
                else:
                    errors.append(f"agents_v7.yaml: llm_profile '{profile}' von Agent '{name}' ist ungültig (muss 'host.key' sein)")

                for tool_name in agent.get('skills', []) or []:
                    # Warnung nur, Fehler wenn Tool komplett fehlt
                    if not hasattr(builtin_tools, tool_name):
                        errors.append(f"tools.py: Tool '{tool_name}' existiert nicht (Agent '{name}')")

        # Tools-Datei minimale Prüfung
        for entry in self.tools_cfg.get('tools', []) or []:
            if 'name' not in entry:
                errors.append("tools_v7.yaml: Ein Tool-Eintrag fehlt 'name'")

        if errors:
            for e in errors:
                logger.error(e)
            raise SystemExit("Konfigurationsvalidierung fehlgeschlagen. Bitte YAMLs korrigieren.")

    def _load_agent_memory(self, agent: ConversableAgent):
        messages = self.memory_manager.get_memory(agent.name)
        if messages and isinstance(agent, AssistantAgent):
            agent._oai_messages[agent] = messages

    def _save_agent_memory(self, agent: ConversableAgent):
        if isinstance(agent, AssistantAgent):
            messages = agent._oai_messages.get(agent, [])
            if messages:
                self.memory_manager.save_memory(agent.name, messages)

    def _create_agents(self):
        self.agents = {}
        for agent_def in self.agents_cfg.get('agents', []):
            name = agent_def['name']
            system_message = agent_def.get('system_message', '')
            llm_profile = agent_def.get('llm_profile', '')
            llm_config = self._get_llm_config(llm_profile)

            agent = AgentWithToolCalling(
                name=name,
                system_message=system_message,
                llm_config=llm_config,
                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            )

            for tool_name in agent_def.get('skills', []):
                func = self.tool_registry.get(tool_name)
                if func is None:
                    logger.warning(f"Tool '{tool_name}' nicht gefunden für Agent '{name}'")
                    continue
                agent.register_for_llm(func)
                agent.register_for_exec(func)

            self._load_agent_memory(agent)
            self.agents[name] = agent

        # Backwards kompatible Kurzreferenzen (falls in externem Code benutzt)
        for key in ['Aria', 'Sam', 'Jordan', 'Taylor', 'Morgan', 'Alex', 'Riley']:
            if key in self.agents:
                setattr(self, key.lower(), self.agents[key])

    def _create_group_chat(self):
        gc = self.agents_cfg.get('group_chat', {})
        self.group_chat = GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=gc.get('max_round', 250),
            speaker_selection_method=gc.get('speaker_selection_method', 'auto'),
            allow_repeat_speaker=gc.get('allow_repeat_speaker', True),
        )
        self.manager = GroupChatManager(groupchat=self.group_chat, llm_config=self._get_llm_config('mac_mini.aria'))

    async def _broadcast(self, event_type: str, data: Dict[str, Any]):
        try:
            if not getattr(self, 'ws_connection', None) or self.ws_connection.closed:
                try:
                    self.ws_connection = await asyncio.wait_for(websockets.connect(self.ws_url), timeout=2.0)
                except Exception as e:
                    logger.debug(f"Dashboard WS nicht erreichbar: {e}")
                    return

            payload = {"type": event_type, "timestamp": datetime.now().isoformat(), "data": data}
            if self.ws_connection and not self.ws_connection.closed:
                await self.ws_connection.send(json.dumps(payload))
        except Exception as e:
            logger.debug(f"Broadcast-Fehler: {e}")
            self.ws_connection = None

    async def run_project(self, description: str, user: str = '', channel: str = '') -> Dict[str, Any]:
        project_id = f"project-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.current_channel = channel
        await self._broadcast('project_start', {"project_id": project_id, "message": description})

        init_msg = (
            f"🚀 New Project: {project_id}\n\n"
            f"Description:\n{description}\n\n"
            f"IMPORTANT: Collaborate freely. Provide backend, frontend, tests, Dockerfiles, docs."
        )

        await self.aria.a_initiate_chat(self.manager, message=init_msg)

        messages = self.group_chat.messages
        await self._broadcast('project_end', {"project_id": project_id, "total_messages": len(messages)})

        # Speicher Memory
        for agent in self.agents.values():
            self._save_agent_memory(agent)
        self.memory_manager.save_memory("GroupChat", messages)

        return {"project_id": project_id, "status": "completed", "messages": len(messages)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aria CEO v7.0 (config-driven)')
    parser.add_argument('--validate-config', action='store_true', help='Nur YAML-Konfiguration validieren und beenden')
    parser.add_argument('--project', type=str, default='', help='Projektbeschreibung zum Start des Chats')
    parser.add_argument('--dry-run', action='store_true', help='Nur Initialisierung ohne Chat ausführen')
    args = parser.parse_args()

    try:
        ceo = AriaCEOv7()
        logger.info("Aria CEO v7.0 bereit (config-driven)")
        if args.validate_config:
            logger.info("Konfiguration gültig.")
            sys.exit(0)
        if args.dry_run or not args.project:
            logger.info("Dry-Run abgeschlossen (keine Chat-Ausführung).")
            sys.exit(0)
        # Chat ausführen
        asyncio.run(ceo.run_project(args.project))
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Startfehler: {e}")
        sys.exit(1)

