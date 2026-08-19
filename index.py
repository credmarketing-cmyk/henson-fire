import pandas as pd
import requests
import time
import random


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


def check_google(url):
    try:
        r = requests.get(
            f"https://www.google.com/search?q=site:{url}",
            headers=HEADERS,
            timeout=10
        )
        html = r.text.lower()

        if "unusual traffic" in html or "captcha" in html:
            return "blocked"

        if "did not match any documents" in html:
            return False

        return True

    except:
        return "error"


def check_bing(url):
    try:
        r = requests.get(
            f"https://www.bing.com/search?q=site:{url}",
            headers=HEADERS,
            timeout=10
        )
        html = r.text.lower()

        if "no results found" in html:
            return False

        return True

    except:
        return "error"


def check_indexing(input_file, output_file):
    df = pd.read_csv(input_file)
    url_column = df.columns[0]

    results = []
    total = len(df)

    for i, row in df.iterrows():
        url = str(row[url_column]).strip()

        if not url or url == "nan":
            continue

        print(f"\n[{i+1}/{total}] {url}")

        g = check_google(url)
        b = check_bing(url)

        print(f"Google: {g} | Bing: {b}")

        # decision logic
        if g == True or b == True:
            status = "indexed"
        elif g == False and b == False:
            status = "not_indexed"
        elif g == "blocked":
            status = "blocked"
        else:
            status = "unknown"

        results.append({
            "url": url,
            "google": g,
            "bing": b,
            "final_status": status
        })

        # safer delay
        time.sleep(random.uniform(2, 4))

    pd.DataFrame(results).to_csv(output_file, index=False)

    print("\n✅ DONE →", output_file)


if __name__ == "__main__":
    check_indexing("check.csv", "checked.csv")