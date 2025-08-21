# scripts/ingest_nist.py
import os, json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType
)

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "nist-csf-index"

if not SEARCH_ENDPOINT or not SEARCH_KEY:
    raise EnvironmentError("Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY")

index_client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))
search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))

def infer_function_from_code(code: str) -> str:
    if not code:
        return "unknown"
    prefix = code.split(".", 1)[0].upper()  # e.g., "GV", "ID", "PR", "DE", "RS", "RC"
    return {
        "GV": "Govern",
        "ID": "Identify",
        "PR": "Protect",
        "DE": "Detect",
        "RS": "Respond",
        "RC": "Recover",
    }.get(prefix, "unknown")

def create_index():
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        # make section searchable so queries like "Identify" return hits
        SearchField(name="section", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
        SimpleField(name="subcategory_code", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        # the text we actually search
        SearchField(name="title", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
    ]
    index = SearchIndex(name=INDEX_NAME, fields=fields)
    try:
        index_client.delete_index(INDEX_NAME)
        print(f"Deleted existing index: {INDEX_NAME}")
    except Exception:
        pass
    index_client.create_index(index)
    print(f"Created new index: {INDEX_NAME}")

def upload_docs():
    with open("nist-data/nist_csf_clean_ready.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    actions = []
    for i, entry in enumerate(data):
        subcat = entry.get("subcategory_code", "")
        section = infer_function_from_code(subcat)  # <-- derive from code, not from entry["function"]
        title = f"{subcat} — {entry.get('category','')}".strip(" —")
        content = entry.get("description", "")

        actions.append({
            "id": entry.get("_id") or str(i),
            "section": section,
            "subcategory_code": subcat,
            "category": entry.get("category", ""),
            "title": title,
            "content": content
        })

    if actions:
        result = search_client.upload_documents(actions)
        ok = getattr(result[0], "succeeded", None) if result else None
        print(f"Uploaded {len(actions)} documents. First result ok? {ok}")
    else:
        print("No documents found to upload.")

if __name__ == "__main__":
    create_index()
    upload_docs()
