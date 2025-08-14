import json
import re
import uuid

# Load structured JSON
with open("nist_csf_structured.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Expanded category map for both 2-part and 3-part prefixes
CATEGORY_MAP = {
    "ID.AM": "Asset Management",
    "ID.BE": "Business Environment",
    "ID.GV": "Governance",
    "ID.RA": "Risk Assessment",
    "ID.RM": "Risk Management Strategy",
    "ID.IM": "Improvement",
    "PR.AC": "Access Control",
    "PR.AT": "Awareness and Training",
    "PR.DS": "Data Security",
    "PR.IP": "Information Protection Processes and Procedures",
    "PR.MA": "Maintenance",
    "PR.PT": "Protective Technology",
    "DE.AE": "Anomalies and Events",
    "DE.CM": "Security Continuous Monitoring",
    "DE.DP": "Detection Processes",
    "RS.RP": "Response Planning",
    "RS.CO": "Communications",
    "RS.AN": "Analysis",
    "RS.MI": "Mitigation",
    "RS.IM": "Improvements",
    "RC.RP": "Recovery Planning",
    "RC.IM": "Improvements",
    "RC.CO": "Communications",
    "GV.OC": "Organizational Context",
    "GV.RM": "Risk Management",
    "GV.RA": "Risk Assessment",
    "GV.PL": "Planning",
    "GV.PO": "Policy",
    "GV.PR": "Processes"
}

def clean_description(desc: str) -> str:
    """Clean bullets, category prefixes, and whitespace."""
    if not desc:
        return ""
    # Remove leading bullets/colons/dashes
    desc = re.sub(r"^[•\-\s:]+", "", desc)
    # Remove inline bullets like "• Something"
    desc = re.sub(r"•\s*", "", desc)
    # Remove category names in parentheses e.g. "(GV.OC):"
    desc = re.sub(r"\([A-Z]{2}\.[A-Z]{2,3}\):?", "", desc)
    # Collapse spaces
    desc = re.sub(r"\s+", " ", desc)
    return desc.strip()

cleaned_data = []
for entry in data:
    code = entry.get("subcategory_code", "").strip()
    # Try longest prefix match first (3-part)
    prefix_parts = code.split("-")[0]  # before -01
    category_name = CATEGORY_MAP.get(prefix_parts)
    if not category_name:
        # Fallback to first two parts
        two_part_prefix = ".".join(code.split(".")[:2])
        category_name = CATEGORY_MAP.get(two_part_prefix, entry.get("category", None))
    
    cleaned_data.append({
        "_id": str(uuid.uuid4()),  # Unique ID for Azure indexing
        "function": entry.get("function"),
        "category": category_name,
        "subcategory_code": code,
        "description": clean_description(entry.get("description", ""))
    })

# Save cleaned JSON
output_file = "nist_csf_clean_ready.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print(f"✅ Cleaned {len(cleaned_data)} entries, added categories & IDs, saved to {output_file}")
