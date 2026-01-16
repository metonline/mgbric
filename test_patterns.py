import re

# The actual raw HTML from the page - notice <br/> between /> and the cards
html_north = '''<img alt="spades" src="/images/s.gif"/>86<br/><img alt="hearts" src="/images/h.gif"/>QJT643<br/><img alt="diamonds" src="/images/d.gif"/>Q2<br/><img alt="clubs" src="/images/c.gif"/>K63'''

# Current pattern - doesn't handle <br/> between /> and cards  
pattern_old = r'alt="(spades|hearts|diamonds|clubs)"[^>]*/>([A-KT2-9x]+)'

# New pattern - allows optional <br/> and whitespace between /> and cards
pattern_new = r'alt="(spades|hearts|diamonds|clubs)"[^>]*/>(?:<br/>)?([A-KT2-9x]+)'

suit_map = {'spades': 'S', 'hearts': 'H', 'diamonds': 'D', 'clubs': 'C'}

print("Old pattern:")
matches = re.findall(pattern_old, html_north)
print(f"  Matches: {matches}")

print("\nNew pattern:")
matches = re.findall(pattern_new, html_north)
print(f"  Matches: {matches}")
hand = {}
for suit_name, cards in matches:
    hand[suit_map[suit_name]] = cards
print(f"  Parsed hand: {hand}")

# Test with both <br/> and no <br/>
test_cases = [
    ('With <br/>', '/>86<br/>'),
    ('Without <br/>', '/>86<img'),
    ('With spaces', '/>\n86<br/>'),
]

pattern_robust = r'alt="(spades|hearts|diamonds|clubs)"[^>]*/>(?:<br/>)?[\s]*([A-KT2-9x]+)'

print("\nRobust pattern tests:")
for name, test in test_cases:
    test_html = f'<img alt="spades" src="/images/s.gif"{test}'
    matches = re.findall(pattern_robust, test_html)
    print(f"  {name}: {matches}")
