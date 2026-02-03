import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

print("Claude CLI ready. Type 'exit' to quit.\n")

while True:
    user = input("You: ")
    if user.lower() in ("exit", "quit"):
        break

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=400,
        messages=[{"role": "user", "content": user}],
    )

    print("Claude:", response.content[0].text, "\n")
