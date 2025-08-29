# agents/lead_architect.py
import os
from openai import AzureOpenAI
from services.search_tool import search_nist_by_function


# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)


DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def lead_architect_agent(function_name: str):
    """Generate a roadmap for ANY NIST CSF function (Identify, Protect, etc.)."""

    # Step 1: Retrieve docs
    search_results = search_nist_by_function(function_name)

    # Step 2: Build prompt
    system_prompt = f"""
You are the Lead Security Architect AI with 7+ years of enterprise experience.
Your task is to turn NIST CSF search results into a prioritized roadmap.

Requirements:
- Cover ALL subcategories within the given function ({function_name}).
- For EACH subcategory: provide
  * Recommendation
  * Priority (High / Medium / Low)
  * Maturity Metric (quantifiable, e.g. "% implemented in 90 days").
- Organize into Immediate (0–90d), Medium (6–12m), Long-term (12m+).
- Speak with authority, precision, and practicality (seasoned architect persona).
- Do not repeat generic NIST definitions; focus on actionable steps.
"""

    user_prompt = f"NIST CSF Function: {function_name}\n\nSubcategories:\n{search_results}"

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content
