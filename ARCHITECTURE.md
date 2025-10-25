# Architecture - Aria CEO v6.3 (Optimized Edition)

## 1. Core System Components

| Component | Location | Role |
| :--- | :--- | :--- |
| **Aria CEO (Python App)** | CT150 (192.168.178.150) | GroupChat Orchestrator, Tool Executor, Memory Manager |
| **Data Services** | CT151 (192.168.178.151) | MongoDB (Logs), Redis (Task Queue), PostgreSQL (Project Data) |
| **Dashboard** | CT152 (192.168.178.152) | Real-time Monitoring via WebSocket (Port 8090) |
| **LLM Host 1 (Mac Mini)** | 192.168.178.159 | Hosts Llama 3.1 & 3.2 (Aria, Riley) |
| **LLM Host 2 (GMKtec)** | 192.168.178.155 | Hosts Specialized Coder Models (Sam, Jordan, Alex, Morgan, Taylor) |

## 2. Agent Workflow

The system uses a **GroupChat** pattern managed by the `GroupChatManager` class.

1. **Input:** User sends a request via Slack to `@Aria`.
2. **Orchestration:** Aria (CEO) receives the request and, using its `queue_task` tool, breaks the request down and assigns the first task.
3. **Execution:** Agents discuss the task. When a tool is needed (e.g., `commit_code`, `run_pytest`), the Agent calls the function defined in `tools.py`.
4. **Data Flow:**
    - **Logs/Metrics:** Test results and key events are logged to MongoDB (CT151).
    - **Task Queue:** Tasks are managed via Redis (CT151).
    - **Real-time Monitoring:** All chat messages are broadcasted via WebSocket to the Dashboard (CT152).
5. **Output:** Alex (PM) generates the final `README.md` and the result is returned to the user via Slack.

## 3. Key Features

- **Persistent Memory:** Each agent's conversation history is stored using `diskcache` for context preservation across sessions.
- **Dynamic Configuration:** Agent roles, prompts, and tool assignments are managed externally in `agents_config.yaml`.
- **Hardware Optimization:** LLMs are assigned based on model size and host capacity to maximize throughput (e.g., 32B model to Jordan for complex Frontend).
