# scripts/inspect_index_schema.py
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = "nist-csf-index"  # or whatever your index is called

client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
idx = client.get_index(index_name)
print("Fields in index:")
for field in idx.fields:
    print(f"- {field.name} (type: {field.type}, searchable={field.searchable}, filterable={field.filterable})")
