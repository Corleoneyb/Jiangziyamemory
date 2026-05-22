# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a personal AI orchestration / knowledge-management system ("封神世界灵台"). It has **no build system, no formal test suite, and no lint configuration**. The codebase consists of:

| Component | Path | How to run |
|-----------|------|------------|
| **Static web pages** (vanilla HTML/CSS/JS) | `index.html`, `gate/`, `hongzun/`, `piyue/` | `python3 -m http.server 8080 --directory /workspace` |
| **闻仲 Flask service** | `wenzhong/wenzhong_service.py` | `cd wenzhong && python3 wenzhong_service.py` (port 7654) |
| **Python utility scripts** | `scripts/*.py` | Standalone; most need hardware (mic, GPIO) or external tokens |

### Running services

- **Static site**: `python3 -m http.server 8080 --directory /workspace` — serves all HTML pages at `http://localhost:8080/`.
- **Wenzhong Flask service**: `cd /workspace/wenzhong && python3 wenzhong_service.py` — listens on `0.0.0.0:7654`. Health check: `GET /wenzhong/health`. Command endpoint: `POST /wenzhong/command` (requires `Authorization: Bearer <auth_token>` from `wenzhong/config.yaml`).

### Caveats

- The `wenzhong/config.yaml` has placeholder API keys/tokens (`sk-xxx`, `ghp_xxx`). The service starts fine with placeholders — health endpoint works, simple commands run locally, but DeepSeek LLM calls and GitHub API writes will fail without real keys.
- The `检查状态` command pattern tries to `cd ~/Jiangziyamemory` which won't exist in cloud VMs. Use `系统状态` to verify the service processes commands.
- Voice scripts (`scripts/voice_*.py`) require macOS audio hardware and `requirements-voice.txt` deps — not runnable in cloud VMs.
- RGB/GPIO scripts require a Raspberry Pi — not runnable in cloud VMs.
- There are **no automated tests** in this repository.
- There is **no linter configuration** (no eslint, flake8, etc.).
- The static pages use GitHub API directly from the browser (CORS-friendly); they work when served from any HTTP origin.

### Dependencies

Python packages needed: `flask`, `pyyaml`, `requests` (for `wenzhong/`). Install with:
```
pip3 install flask pyyaml requests
```
