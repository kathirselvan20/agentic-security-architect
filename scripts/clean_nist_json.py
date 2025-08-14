import json
import re

# Load the structured JSON file
with open("nist_csf_structured.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Mapping from subcategory prefix to category name (fill in as needed)
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
    "RC.CO": "Communications"
}

def clean_description(desc: str) -> str:
    """Remove bullets, extra colons, and whitespace."""
    if not desc:
        return ""
    desc = re.sub(r"^[•\-\s:]+", "", desc)  # remove leading bullets/colons
    desc = re.sub(r"\s+", " ", desc)  # collapse multiple spaces
    return desc.strip()

cleaned_data = []
for entry in data:
    code = entry.get("subcategory_code", "")
    prefix = ".".join(code.split(".")[:2]) if code else ""
    category_name = CATEGORY_MAP.get(prefix, entry.get("category", None))
    
    cleaned_data.append({
        "function": entry.get("function"),
        "category": category_name,
        "subcategory_code": code,
        "description": clean_description(entry.get("description", ""))
    })

# Save cleaned JSON
output_file = "nist_csf_clean.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print(f"✅ Cleaned {len(cleaned_data)} entries and saved to {output_file}")
