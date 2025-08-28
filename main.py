import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from agents.lead_architect import lead_architect_agent

if __name__ == "__main__":
    print("=== Lead Architect AI ===")
    while True:
        query = input("\nEnter your query (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break

        response = lead_architect_agent(query)
        print("\n=== Lead Architect Response ===")
        print(response)
