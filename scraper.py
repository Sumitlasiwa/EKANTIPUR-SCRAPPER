"""
Scrape ekantipur.com listing pages with Playwright (sync API).
Writes combined results to output.json (UTF-8, Nepali script preserved).
"""
from playwright.sync_api import sync_playwright
import json


def extract_entertainment(page):
    """First 5 articles from /entertainment: title, image, section category, author."""
    page.goto("https://ekantipur.com/entertainment", wait_until="domcontentloaded")
    # Images and secondary content often load after first paint
    # page.wait_for_timeout(2000)

    articles = []

    # Each top story is a div.category block (title + blurb + thumb)
    cards = page.locator("div.category").all()
    print(len(cards))

    for card in cards[:5]:
        try:
            title_el = card.locator("h2 a").first
            title = title_el.text_content().strip() if title_el.count() > 0 else None

            # Lazy-loaded thumbs may use data-src until visible
            img_el = card.locator("img")
            image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")

            # Section name (e.g. मनोरञ्जन) lives once in the page chrome, not inside each card
            cat_el = page.locator("div.category-name a").first
            category = cat_el.text_content().strip() if cat_el.count() > 0 else None

            author_el = card.locator("div.author-name p a").first
            author = author_el.text_content().strip() if author_el.count() > 0 else None

            articles.append({
                "title": title,
                "image_url": image_url,
                "category": category,
                "author": author
            })

        except Exception as e:
            print(f"Error parsing card: {e}")
            continue

    return articles


def extract_cartoon(page):
    """Today's cartoon panel: title, image URL, cartoonist name if parseable."""
    page.goto("https://ekantipur.com/cartoon", wait_until="domcontentloaded")

    try:
        # Main strip is injected after initial load
        # page.locator("section.cartoon-main-wrapper").wait_for(timeout=10000)
        card = page.locator("div.cartoon-wrapper").all()[0] # first card

        # TITLE: prefer cartoon-header h4, fall back to description p
        header_el = card.locator("div.cartoon-header h4")
        desc_el = card.locator("div.cartoon-description p").first
        raw_desc = desc_el.text_content().strip()

        if header_el.count() > 0:
            title = header_el.text_content().strip()
            # Author format: "कार्टुनिस्ट: अविन" → split on ": "
            if raw_desc and ": " in raw_desc:
                author = raw_desc.split(": ", 1)[1].strip()
            else:
                author = raw_desc.strip()
        else:
            # No header — format: "गजब छ बा! - अविन"
            print("No title so title taken from description !")
            if raw_desc and " - " in raw_desc:
                parts = raw_desc.split(" - ", 1)
                title = parts[0].strip()
                author = parts[1].strip()
            else:
                title = raw_desc or ""
                author = ""

        # Art next to caption; lazy load may use data-src
        img_el = card.locator("div.cartoon-image img")
        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")

        return {"title": title, "image_url": image_url, "author": author}

    except Exception as e:
        print(f"Cartoon extraction failed: {e}")
        return {"title": "", "image_url": "", "author": ""}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Some CDNs / WAFs treat default Playwright UA as automation
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
        })

        print("Extracting entertainment news...")
        entertainment = extract_entertainment(page)
        print(f"  Found {len(entertainment)} articles")

        print("Extracting cartoon of the day...")
        cartoon = extract_cartoon(page)
        if cartoon:
            print(f"  Cartoon title: {cartoon['title']}")

        output = {
            "entertainment_news": entertainment,
            "cartoon_of_the_day": cartoon
        }

        # json.dumps defaults to ASCII escapes; disable for Devanagari etc.
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("\n✅ Saved to output.json")
        browser.close()

if __name__ == "__main__":
    main()
