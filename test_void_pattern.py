import re

html = '<img alt="hearts" src="/images/h.gif"/>-<br/>'

# Current pattern
pattern1 = r'<img[^>]*alt="hearts"[^>]*/>[\s]*([A2-9TJKQX]+)'

# New pattern with optional dash for void
pattern2 = r'<img[^>]*alt="hearts"[^>]*/>[\s]*([A2-9TJKQX]+-?)'

# Better pattern - match either cards or dash
pattern3 = r'<img[^>]*alt="hearts"[^>]*/>[\s]*((?:[A2-9TJKQX]+|-)?)'

matches1 = re.findall(pattern1, html, re.I)
matches2 = re.findall(pattern2, html, re.I)
matches3 = re.findall(pattern3, html, re.I)

print(f"Pattern 1: {matches1}")
print(f"Pattern 2: {matches2}")
print(f"Pattern 3: {matches3}")

# Best pattern - match the content after /> until <br/>
pattern_best = r'<img[^>]*alt="hearts"[^>]*/>[\s]*([^<]*)'

matches_best = re.findall(pattern_best, html, re.I)
print(f"Pattern best: {matches_best}")
