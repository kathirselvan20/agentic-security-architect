# scripts/fix_categories.py
import json, os, re
SRC = "nist-data/nist_csf_clean_ready.json"
DST = "nist-data/nist_csf_clean_fixed.json"

# authoritative mapping for missing prefixes -> category name
PREFIX_TO_CATEGORY = {
    "GV.RR": "Roles, Responsibilities, and Authorities",
    "GV.OV": "Oversight",
    "GV.SC": "Cybersecurity Supply Chain Risk Management",
    "PR.AA": "Identity Management, Authentication, and Access Control",
    "PR.PS": "Platform Security",
    "PR.IR": "Technology Infrastructure Resilience",
    "RS.MA": "Incident Management"
}

def prefix_of(code):
    # code like "PR.AA-01" -> "PR.AA"
    if not code or "." not in code:
        return code
    sec = code.split(".")[1].split("-")[0]
    return code.split(".")[0] + "." + sec

with open(SRC, "r", encoding="utf-8") as f:
    docs = json.load(f)

fixed = []
missing_before = []
for d in docs:
    cat = d.get("category")
    # normalize if string "None"
    if isinstance(cat, str) and cat.strip().lower() == "none":
        cat = None
    if cat is None or (isinstance(cat, str) and not cat.strip()):
        # try to infer from code prefix
        code = d.get("subcategory_code","")
        pref = prefix_of(code)
        if pref in PREFIX_TO_CATEGORY:
            d["category"] = PREFIX_TO_CATEGORY[pref]
        else:
            # leave as None for manual inspection
            missing_before.append((d.get("subcategory_code"), d.get("description","")[:160]))
    fixed.append(d)

with open(DST, "w", encoding="utf-8") as f:
    json.dump(fixed, f, indent=2, ensure_ascii=False)

print(f"Processed {len(docs)} docs. {len(missing_before)} items still missing category (check {DST}).")
if missing_before:
    print("Examples of still-missing items (code, desc snippet):")
    for c, s in missing_before[:20]:
        print("-", c, "|", s)
