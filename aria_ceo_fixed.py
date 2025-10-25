"""
Aria CEO - Version 6.1 (Bugfix Edition)
Fixed Issues:
- Disabled endless clarification loop
- Added dashboard WebSocket broadcasts

Changes:
1. _needs_clarification() now always returns False
2. _run_group_chat() now broadcasts to dashboard via WebSocket
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

from autogen import AssistantAgent, GroupChat, GroupChatManager

# Import integrations
from integrations.github_integration import GitHubIntegration
from integrations.dockerhub_integration import DockerHubIntegration

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
    Aria - Virtual CEO v6.1
    Bugfix Edition
    """
    
    def __init__(self, slack_client=None):
        self.version = "6.1-bugfix-edition"
        logger.info(f"Initializing Aria CEO - Version {self.version}")
        
        # Slack client for status updates
        self.slack_client = slack_client
        self.current_channel = None
        
        # Load config
        self.config = self._load_config()
        
        # Initialize GitHub integration
        github_config = self.config.get('github', {})
        self.github = GitHubIntegration(github_config)
        
        # Initialize Docker Hub integration
        dockerhub_config = self.config.get('docker_hub', {})
        self.dockerhub = DockerHubIntegration(dockerhub_config)
        
        # Initialize LLM Monitor
        if LLM_MONITOR_AVAILABLE:
            self.llm_monitor = LLMMonitor(self.config.get('llm', {}))
        else:
            self.llm_monitor = None
        
        # WebSocket connection for dashboard broadcasts
        self.ws_url = self.config.get('dashboard', {}).get('websocket_url', 'ws://192.168.178.150:8090/ws')
        self.ws_connection = None
        
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
        logger.info("  ❌ Clarification Questions (DISABLED)")
    
    def _load_config(self):
        """Load configuration"""
        config_path = Path("/opt/aria-system/config/config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
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
    
    def _create_agents(self):
        """Create all team agents with free communication instructions"""
        llm_config = self._get_llm_config()
        
        # Aria (CEO) - Enhanced with free communication support
        self.aria = AssistantAgent(
            name="Aria",
            system_message="""You are Aria, the Virtual CEO. You coordinate the development team.

Your role:
1. Analyze project requirements
2. Break down into tasks
3. **ENCOURAGE FREE COMMUNICATION** between all team members
4. Let workers discuss and collaborate freely
5. Only intervene when necessary
6. Ensure all deliverables are complete

**IMPORTANT: Every project MUST include:**
- Backend code (Sam)
- Tests (Taylor)
- Dockerfile (Morgan)
- docker-compose.yml (Morgan)
- README.md (Alex)
- requirements.txt or package.json (Sam/Jordan)

**FREE COMMUNICATION:**
- Workers can talk to each other directly
- Workers can ask questions to anyone
- Workers can provide feedback to anyone
- You don't need to be in every conversation

When the project is complete, say: "TERMINATE"
""",
            llm_config=llm_config,
        )
        
        # Sam (Backend Developer)
        self.sam = AssistantAgent(
            name="Sam",
            system_message="""You are Sam, a Senior Backend Developer.

Your expertise:
- Python (FastAPI, Django, Flask)
- Node.js (Express)
- Databases (PostgreSQL, MySQL, MongoDB, SQLite)
- REST APIs, GraphQL
- Authentication (JWT, OAuth)

**FREE COMMUNICATION:**
- You can talk to ANYONE directly: "Jordan, ...", "Taylor, ...", etc.
- You can ask questions to ANYONE
- You can provide feedback and tips to ANYONE
- You DON'T need to wait for Aria

**COLLABORATION EXAMPLES:**
- "Jordan, I'm planning these API endpoints: /users, /auth, /data. What do you need for the frontend?"
- "Taylor, can you review my error handling approach?"
- "Morgan, what environment variables should I expose in the Dockerfile?"
- "Riley, what are best practices for API authentication?"

You MUST provide:
1. Complete, working code
2. requirements.txt (Python) or package.json (Node.js)
3. Database models
4. API endpoints
5. Error handling

Format your code as:

# File: backend/main.py
```python
# Your code here
```

ALWAYS include the "# File: path/to/file" header!
""",
            llm_config=llm_config,
        )
        
        # Jordan (Frontend Developer)
        self.jordan = AssistantAgent(
            name="Jordan",
            system_message="""You are Jordan, a Senior Frontend Developer.

Your expertise:
- React, Vue.js, Next.js
- TypeScript, JavaScript
- Responsive Design

**FREE COMMUNICATION:**
- You can talk to ANYONE directly
- Ask Sam about API endpoints BEFORE starting
- Ask Taylor about frontend testing
- Ask Morgan about deployment
- Share UI/UX ideas with the team

**COLLABORATION EXAMPLES:**
- "Sam, what API endpoints will be available? What data format?"
- "Taylor, should I add frontend tests? What framework?"
- "Morgan, any special considerations for the frontend in Docker?"

When frontend is needed, provide complete code with "# File: path/to/file" headers.

If no frontend is needed, say: "No frontend required for this project."
""",
            llm_config=llm_config,
        )
        
        # Taylor (QA Engineer)
        self.taylor = AssistantAgent(
            name="Taylor",
            system_message="""You are Taylor, a Senior QA Engineer.

Your expertise:
- Unit testing (pytest, jest)
- Integration testing
- API testing

**FREE COMMUNICATION:**
- You can talk to ANYONE directly
- Review Sam's code for testability
- Ask Jordan about frontend testing needs
- Coordinate with Morgan on testing in Docker
- Suggest improvements to ANYONE

**COLLABORATION EXAMPLES:**
- "Sam, can you explain the main functions I should test?"
- "Jordan, what user flows should I test in the frontend?"
- "Morgan, should tests run in the Docker build?"
- "I noticed a potential issue in Sam's code..."

You MUST provide comprehensive tests with "# File: tests/test_*.py" headers.
""",
            llm_config=llm_config,
        )
        
        # Morgan (DevOps Engineer)
        self.morgan = AssistantAgent(
            name="Morgan",
            system_message="""You are Morgan, a Senior DevOps Engineer.

Your expertise:
- Docker, docker-compose
- CI/CD
- Cloud deployment

**FREE COMMUNICATION:**
- You can talk to ANYONE directly
- Review code for Docker compatibility
- Ask about environment variables
- Coordinate with Taylor on testing in containers
- Suggest deployment improvements to ANYONE

**COLLABORATION EXAMPLES:**
- "Sam, what environment variables does the app need?"
- "Jordan, does the frontend need any build steps?"
- "Taylor, should I include test execution in the Docker build?"

You MUST provide:
1. Dockerfile (with "# File: Dockerfile" header)
2. docker-compose.yml (with "# File: docker-compose.yml" header)

This is MANDATORY for every project!
""",
            llm_config=llm_config,
        )
        
        # Alex (Project Manager)
        self.alex = AssistantAgent(
            name="Alex",
            system_message="""You are Alex, a Senior Project Manager.

Your expertise:
- Documentation
- Technical writing

**FREE COMMUNICATION:**
- You can talk to ANYONE directly
- Gather information from ALL team members
- Ask clarifying questions to ANYONE
- Request feedback on documentation

**COLLABORATION EXAMPLES:**
- "Sam, what are the main features and how do I run the backend?"
- "Jordan, what frontend features should I document?"
- "Taylor, how do I run the tests?"
- "Morgan, what are the deployment instructions?"

You MUST provide README.md with "# File: README.md" header.

This is MANDATORY for every project!
""",
            llm_config=llm_config,
        )
        
        # Riley (Research Specialist)
        self.riley = AssistantAgent(
            name="Riley",
            system_message="""You are Riley, a Senior Research Specialist.

Your expertise:
- Best practices research
- Technology recommendations
- Architecture patterns
- Security guidelines

**FREE COMMUNICATION:**
- You can talk to ANYONE directly
- Provide recommendations to ANYONE
- Answer technical questions from ANYONE
- Share relevant best practices

**COLLABORATION EXAMPLES:**
- "Sam, for authentication I recommend JWT with refresh tokens. Here's why..."
- "Morgan, for this use case, I suggest using multi-stage Docker builds..."
- "Taylor, here are some edge cases you should test..."

You provide guidance and recommendations, but don't write code.
""",
            llm_config=llm_config,
        )
        
        # Casey (Audio/Video Specialist) - Optional, only if needed
        self.casey = AssistantAgent(
            name="Casey",
            system_message="""You are Casey, an Audio/Video Processing Specialist.

Your expertise:
- Audio processing (speech-to-text, text-to-speech)
- Video processing
- Media streaming
- FFmpeg

**FREE COMMUNICATION:**
- You can talk to ANYONE directly
- Provide media processing guidance
- Help with audio/video features

Only participate when audio/video features are needed.
""",
            llm_config=llm_config,
        )
        
        logger.info("All agents created successfully")
    
    def _create_group_chat(self):
        """Create group chat with free communication"""
        
        # All agents in the team
        agents = [
            self.aria,
            self.sam,
            self.jordan,
            self.taylor,
            self.morgan,
            self.alex,
            self.riley,
            # Casey only joins when needed
        ]
        
        # Free communication: any agent can speak at any time
        self.group_chat = GroupChat(
            agents=agents,
            messages=[],
            max_round=250,  # Increased for complex projects
            speaker_selection_method="auto",  # Let agents decide who speaks next
            allow_repeat_speaker=True,  # Allow multiple messages from same agent
        )
        
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

**IMPORTANT:**
- Talk to each other freely! No need to wait for me.
- Ask questions directly: "Sam, ..." or "Jordan, ..."
- Discuss and collaborate as a real team.
- Every project needs: Backend, Tests, Dockerfile, docker-compose.yml, README.md

**Let's start! Sam and Jordan, please discuss the architecture first.**
"""
        
        # Run group chat
        try:
            result = await self._run_group_chat(initial_message, project_id)
            
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
            # Try to connect if not connected
            if not self.ws_connection:
                try:
                    self.ws_connection = await asyncio.wait_for(
                        websockets.connect(self.ws_url),
                        timeout=2.0
                    )
                    logger.info(f"Connected to dashboard WebSocket: {self.ws_url}")
                except Exception as e:
                    logger.warning(f"Could not connect to dashboard: {e}")
                    return
            
            # Prepare message
            message = {
                'type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            # Send to dashboard
            await self.ws_connection.send(json.dumps(message))
            logger.debug(f"Broadcast to dashboard: {event_type}")
            
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
        
        # Reset messages
        self.group_chat.messages = []
        
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
    logger.info("Aria CEO v6.1 (Bugfix Edition) ready!")

