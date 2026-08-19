import csv
import requests
from bs4 import BeautifulSoup

INPUT_CSV = "input_links.csv"
OUTPUT_CSV = "matched_links.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def check_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"[FAIL] Status {response.status_code} -> {url}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # --- LOGIC 1: Check main wrapper ---
        wrapper = soup.find("div", class_="review-widget-wrapper")

        # --- LOGIC 2: Check Birdeye script ---
        script = soup.find("script", src=lambda x: x and "birdeye.com/embed" in x)

        # --- LOGIC 3: Check iframe container ID ---
        iframe_div = soup.find("div", id=lambda x: x and "bf-revz-widget" in x)

        # If ANY of these exist → match
        if wrapper or script or iframe_div:
            print(f"[MATCH] Found review widget -> {url}")
            return True
        else:
            print(f"[NO MATCH] -> {url}")
            return False

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return False


def main():
    matched_links = []

    with open(INPUT_CSV, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            url = row[0].strip()
            print(f"Checking: {url}")

            if check_page(url):
                matched_links.append([url])

    # Save output
    with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["URL"])
        writer.writerows(matched_links)

    print("\n✅ Done! Matching links saved to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()