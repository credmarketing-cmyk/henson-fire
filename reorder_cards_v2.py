import re

html_file = "/Users/zentrades/blog/john.html"

with open(html_file, "r") as f:
    html = f.read()

# We need to extract the 10 cards we added at the bottom.
# The 10 titles to search for:
titles = [
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

cards_extracted = []

# Find all cards in the file to make sure we replace the correct ones.
for i, title in enumerate(titles):
    pattern = re.compile(r'(<a href="[^"]+" class="card-all"[^>]*>.*?<h3>' + re.escape(title) + r'</h3>.*?</a>\s*)', re.DOTALL)
    # We want to replace the LAST occurrence (which is the one we added at the end)
    # Or simply search for it, and cut it out by index.
    matches = list(pattern.finditer(html))
    if matches:
        last_match = matches[-1] # The one at the end of the file
        card_html = last_match.group(1)
        
        # Replace the date
        # It currently says "January XX, 2023"
        card_html = re.sub(r'January \d{2}, 2023', dates_to_apply[i], card_html)
        
        cards_extracted.append((last_match.start(), last_match.end(), card_html))
    else:
        print(f"Could not find card: {title}")

# Sort by start index in reverse so we can remove them from the string without messing up indices
cards_extracted.sort(key=lambda x: x[0], reverse=True)

# Remove the cards from html
for start, end, _ in cards_extracted:
    html = html[:start] + html[end:]

# Get the updated cards to insert at the top
cards_to_insert = [c[2] for c in sorted(cards_extracted, key=lambda x: x[0])] # Original order

# Now find the START of the grid
grid_start_pattern = r'<div class="all-blogs-grid">\s*'
match = re.search(grid_start_pattern, html)
if match:
    insert_pos = match.end()
    all_cards_str = "".join(cards_to_insert)
    html = html[:insert_pos] + all_cards_str + html[insert_pos:]
    
    with open(html_file, "w") as f:
        f.write(html)
    print("Successfully moved cards to the top.")
else:
    print("Could not find start of grid.")
