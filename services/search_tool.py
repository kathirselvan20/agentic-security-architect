import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Load env vars
endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX", "nist-csf-index")

# Initialize Azure Cognitive Search client
search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(key)
)

def search_nist(query: str, top: int = 5):
    """Search the NIST CSF index and return formatted results."""
    results = search_client.search(query, top=top)

    formatted = []
    for result in results:
        formatted.append(
            f"- {result['id']} | {result.get('section', 'Unknown')} > {result.get('category', 'Unknown')}\n"
            f"  Title: {result.get('title', 'N/A')}\n"
            f"  Snippet: {result.get('content', '')[:200]}..."
        )

    return "\n\n".join(formatted) if formatted else "No results found."
