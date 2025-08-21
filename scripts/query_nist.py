# scripts/query_nist.py
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Load environment variables
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "nist-csf-index"

if not SEARCH_ENDPOINT or not SEARCH_KEY:
    raise EnvironmentError("Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY in environment variables.")

# Create search client
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)

# Global caches
functions = []
categories = []

# Load distinct functions + categories
def load_facets():
    global functions, categories

    facets = search_client.search("", facets=["section", "category"], top=0)

    if facets.get_facets():
        if "section" in facets.get_facets():
            functions = [f["value"].lower() for f in facets.get_facets()["section"]]
        if "category" in facets.get_facets():
            categories = [c["value"].lower() for c in facets.get_facets()["category"] if c["value"]]

# Show facet distribution + sample docs
def show_debug_info():
    print("\n=== FACETS: Section distribution ===")
    facets = search_client.search("", facets=["section"], top=0)
    if facets.get_facets() and "section" in facets.get_facets():
        for facet in facets.get_facets()["section"]:
            print(f"- {facet['value']}: {facet['count']}")

    print("\n=== Representative sample from each Function ===\n")
    for func in functions:
        results = search_client.search(
            search_text="",
            filter=f"section eq '{func.capitalize()}'",
            top=1,
            select=["id", "section", "subcategory_code", "category", "title", "content"]
        )
        for r in results:
            print(f"[{func.capitalize()}]")
            print(f"- {r['id']} | {r.get('section', 'Unknown')} > {r.get('category', 'Unknown')}")
            print(f"  Title: {r.get('title','')}")
            snippet = r.get('content', '')
            if snippet and len(snippet) > 100:
                snippet = snippet[:100] + "..."
            print(f"  Snippet: {snippet}\n")

# Search handler
def search_nist(query: str):
    print(f"\n=== Query: {query} ===\n")

    q_norm = query.strip().lower()

    results = None

    if q_norm in functions:
        # Function filter
        filter_expr = f"section eq '{q_norm.capitalize()}'"
        results = search_client.search(
            search_text="",
            filter=filter_expr,
            top=50,
            select=["id", "section", "subcategory_code", "category", "title", "content"]
        )
    elif q_norm in categories:
        # Category filter
        # Note: Category values in index are case-sensitive → must use original form
        matching = [c for c in categories if c == q_norm]
        if matching:
            filter_expr = f"category eq '{matching[0].capitalize()}'"
            results = search_client.search(
                search_text="",
                filter=filter_expr,
                top=50,
                select=["id", "section", "subcategory_code", "category", "title", "content"]
            )
    else:
        # Free-text search
        results = search_client.search(
            search_text=query,
            top=50,
            select=["id", "section", "subcategory_code", "category", "title", "content"]
        )

    found = False
    if results:
        for r in results:
            found = True
            print(f"- {r['id']} | {r.get('section','Unknown')} > {r.get('category','Unknown')}")
            print(f"  Title: {r.get('title','')}")
            snippet = r.get('content','')
            if snippet and len(snippet) > 150:
                snippet = snippet[:150] + "..."
            print(f"  Snippet: {snippet}\n")

    if not found:
        print("⚠️ No results found.")

if __name__ == "__main__":
    load_facets()
    show_debug_info()
    user_query = input("\nEnter your query: ")
    search_nist(user_query)
