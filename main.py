# main.py
from agents.lead_architect import lead_architect_agent

print("=== Lead Architect AI ===")
while True:
    query = input("\nEnter a NIST Function (Identify, Protect, Detect, Respond, Recover) or 'exit': ")
    if query.lower() == "exit":
        break

    response = lead_architect_agent(query.capitalize())

    print("\n=== Lead Architect Response ===")
    print(response)
