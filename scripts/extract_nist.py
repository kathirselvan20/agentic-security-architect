import pymupdf as fitz  # PyMuPDF
import re
import json

# Path to your uploaded file
pdf_path = "NIST.CSWP.29.pdf"

# Open the PDF
doc = fitz.open(pdf_path)

# Regex patterns
function_pattern = re.compile(r"^(Identify|Protect|Detect|Respond|Recover)\b", re.IGNORECASE)
category_pattern = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\s")  # e.g., ID.AM
subcategory_pattern = re.compile(r"\b([A-Z]{2}\.[A-Z]{2}-\d{2})\b")  # e.g., ID.AM-01

# Storage
nist_data = []
current_function = None
current_category = None

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text("text")
    lines = text.split("\n")
    
    for i, line in enumerate(lines):
        # Detect function heading
        if function_pattern.match(line.strip()):
            current_function = line.strip().split(" ")[0].capitalize()
            continue
        
        # Detect category heading
        if category_pattern.match(line.strip()) and "-" not in line.strip():
            current_category = line.strip()
            continue
        
        # Detect subcategory
        match = subcategory_pattern.search(line)
        if match:
            code = match.group(1).strip()
            
            # Capture description
            description_parts = []
            if len(line) > match.end():
                description_parts.append(line[match.end():].strip())
            
            j = i + 1
            while j < len(lines) and not subcategory_pattern.search(lines[j]) and lines[j].strip():
                description_parts.append(lines[j].strip())
                j += 1
            
            description = " ".join(description_parts)
            
            # Append structured data
            nist_data.append({
                "function": current_function,
                "category": current_category,
                "subcategory_code": code,
                "description": description
            })

# Save JSON
output_file = "nist_csf_structured.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(nist_data, f, indent=2, ensure_ascii=False)

print(f"✅ Extracted {len(nist_data)} structured entries into {output_file}")
