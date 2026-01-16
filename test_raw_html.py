import re

# The actual raw HTML from the page
html_north = '''<span class="isim">YAHYA<br/>KÜÇÜKKILIÇ</span><br/><img alt="spades" src="/images/s.gif"/>86<br/><img alt="hearts" src="/images/h.gif"/>QJT643<br/><img alt="diamonds" src="/images/d.gif"/>Q2<br/><img alt="clubs" src="/images/c.gif"/>K63'''

html_south = '''<span class="isim">MEHMET<br/>ALÝKORDÖVAJ</span><br/><img alt="spades" src="/images/s.gif"/>32<br/><img alt="hearts" src="/images/h.gif"/>K52<br/><img alt="diamonds" src="/images/d.gif"/>KT65<br/><img alt="clubs" src="/images/c.gif"/>A7'''

# Pattern to match suit + cards
pattern = r'alt="(spades|hearts|diamonds|clubs)"[^>]*/>([A-KT2-9x]+)'

suit_map = {'spades': 'S', 'hearts': 'H', 'diamonds': 'D', 'clubs': 'C'}

print("Testing North hand:")
matches = re.findall(pattern, html_north)
print(f"Matches: {matches}")
hand = {}
for suit_name, cards in matches:
    hand[suit_map[suit_name]] = cards
print(f"Parsed hand: {hand}")

print("\nTesting South hand:")
matches = re.findall(pattern, html_south)
print(f"Matches: {matches}")
hand = {}
for suit_name, cards in matches:
    hand[suit_map[suit_name]] = cards
print(f"Parsed hand: {hand}")
