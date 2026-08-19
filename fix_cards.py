import re
from bs4 import BeautifulSoup

html_file = "/Users/zentrades/blog/john.html"

with open(html_file, "r") as f:
    html = f.read()

# Match the entire grid content
grid_pattern = re.compile(r'(<div class="all-blogs-grid">)(.*?)(\n\s*</div>\n\s*<!-- Pagination -->|\n\s*</div>\n\s*<div class="pagination">)', re.DOTALL)
match = grid_pattern.search(html)

if not match:
    # Try another pattern just in case
    grid_pattern = re.compile(r'(<div class="all-blogs-grid">)(.*?)(</div>\s*<section class="pagination"|</div>\s*<div class="pagination"|</div>\s*</section>)', re.DOTALL)
    match = grid_pattern.search(html)

if not match:
    print("Could not find the grid block.")
    exit(1)

grid_content = match.group(2)
soup = BeautifulSoup(grid_content, "html.parser")
cards = soup.find_all("a", class_="card-all")

print(f"Found {len(cards)} cards in the grid.")

unique_cards = []
seen_titles = set()

# The titles of the 10 cards we want to move to the front
special_titles = [
    "False Smoke Alarm: Why It Keeps Going Off and How to Actually Fix a False Alarm?",
    "Portable Smoke Alarms: The Complete Guide to Carbon Monoxide Detectors",
    "What to Do When the Fire Alarm Goes Off? Evacuate Fast, Fix Nuisance Alarms, Stay Compliant",
    "Fire Alarm System Requirements: What Your Building Actually Needs to Meet Code?",
    "NFPA 72 Fire Alarm Monitoring Requirements: What Building Owners Need to Know?",
    "OSHA Fire Alarm Requirements: What Every Employer Needs to Get Right?",
    "How Are Smoke Detectors Wired? Everything You Need to Know About Hardwired Systems",
    "Smoke Detector or Carbon Monoxide Detector: What Every US Homeowner Needs to Know?",
    "Fire Alarm Test Requirements: The Complete US Guide to Staying Compliant",
    "Fire Alarm Inspection: The Complete Guide for Contractors and Business Owners"
]

dates_to_apply = [
    "April 24, 2026",
    "April 23, 2026",
    "April 22, 2026",
    "April 21, 2026",
    "April 20, 2026",
    "April 17, 2026",
    "April 16, 2026",
    "April 15, 2026",
    "April 14, 2026",
    "April 13, 2026"
]

special_cards_dict = {}
normal_cards = []

for card in cards:
    h3 = card.find("h3")
    if not h3:
        continue
    title = h3.text.strip()
    
    if title not in seen_titles:
        seen_titles.add(title)
        
        # Format the card HTML beautifully
        # But we can just use str(card) since it's already well-formatted from the source,
        # wait, BeautifulSoup might have stripped some whitespace. 
        card_html = str(card)
        
        if title in special_titles:
            idx = special_titles.index(title)
            # Make sure date is updated
            # The date is in a span inside .info
            # We can use regex to replace it to be sure
            card_html = re.sub(r'<span>(January \d{2}, 2023|April \d{2}, 2026)</span>', f'<span>{dates_to_apply[idx]}</span>', card_html)
            special_cards_dict[idx] = card_html
        else:
            normal_cards.append(card_html)

print(f"Unique cards found: {len(seen_titles)}")
print(f"Special cards found: {len(special_cards_dict)}")

# Construct the new grid content
new_grid_content = "\n"

# 1. Add the 10 special cards at the beginning, in order
for i in range(10):
    if i in special_cards_dict:
        new_grid_content += special_cards_dict[i] + "\n"
    else:
        print(f"Warning: special card {i} not found!")

# 2. Add the rest of the normal cards
for card_html in normal_cards:
    new_grid_content += card_html + "\n"

# Replace in original HTML
new_html = html[:match.start(2)] + new_grid_content + html[match.end(2):]

with open(html_file, "w") as f:
    f.write(new_html)

print("Restored grid successfully!")
