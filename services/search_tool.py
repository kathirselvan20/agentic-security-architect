# services/search_tool.py
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX", "nist-csf-index")
api_key = os.getenv("AZURE_SEARCH_KEY")

search_client = SearchClient(endpoint=endpoint,
                             index_name=index_name,
                             credential=AzureKeyCredential(api_key))

def search_nist_by_function(function_name: str):
    """
    Retrieve all subcategories for a given NIST CSF function
    (Identify, Protect, Detect, Respond, Recover).
    """
    results = []
    docs = search_client.search(
        search_text=function_name,
        filter=f"section eq '{function_name}'",
        top=50
    )
    for doc in docs:
        results.append({
            "subcategory_code": doc.get("subcategory_code"),
            "title": doc.get("title"),
            "content": doc.get("content")
        })
    return results
