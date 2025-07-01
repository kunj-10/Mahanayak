## Getting Started with UV

Run the following commands to set up the project using the [UV package manager](https://github.com/astral-sh/uv):

### Install uv package manager
```bash
pip install uv
```

### Install all dependencies (like 'npm install')
```bash
uv sync
```

### Run the content creator agent
```bash
uv run -m app.agents.content_creator
uv run -m app.agents.volunteer_guidelines_agent
```

### Add a new dependency
```bash
uv add langgraph
```
