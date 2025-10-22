
import os
import re
import json
import time

from file_agent import FileAgent
from agent_prompt import get_prompt_agent

from langchain_openai import ChatOpenAI
from mcp_use import MCPClient
from mcp_use.adapters.langchain_adapter import LangChainAdapter

from dotenv import load_dotenv


print('current working directory:', os.getcwd())
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
AGENT_STEP_LIMIT = int(os.getenv("AGENT_STEP_LIMIT", "10"))



def clean_text(text: str) -> str:
    text = re.sub(r"```(json)?\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text

class CustomMCPAgent:
    def __init__(self, client, llm, tools, max_steps) -> None:
        self.client = client
        self.llm = llm
        self.max_steps = max_steps
        self.tools = tools
        self.llm_with_tools = None
        self.session = None
        self.start = None
        self.end = None
        self.scenario = None

    def load_scenario(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    async def initialize(self):
        # Bind LLM with tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        # Create MCP sessions
        await self.client.create_all_sessions()
        # Get the specific session, Playwright in this case
        self.session = self.client.get_session("playwright")
        self.scenario = self.load_scenario("automate-browser/src/your_scenario.txt")
        self.start = time.time()


    async def run(self):
        context = []
        if self.llm_with_tools is None:
            print("⚙️ Initializing agent environment (LLM + tools + session)...")
            await self.initialize()
            print("✅ Agent successfully initialized and ready.\n")

        for step in range(1,self.max_steps+1):
            print(f"\n--- Step {step}/{self.max_steps} ---")
            context.append(f"--- Step {step} ---\n")
            ctx = "\n".join(context)
            prompt = get_prompt_agent(self.scenario, context=ctx, step_index=step) # Generate prompt for the current step if you want to add different context
            result = await self.llm_with_tools.ainvoke(prompt)

            # TOKENS TRACE
            usage = result.usage_metadata if hasattr(result, 'usage_metadata') else None
            if usage:
                print(f"Input tokens: {usage.get('input_tokens', 'N/A')}, Completion tokens: {usage.get('output_tokens', 'N/A')}, Total tokens: {usage.get('total_tokens', 'N/A')}")

            clean_output = clean_text(result.content)
            try:
                parsed_output = json.loads(clean_output)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                raise e

            status_emoji = "✅" if parsed_output.get("done") else "🧭"
            print(
                f"🧠 Step {step}: Goal {parsed_output['goal']} | Note: {parsed_output['notes']} | Status: {status_emoji}"
            )

            if parsed_output.get("done") and not parsed_output.get("tool_calls"):
                print(
                    "🤖 All goals completed successfully. Session terminated gracefully. ✅"
                )
                self.end = time.time()
                duration = self.end - self.start
                self.start, self.end = None, None
                print(f"⏱️ Total execution time: {duration:.2f} seconds")
                parsed_output["execution_time_seconds"] = f"{duration:.2f}"
                del parsed_output["tool_calls"]
                return parsed_output

            # Execute tool calls through Playwright MCP session
            for tool in parsed_output.get("tool_calls", []):
                tool_name = tool["function"]["name"].split(".")[-1]
                tool_args = tool["function"]["arguments"]

                res = await self.session.call_tool(name=tool_name, arguments=tool_args)
                # taking screenshot for each tool call
                await asyncio.sleep(0.5) # wait for the page to stabilize
                await self.session.call_tool(name="browser_take_screenshot", arguments={"filename":f"step{step}_{tool_name}.png", "format":"png", "fullPage":True})

                #Kind of Dirty fix to avoid context size explosion :)
                #I choose to trim context every 10 steps
                if step % 10 == 0:
                    context=context[5:]
                context.append(f"Tool: {tool_name}\nArgs: {tool_args}\nResult: {res.content[0].text}\n")

        return "Maximum steps reached without completing all goals."

async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "playwright": {
                "command": "npx",
                "args": [
                    "@playwright/mcp@latest",
                    "--isolated",
                    "--browser",
                    "chromium",
                    "--caps",
                    "pdf,snapshot",
                    "--output-dir",
                    "./output",
                ],
            }
        }
    }

    client = MCPClient(config=config)
    await client.create_all_sessions()
    llm = ChatOpenAI(model=LLM_MODEL, openai_api_key=OPENAI_KEY, temperature=0)
    adapter = LangChainAdapter()
    tools = await adapter.create_tools(client)

    agent = CustomMCPAgent(llm=llm, client=client, tools=tools, max_steps=AGENT_STEP_LIMIT)
    result = await agent.run()

    FileAgent().save_content(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
