import re
from bs4 import BeautifulSoup

html_file = "/Users/zentrades/blog/john.html"

with open(html_file, "r") as f:
    html = f.read()

# 1. Extract everything before the grid
grid_start_pattern = r'<div class="all-blogs-grid">\s*'
match = re.search(grid_start_pattern, html)
if not match:
    print("Could not find start of grid")
    exit(1)

top_html = html[:match.start()] + '<div class="all-blogs-grid">\n'

# 2. Extract all cards using BeautifulSoup
# Since the file might not have a closing </div>, we just parse the rest
rest_of_html = html[match.end():]
soup = BeautifulSoup(rest_of_html, "html.parser")
all_cards = soup.find_all("a", class_="card-all")

seen_titles = set()
unique_normal_cards = []

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

for card in all_cards:
    h3 = card.find("h3")
    if not h3:
        continue
    title = h3.text.strip()
    
    if title not in seen_titles:
        seen_titles.add(title)
        
        # We need the HTML of the card
        card_html = str(card)
        
        if title in special_titles:
            idx = special_titles.index(title)
            card_html = re.sub(r'<span>(January \d{2}, 2023|April \d{2}, 2026)</span>', f'<span>{dates_to_apply[idx]}</span>', card_html)
            special_cards_dict[idx] = card_html
        else:
            unique_normal_cards.append(card_html)

grid_html = ""
for i in range(10):
    if i in special_cards_dict:
        grid_html += special_cards_dict[i] + "\n"

for card in unique_normal_cards:
    grid_html += card + "\n"

# 3. Add the end of the file
end_html = """        </div>
        <div class="pagination">
        </div>
    </section>

    <script>
        // Pagination & Filtering Logic
        const itemsPerPage = 6;
        let currentPage = 1;
        let currentCategory = null;
        let currentKeyword = null;

        function getFilteredCards() {
            const allCards = Array.from(document.querySelectorAll('.card-all'));
            return allCards.filter(card => {
                const cat = card.dataset.category || '';
                const kws = (card.dataset.keywords || '').toLowerCase();
                const matchCat = currentCategory ? cat === currentCategory : true;
                const matchKw = currentKeyword ? kws.includes(currentKeyword.toLowerCase()) : true;
                return matchCat && matchKw;
            });
        }

        function showPage(page) {
            const filtered = getFilteredCards();
            const total = filtered.length;
            const pageCount = Math.max(1, Math.ceil(total / itemsPerPage));
            if (page < 1) page = 1;
            if (page > pageCount) page = pageCount;
            currentPage = page;

            document.querySelectorAll('.card-all').forEach(c => c.style.display = 'none');
            const start = (currentPage - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            filtered.slice(start, end).forEach(c => c.style.display = 'flex');
        }

        function makeLink(text, pageNum, disabled = false) {
            const a = document.createElement('a');
            a.href = '#';
            a.innerHTML = text;
            if (disabled) {
                a.classList.add('disabled');
            } else if (pageNum === currentPage) {
                a.classList.add('active');
            }
            a.addEventListener('click', e => {
                e.preventDefault();
                if (!disabled) {
                    applyFilters(pageNum);
                    // scroll smoothly back up to the category bar
                    document.querySelector('.blog-categories')
                        .scrollIntoView({ behavior: 'smooth' });
                }
            });
            return a;
        }

        // 4) Build pagination UI with ellipses
        function setupPagination() {
            const pag = document.querySelector('.pagination');
            if (!pag) return;
            pag.innerHTML = '';
            const total = getFilteredCards().length;
            const pageCount = Math.max(1, Math.ceil(total / itemsPerPage));

            if (pageCount <= 1) {
                pag.style.display = 'none';
                return;
            }
            pag.style.display = 'flex';

            // Prev
            pag.appendChild(makeLink('« Prev', currentPage - 1, currentPage === 1));
            // always show page 1
            pag.appendChild(makeLink('1', 1));

            // left ellipsis?
            if (currentPage > 4) {
                const span = document.createElement('span');
                span.textContent = '…';
                pag.appendChild(span);
            }

            // sliding window around current
            const start = Math.max(2, currentPage - 2);
            const end = Math.min(pageCount - 1, currentPage + 2);
            for (let i = start; i <= end; i++) {
                pag.appendChild(makeLink(i.toString(), i));
            }

            // right ellipsis?
            if (currentPage < pageCount - 3) {
                const span = document.createElement('span');
                span.textContent = '…';
                pag.appendChild(span);
            }

            // always show last page
            if (pageCount > 1) {
                pag.appendChild(makeLink(pageCount.toString(), pageCount));
            }

            // Next
            pag.appendChild(makeLink('Next »', currentPage + 1, currentPage === pageCount));
        }

        // 5) Populate the keyword <select> from all cards' data-keywords
        function populateKeywords() {
            const select = document.getElementById('keyword-select');
            if (!select) return;
            const allKW = new Set();
            document.querySelectorAll('.card-all').forEach(card => {
                (card.dataset.keywords || '')
                    .split(',').map(k => k.trim().toLowerCase()).filter(k => k)
                    .forEach(k => allKW.add(k));
            });
            Array.from(allKW).sort().forEach(kw => {
                const opt = document.createElement('option');
                opt.value = kw;
                opt.textContent = kw.charAt(0).toUpperCase() + kw.slice(1);
                select.appendChild(opt);
            });
        }

        // 6) Render (or clear) the "selected keyword" pill
        function updateKeywordPill() {
            const container = document.getElementById('selected-keyword');
            container.innerHTML = '';
            if (!currentKeyword) return;

            const pill = document.createElement('span');
            pill.className = 'keyword-pill';
            pill.textContent = currentKeyword;

            const btn = document.createElement('button');
            btn.textContent = '×';
            btn.addEventListener('click', () => {
                currentKeyword = null;
                const sel = document.getElementById('keyword-select');
                if (sel) sel.value = '';
                updateKeywordPill();
                applyFilters(1);
            });

            pill.appendChild(btn);
            container.appendChild(pill);
        }

        // 7) Apply filters → show page & rebuild pagination
        function applyFilters(page = 1) {
            showPage(page);
            setupPagination();
        }

        // 8) Initialize everything: wire up handlers & kick off
        function init() {
            // --- Keyword dropdown ---
            const kwSelect = document.getElementById('keyword-select');
            if (kwSelect) {
                kwSelect.addEventListener('change', e => {
                    currentKeyword = e.target.value || null;
                    // clear category
                    currentCategory = null;
                    document.querySelectorAll('.categories button')
                        .forEach(b => b.classList.remove('active'));
                    document.querySelector('.categories button.all')
                        .classList.add('active');
                    document.querySelector('.all-blogs h2').textContent = 'All Blogs';

                    updateKeywordPill();
                    applyFilters(1);
                });
            }

            // --- Category buttons ---
            document.querySelectorAll('.categories button')
                .forEach(btn => {
                    btn.addEventListener('click', () => {
                        // clear keyword
                        currentKeyword = null;
                        const sel = document.getElementById('keyword-select');
                        if (sel) sel.value = '';
                        updateKeywordPill();

                        // standard category logic
                        document.querySelectorAll('.categories button')
                            .forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        currentCategory = btn.classList.contains('all')
                            ? null
                            : btn.dataset.cat;
                        const heading = document.querySelector('.all-blogs h2');
                        if (heading) {
                            heading.textContent = currentCategory
                                ? `${currentCategory} Blogs`
                                : 'All Blogs';
                        }

                        applyFilters(1);
                    });
                });

            populateKeywords();
            applyFilters(1);
        }

        // 9) Kick off on DOM ready
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

final_html = top_html + grid_html + end_html

with open(html_file, "w") as f:
    f.write(final_html)

print("File reconstructed successfully!")
