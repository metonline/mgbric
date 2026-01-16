import json
import re

# Read the file
with open('hands_database.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix missing commas between objects
content = re.sub(r'(\n  })\n  ("404562)', r'\1,\n  \2', content)

# Remove duplicate closing braces
content = re.sub(r'(\n  })\n  }', r'\1', content)

# Write back
with open('hands_database.json', 'w', encoding='utf-8') as f:
    f.write(content)

# Validate
with open('hands_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'✓ Fixed! Valid JSON with {len(data)} keys')
