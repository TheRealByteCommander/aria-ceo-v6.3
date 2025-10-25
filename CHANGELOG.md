# Changelog - Aria CEO v6.3 (Optimized Edition)

## v6.3 - Final Optimized Edition (2025-10-26)

### ✨ New Features & Optimizations

- **LLM Optimization:** Implemented final, hardware-optimized LLM assignments based on model size and host capacity (GMKTec vs. Mac Mini).
- **Persistent Memory:** Added persistent conversation memory for all agents using `diskcache`.
- **External Configuration:** Extracted all agent prompts and skills to `agents_config.yaml` for easy modification.
- **Specialized Tools:** Implemented new, role-specific tools (`queue_task`, `run_db_migration`, `build_frontend`, etc.).
- **MongoDB Logging:** Replaced Confluence placeholder with a dedicated MongoDB logging tool for local data services.
- **Agent Reduction:** Removed the redundant `Casey` agent to streamline the team to 7 core members.

### 🐛 Bugfixes & Maintenance

- **Infrastructure Sync:** Corrected all hardcoded IP addresses in `config.yaml` and `tools.py` to match the final user-confirmed infrastructure map (CT150, CT151, CT152).
- **Installation Fix:** Resolved file naming inconsistencies (`aria_ceo_fixed.py` -> `aria_ceo.py`) and updated `install_aria_v6.3.sh` to copy all new files (`tools.py`, `memory_manager.py`, `requirements.txt`).
- **Slack Hotfix:** Integrated v6.2 hotfix logic for reliable Slack status updates.
- **Documentation Structure:** Finalized file structure (e.g., `INSTALLATION.md`, `ARCHITECTURE.md`) and updated all documentation to reflect v6.3 features.
