import os
from openai import AzureOpenAI
from services.search_tool import search_nist

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)

def lead_architect_agent(query: str) -> str:
    """
    Lead Architect agent that:
      1. Queries NIST CSF via Azure Cognitive Search
      2. Summarizes & reasons with Azure OpenAI
    """
    # Step 1: Search NIST CSF
    search_results = search_nist(query)

    # Step 2: Summarize + reason
    system_prompt = (
        "You are the Lead Architect AI. "
        "Use NIST Cybersecurity Framework (CSF) results to provide actionable security strategy, "
        "clear reasoning, and structured recommendations."
    )
    user_prompt = f"Query: {query}\n\nNIST Search Results:\n{search_results}"

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3  # keep it focused
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[Lead Architect Agent Error] {e}"
