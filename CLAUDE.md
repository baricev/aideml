# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Install with virtual environment (recommended)
make install

# Development install from source
pip install -e .

# Docker build and run
make docker
```

### Running AIDE
```bash
# Basic usage
aide data_dir="example_tasks/house_prices" goal="Predict sales price" eval="RMSE"

# With custom model and steps
aide agent.code.model="claude-4-sonnet" agent.steps=50 data_dir=... goal=... eval=...

# Using DeepSeek models
export DEEPSEEK_API_KEY="your-api-key"
aide agent.code.model="deepseek-chat" data_dir=... goal=... eval=...

# Web UI
cd aide/webui && streamlit run app.py
```

### Testing
```bash
pytest  # Run tests using pytest
```

### Code Formatting
```bash
black .  # Format code (black is included in requirements.txt)
```

## Architecture Overview

AIDE ML implements a tree-search based ML agent that autonomously writes, debugs, and optimizes machine learning code through iterative improvement.

### Core Components

**Main Entry Points:**
- `aide/run.py` - Main CLI entry point and orchestration
- `aide/agent.py` - Core Agent class implementing the tree search algorithm
- `aide/webui/app.py` - Streamlit web interface

**Key Modules:**
- `aide/interpreter.py` - Code execution and sandbox management
- `aide/journal.py` - Solution tree tracking and node management
- `aide/backend/` - LLM backend abstractions (OpenAI, Anthropic, Gemini, DeepSeek, OpenRouter)
- `aide/utils/` - Configuration, metrics, data preview, visualization utilities

### Tree Search Algorithm
The agent uses an iterative tree search where:
1. Each code solution is a node in the tree
2. LLM generates multiple code variations (children) from each node
3. Code is executed and evaluated using specified metrics
4. Best performing solutions guide further exploration
5. Failed executions create debugging branches

### Configuration System
- Default config: `aide/utils/config.yaml`
- Override via CLI: `aide agent.steps=50 agent.code.model="gpt-4"`
- Key settings:
  - `agent.steps`: Number of improvement iterations (default: 20)
  - `agent.code.model`: LLM for code generation (default: o4-mini)
  - `agent.search.num_drafts`: Drafts per iteration (default: 5)

### Data and Task Structure
- Tasks defined by: data directory + goal description + evaluation metric
- Example tasks in `aide/example_tasks/`
- Agent automatically creates workspace and copies/symlinks data
- Results saved to `logs/<experiment_id>/`

### Backend Support
Multiple LLM backends supported:
- OpenAI (default)
- Anthropic Claude
- Google Gemini  
- DeepSeek (`deepseek-chat`, `deepseek-reasoner`)
- OpenRouter
- Local models via OpenAI-compatible API

Set API keys via environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`).

### Output and Visualization
- Best solution code: `logs/<id>/best_solution.py`
- Solution tree visualization: `logs/<id>/tree_plot.html`
- Real-time progress display during execution
- Journal tracking of all attempts and metrics