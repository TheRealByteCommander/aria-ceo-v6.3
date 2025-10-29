"""
Aria CEO - Version 6.3 (Memory Edition)
Fixed Issues:
- Disabled endless clarification loop
- Added dashboard WebSocket broadcasts

Changes:
1. _needs_clarification() now always returns False
2. _run_group_chat() now broadcasts to dashboard via WebSocket
3. **NEW:** Integrated persistent conversation memory using diskcache for all agents.
"""

import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
import yaml
import time
import websockets

from autogen import AssistantAgent, GroupChat, GroupChatManager, ConversableAgent
from autogen.agentchat.contrib.agent_with_tool_calling import AgentWithToolCalling

# Import Memory Manager
from memory_manager import MemoryManager
import tools

# Import integrations
try:
    from integrations.github_integration import GitHubIntegration
    GITHUB_INTEGRATION_AVAILABLE = True
except ImportError:
    GITHUB_INTEGRATION_AVAILABLE = False
    GitHubIntegration = None  # type: ignore

try:
    from integrations.dockerhub_integration import DockerHubIntegration
    DOCKERHUB_INTEGRATION_AVAILABLE = True
except ImportError:
    DOCKERHUB_INTEGRATION_AVAILABLE = False
    DockerHubIntegration = None  # type: ignore

# Import utilities (to be created)
try:
    from utils.code_file_generator import CodeFileGenerator
    CODE_GEN_AVAILABLE = True
except ImportError:
    CODE_GEN_AVAILABLE = False
    logger.warning("Code file generator not available")

try:
    from utils.llm_monitor import LLMMonitor
    LLM_MONITOR_AVAILABLE = True
except ImportError:
    LLM_MONITOR_AVAILABLE = False
    logger.warning("LLM monitor not available")


class AriaCEO:
    """
    Aria - Virtual CEO v6.3
    Memory Edition
    """
    
    def __init__(self, slack_client=None):
        self.version = "6.3-memory-edition"
        self.slack_client = slack_client
        self.current_channel = None
        logger.info(f"Initializing Aria CEO - Version {self.version}")
        
        # Slack client for status updates (HOTFIX)
        self.slack_client = slack_client
        self.current_channel = None
        
        # Load config
        self.config = self._load_config()
        
        # Initialize Database Configuration
        self.db_config = self.config.get('database', {})
        
        # Initialize GitHub integration (optional)
        github_config = self.config.get('github', {})
        if GITHUB_INTEGRATION_AVAILABLE and GitHubIntegration is not None:
            try:
                self.github = GitHubIntegration(github_config)
            except Exception:
                class _Disabled:
                    enabled = False
                self.github = _Disabled()
                logger.warning("GitHubIntegration initialization failed; disabled.")
        else:
            class _Disabled:
                enabled = False
            self.github = _Disabled()
            logger.warning("GitHubIntegration not available; disabled.")

        # Initialize Docker Hub integration (optional)
        dockerhub_config = self.config.get('docker_hub', {})
        if DOCKERHUB_INTEGRATION_AVAILABLE and DockerHubIntegration is not None:
            try:
                self.dockerhub = DockerHubIntegration(dockerhub_config)
            except Exception:
                class _Disabled:
                    enabled = False
                self.dockerhub = _Disabled()
                logger.warning("DockerHubIntegration initialization failed; disabled.")
        else:
            class _Disabled:
                enabled = False
            self.dockerhub = _Disabled()
            logger.warning("DockerHubIntegration not available; disabled.")
        
        # Initialize LLM Monitor
        if LLM_MONITOR_AVAILABLE:
            self.llm_monitor = LLMMonitor(self.config.get('llm', {}))
        else:
            self.llm_monitor = None
        
        # WebSocket connection for dashboard broadcasts
        self.ws_url = self.config.get('dashboard', {}).get('websocket_url', 'ws://192.168.178.150:8090/ws')
        self.ws_connection = None
        
        # Initialize Memory Manager
        self.memory_manager = MemoryManager()
        
        # Load agent configurations
        self.agent_configs = self._load_agent_configs()
        
        # Create agents
        self._create_agents()
        
        # Create group chat with free communication
        self._create_group_chat()
        
        logger.info(f"Aria CEO initialized - Version {self.version}")
        logger.info("✨ Features enabled:")
        logger.info("  ✅ GitHub Integration" if self.github.enabled else "  ❌ GitHub Integration")
        logger.info("  ✅ Docker Hub Integration" if self.dockerhub.enabled else "  ❌ Docker Hub Integration")
        logger.info("  ✅ Free Worker Communication")
        logger.info("  ✅ LLM Monitoring" if self.llm_monitor else "  ❌ LLM Monitoring")
        logger.info("  ✅ Dashboard Broadcasts")
        logger.info("  ✅ Persistent Agent Memory")
        logger.info("  ❌ Clarification Questions (DISABLED)")
    
    def _load_config(self):
        """Load configuration"""
        config_path = Path("/opt/aria-system/config/config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

    def _load_agent_configs(self):
        """Load agent configurations from YAML file"""
        system_config = Path("/opt/aria-system/config/agents_config.yaml")
        local_config = Path(__file__).parent / "agents_config.yaml"
        config_path = system_config if system_config.exists() else local_config
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
                return data.get('agents', {})
        logger.error("agents_config.yaml not found in system or local paths!")
        return {}
    
    def _get_llm_config(self):
        """Get LLM configuration for agents"""
        llm_config = self.config.get('llm', {})
        config_list = []
        
        # Mac Mini server
        mac_mini = llm_config.get('mac_mini', {})
        if mac_mini:
            config_list.append({
                "model": mac_mini.get('models', {}).get('aria', 'llama3.1:8b'),
                "base_url": f"http://{mac_mini.get('host', '192.168.178.159')}:{mac_mini.get('port', 11434)}/v1",
                "api_key": "ollama",
            })
        
        # GMKTec server (if available)
        gmktec = llm_config.get('gmktec', {})
        if gmktec:
            config_list.append({
                "model": gmktec.get('models', {}).get('sam', 'qwen2.5-coder:32b'),
                "base_url": f"http://{gmktec.get('host', '192.168.178.155')}:{gmktec.get('port', 11434)}/v1",
                "api_key": "ollama",
            })
        
        return {
            "config_list": config_list,
            "timeout": 600,
            "temperature": 0.7,
        }

    def _load_agent_memory(self, agent: ConversableAgent):
        """Loads conversation history from the MemoryManager and sets it to the agent."""
        messages = self.memory_manager.get_memory(agent.name)
        if messages:
            # AutoGen agents store messages in the _oai_messages attribute
            # We need to set the messages for the specific receiver (the agent itself)
            # The key is a tuple: (agent, None) for the agent's own history
            # Note: For AssistantAgent, we use _oai_messages to inject prior history.
            if isinstance(agent, AssistantAgent):
                agent._oai_messages[agent] = messages
                logger.info(f"Loaded {len(messages)} messages for agent {agent.name}")
            
    def _save_agent_memory(self, agent: ConversableAgent):
        """Saves the conversation history of the agent to the MemoryManager."""
        if isinstance(agent, AssistantAgent):
            # The agent's own history is stored under the key (agent, None)
            messages = agent._oai_messages.get(agent, [])
            if messages:
                self.memory_manager.save_memory(agent.name, messages)
                logger.debug(f"Saved {len(messages)} messages for agent {agent.name}.")

    def _save_group_chat_memory(self):
        """Saves the conversation history of the GroupChat to the MemoryManager."""
        # The GroupChat object holds the messages for the entire conversation
        if self.group_chat.messages:
            self.memory_manager.save_memory("GroupChat", self.group_chat.messages)
            logger.info(f"Saved {len(self.group_chat.messages)} messages for GroupChat.")
            
    def _load_group_chat_memory(self):
        """Loads the conversation history for the GroupChat."""
        messages = self.memory_manager.get_memory("GroupChat")
        if messages:
            self.group_chat.messages = messages
            logger.info(f"Loaded {len(messages)} messages into GroupChat.")
    
    def _create_agents(self):
        """Create all team agents with free communication instructions and load memory"""
        llm_config = self._get_llm_config()
        
        self.agents = {}
        for agent_name, config in self.agent_configs.items():
            system_message = config['system_message']
            
            # Use AgentWithToolCalling to enable tool use
            agent = AgentWithToolCalling(
                name=agent_name,
                system_message=system_message,
                llm_config=llm_config,
                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            )
            
            # Register tools based on the YAML configuration
            for tool_name in config.get('skills', []):
                if hasattr(tools, tool_name):
                    tool_func = getattr(tools, tool_name)
                    
                    # Special handling for tools that need DB config
                    # We set environment variables here, which tools.py will read
                    if tool_name == 'queue_task':
                        redis_conf = self.db_config.get('redis', {})
                        if redis_conf:
                            os.environ['REDIS_HOST'] = redis_conf.get('host', '')
                            os.environ['REDIS_PORT'] = str(redis_conf.get('port', 6379))
                    
                    if tool_name == 'log_test_result_to_mongo':
                        mongo_conf = self.db_config.get('mongodb', {})
                        if mongo_conf:
                            os.environ['MONGO_URI'] = f"mongodb://{mongo_conf.get('host')}:{mongo_conf.get('port')}/"
                            os.environ['MONGO_DB_NAME'] = mongo_conf.get('database', 'aria_logs')
                            
                    agent.register_for_llm(tool_func)
                    agent.register_for_exec(tool_func)
                    logger.info(f"Tool '{tool_name}' registered for agent '{agent_name}'")
                else:
                    logger.warning(f"Tool '{tool_name}' not found in tools.py for agent '{agent_name}'")
            
            # Load memory for the agent
            self._load_agent_memory(agent)
            
            # Store agent in the instance
            setattr(self, agent_name.lower(), agent)
            self.agents[agent_name] = agent
            
        # Assign agents to instance variables for backward compatibility
        self.aria = self.agents['Aria']
        self.sam = self.agents['Sam']
        self.jordan = self.agents['Jordan']
        self.taylor = self.agents['Taylor']
        self.alex = self.agents['Alex']
        self.riley = self.agents['Riley']
        # self.casey = self.agents['Casey'] # Removed Casey for optimization
        
        logger.info(f"All {len(self.agents)} agents created successfully and memory loaded")
    
    def _create_group_chat(self):
        """Create group chat with free communication and load memory"""
        
        # All agents in the team (dynamically loaded)
        agents = list(self.agents.values())
        
        # Free communication: any agent can speak at any time
        self.group_chat = GroupChat(
            agents=agents,
            messages=[],
            max_round=250,  # Increased for complex projects
            speaker_selection_method="auto",  # Let agents decide who speaks next
            allow_repeat_speaker=True,  # Allow multiple messages from same agent
        )
        
        # Load previous GroupChat history
        self._load_group_chat_memory()
        
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self._get_llm_config(),
        )
        
        logger.info("GroupChat created with free communication support")

    
    async def handle_project(self, description, user, channel):
        """
        Handle a complete project request
        
        Args:
            description: Project description from user
            user: User who requested the project
            channel: Slack channel for communication
        
        Returns:
            dict: Project results including GitHub/Docker Hub URLs
        """
        project_id = f"project-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        logger.info(f"Starting project: {project_id}")
        logger.info(f"Description: {description}")
        
        # Store channel for status updates
        self.current_channel = channel
        
        # BUGFIX #1: Clarification is now completely disabled
        # No more endless loops!
        
        # Start LLM monitoring
        if self.llm_monitor:
            await self.llm_monitor.start_monitoring(project_id)
        
        # Initial message to team
        initial_message = f"""
🚀 **New Project: {project_id}**

**Description:**
{description}

**Team:**
- Sam (Backend Developer)
- Jordan (Frontend Developer)
- Taylor (QA Engineer)
- Morgan (DevOps Engineer)
- Alex (Project Manager)
- Riley (Research Specialist)
- Casey (Audio/Video Specialist)

**IMPORTANT:**
- Talk to each other freely! No need to wait for me.
- Ask questions directly: "Sam, ..." or "Jordan, ..."
- Discuss and collaborate as a real team.
- Every project needs: Backend, Tests, Dockerfile, docker-compose.yml, README.md

**Let's start! Sam and Jordan, please discuss the architecture first.**
"""
        
        # Run group chat
        try:
            # The loaded group chat messages are already in self.group_chat.messages
            # We don't reset them here to maintain context from previous runs.
            
            result = await self._run_group_chat(initial_message, project_id)
            
            # Save the full conversation history
            self._save_group_chat_memory()
            
            # Save individual agent memories (optional, but good practice)
            for agent in self.agents.values():
                self._save_agent_memory(agent)
            
            # Extract code files from conversation
            project_dir = await self._extract_and_save_code(result, project_id)
            
            # Store in GitHub
            github_info = None
            if self.github.enabled and project_dir:
                github_info = self.github.store_project(
                    project_id,
                    project_dir,
                    description=description
                )
            
            # Build and push to Docker Hub
            dockerhub_info = None
            if self.dockerhub.enabled and project_dir:
                dockerhub_info = self.dockerhub.build_and_push(
                    project_dir,
                    project_id
                )
            
            # Stop LLM monitoring
            if self.llm_monitor:
                await self.llm_monitor.stop_monitoring(project_id)
            
            # Send final completion message to Slack
            completion_msg = f":tada: **Project {project_id} Complete!**\n\n"
            
            if github_info:
                completion_msg += f":octocat: GitHub: {github_info.get('url', 'N/A')}\n"
            if dockerhub_info:
                completion_msg += f":whale: Docker Hub: {dockerhub_info.get('url', 'N/A')}\n"
            if project_dir:
                completion_msg += f":file_folder: Local: {project_dir}\n"
            
            completion_msg += f"\n:sparkles: All deliverables are ready!"
            
            await self._send_slack_update(completion_msg)
            
            return {
                'project_id': project_id,
                'status': 'completed',
                'github': github_info,
                'dockerhub': dockerhub_info,
                'local_path': str(project_dir) if project_dir else None,
            }
        
        except Exception as e:
            logger.error(f"Error handling project: {e}")
            if self.llm_monitor:
                await self.llm_monitor.stop_monitoring(project_id)
            raise
    
    def _needs_clarification(self, description):
        """
        BUGFIX #1: Completely disabled clarification questions
        
        This method now ALWAYS returns False to prevent the endless loop.
        The original logic was causing repeated clarification requests.
        """
        # Always return False - no clarifications needed
        logger.info("Clarification check: DISABLED (always returns False)")
        return False
    
    async def _broadcast_to_dashboard(self, event_type, data):
        """
        BUGFIX #2: Broadcast events to dashboard via WebSocket
        
        This enables real-time chat updates in the web interface.
        """
        try:
            # Try to connect if not connected or if the connection is closed
            if not self.ws_connection or self.ws_connection.closed:
                try:
                    # Use a context manager for connection to ensure it's closed properly in case of error,
                    # but since we want to keep it open, we use the raw connect.
                    self.ws_connection = await asyncio.wait_for(
                        websockets.connect(self.ws_url),
                        timeout=2.0
                    )
                    logger.info(f"Connected to dashboard WebSocket: {self.ws_url}")
                except Exception as e:
                    logger.warning(f"Could not connect to dashboard at {self.ws_url}: {e}")
                    return
            
            # Prepare message
            message = {
                'type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            # Check again if connection is still valid before sending
            if self.ws_connection and not self.ws_connection.closed:
                # Send to dashboard
                await self.ws_connection.send(json.dumps(message))
                logger.debug(f"Broadcast to dashboard: {event_type}")
            else:
                logger.warning("WebSocket connection lost, cannot broadcast.")
                self.ws_connection = None
            
        except Exception as e:
            logger.warning(f"Error broadcasting to dashboard: {e}")
            # Reset connection on error
            self.ws_connection = None
    
    async def _send_slack_update(self, message):
        """
        Send status update to Slack channel
        
        BUGFIX #3: Send progress updates to Slack during project execution
        """
        if not self.slack_client or not self.current_channel:
            logger.debug("Slack client or channel not available for updates")
            return
        
        try:
            await self.slack_client.chat_postMessage(
                channel=self.current_channel,
                text=message
            )
            logger.debug(f"Slack update sent: {message[:50]}...")
        except Exception as e:
            logger.warning(f"Error sending Slack update: {e}")
    
    async def _run_group_chat(self, initial_message, project_id):
        """
        Run the group chat with free communication
        
        BUGFIX #2: Now broadcasts all chat messages to the dashboard
        """
        logger.info(f"Starting group chat for project {project_id}")
        
        # Broadcast project start
        await self._broadcast_to_dashboard('project_start', {
            'project_id': project_id,
            'message': initial_message
        })
        
        # Send Slack update: Team is working
        await self._send_slack_update(
            f":construction_worker: **Team is working on {project_id}**\n"
            f"The agents are collaborating on your request..."
        )
        
        # Start chat
        await self.aria.a_initiate_chat(
            self.manager,
            message=initial_message,
        )
        
        # Get all messages
        messages = self.group_chat.messages
        
        # Send periodic Slack updates
        message_count = len(messages)
        if message_count > 0:
            await self._send_slack_update(
                f":speech_balloon: **Progress Update**\n"
                f"Team has exchanged {message_count} messages so far...\n"
                f"Working on: Architecture, Implementation, Testing, Documentation"
            )
        
        # Broadcast each message to dashboard
        for i, message in enumerate(messages):
            agent_name = message.get('name', 'Unknown')
            content = message.get('content', '')
            
            await self._broadcast_to_dashboard('chat_message', {
                'project_id': project_id,
                'message_number': i + 1,
                'total_messages': len(messages),
                'agent': agent_name,
                'content': content
            })
            
            # Small delay to avoid overwhelming the dashboard
            await asyncio.sleep(0.1)
        
        # Broadcast project end
        await self._broadcast_to_dashboard('project_end', {
            'project_id': project_id,
            'total_messages': len(messages)
        })
        
        # Send final Slack update
        await self._send_slack_update(
            f":white_check_mark: **Team Discussion Complete!**\n"
            f"Total messages: {message_count}\n"
            f"Now processing deliverables..."
        )
        
        logger.info(f"Group chat completed with {len(messages)} messages")
        logger.info(f"All messages broadcasted to dashboard")
        
        return messages
    
    async def _extract_and_save_code(self, messages, project_id):
        """Extract code from messages and save to files"""
        if not CODE_GEN_AVAILABLE:
            logger.warning("Code file generator not available")
            return None
        
        project_dir = Path(f"/opt/aria-system/projects/{project_id}")
        project_dir.mkdir(parents=True, exist_ok=True)
        
        code_gen = CodeFileGenerator()
        
        # Extract all code blocks from messages
        for message in messages:
            content = message.get('content', '')
            code_gen.extract_and_save(content, project_dir)
        
        logger.info(f"Code saved to: {project_dir}")
        
        return project_dir


# Main entry point
if __name__ == "__main__":
    aria = AriaCEO()
    logger.info("Aria CEO v6.3 (Memory Edition) ready!")
