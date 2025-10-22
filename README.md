
# Automate-browser

An autonomous web automation agent powered by **Playwright**, **LangChain**, and **OpenAI**.
This project demonstrates how an LLM can control a real browser, execute actions step-by-step, and verify progress dynamically.

---

## Features

- LLM-driven decision-making (LangChain + OpenAI)
- Browser control via Playwright
- Step-by-step reasoning with tool invocation
- Automatic screenshots after each action
- JSON-based action parsing and reporting

---

## Installation

This project uses [`uv`]
No need for a `requirements.txt` file — everything is managed through `pyproject.toml`.
### install browsers
playwright install
### or with system deps (Debian/Ubuntu)
sudo apt-get update
sudo apt-get install -y python3-apt || true
playwright install --with-deps


### Prerequisites

- Python **3.12+**
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed:
  ```bash
  pip install uv

##
A valid OpenAI API key (add it to your .env file)
npm install @playwright/mcp@latest


## Quick Start

### 1. Clone the repository
git clone https://github.com/danywilliamta/AI-Automate-browser.git
cd automate-browser

### 2. Install dependencies (using uv)
uv sync and source .venv/bin/activate

### 3. Install Playwright browsers
uv run playwright install --with-deps

### 4. Add your OpenAI API key in  .env

### 5. Run the agent
cd AI-Automate-browser
python automate-browser/src/mcp_agent.py