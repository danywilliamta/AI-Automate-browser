def get_prompt_agent(your_scenario, context, step_index):
    return f"""
You are a UI automation agent controlling a web browser.

Scenario description: 
{your_scenario}

Context so far:
{context}

Task for step {step_index}:
1. Decide the next action(s) to perform.
2. Predict the outcome of these actions.
3. Update the state based on predicted results.
4. Indicate if the goals have been achieved.

Output instructions:
- Return strictly JSON with the following keys:
{{"goal": "<current goal description>",
  "done": bool,           # True if goals achieved, else False
  "state": {{ ... }},     # Updated state assertions
  "tool_calls": [         # List of actions to execute
    {{ "function": {{ "name": "<tool_name>", "arguments": "{{...}}" }} }},
    ...
  ],
  "notes": "<optional reasoning or next-step guidance>"
}}

Requirements:
- Only use the provided actions and selectors.
- Include all necessary arguments for each tool call.
- Ensure the JSON is parseable; do not include extra text outside JSON.
"""
