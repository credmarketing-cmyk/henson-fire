import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


TARGET_TEXT = "FREE QUOTE! Same-day Water Heater Services Santa Rosa"


def create_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # run fast in background
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)


def process_links(csv_file):
    df = pd.read_csv(csv_file)
    url_column = df.columns[0]

    driver = create_driver()

    yes_links = []
    no_links = []

    total = len(df)

    for index, row in df.iterrows():
        url = str(row[url_column]).strip()

        if not url or url == "nan":
            continue

        print(f"[{index+1}/{total}] Checking: {url}")

        try:
            driver.get(url)

            # wait until page loads
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # get full page text
            page_text = driver.page_source.lower()

            if TARGET_TEXT.lower() in page_text:
                print("❌ NO (text found)")
                no_links.append(url)
            else:
                print("✅ YES (text not found)")
                yes_links.append(url)

        except Exception as e:
            print(f"⚠️ Error: {e}")
            no_links.append(url)  # treat errors as NO (optional)

        time.sleep(1)

    driver.quit()

    # save results
    pd.DataFrame(yes_links, columns=["url"]).to_csv("yes_links.csv", index=False)
    pd.DataFrame(no_links, columns=["url"]).to_csv("no_links.csv", index=False)

    print("\n✅ DONE")
    print(f"YES: {len(yes_links)}")
    print(f"NO: {len(no_links)}")


if __name__ == "__main__":
    process_links("links.csv")