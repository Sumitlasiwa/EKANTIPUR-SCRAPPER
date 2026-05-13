from playwright.sync_api import sync_playwright
import json

def extract_entertainment(page):
    # Navigate to entertainment section
    page.goto("https://ekantipur.com/entertainment", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)  # let lazy content settle

    articles = []

    cards = page.query_selector_all("div.category")
    print(len(cards))
    

    for card in cards[:5]:  # top 5 only
        try:
            title_el = card.query_selector("h2 a")
            title = title_el.text_content().strip() if title_el else None

            # Image — check both src and data-src (lazy loading)
            img_el = card.query_selector("img")
            image_url = None
            if img_el:
                image_url = (
                    img_el.get_attribute("src") or
                    img_el.get_attribute("data-src")
                )
            
            # Category label
            cat_el = page.query_selector("div.category-name a")
            category = cat_el.text_content().strip() if cat_el else None

            # Author — often missing; safe fallback to None
            author_el = card.query_selector("div.author-name p a")
            author = author_el.text_content().strip() if author_el else None

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
    page.goto("https://ekantipur.com/cartoon", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    
    try:
        page.wait_for_selector("section.cartoon-main-wrapper", timeout=10000)

        card = page.query_selector(".cartoon-wrapper")

        # TITLE: prefer cartoon-header h4, fall back to description p
        header_el = card.query_selector(".cartoon-header h4")
        desc_el = card.query_selector(".cartoon-description p")
        raw_desc = desc_el.text_content().strip() if desc_el else ""

        if header_el:
            title = header_el.text_content().strip()
            # Author format: "कार्टुनिस्ट: अविन" → split on ": "
            if ": " in raw_desc:
                author = raw_desc.split(": ", 1)[1].strip() or None
            else:
                author = raw_desc.strip() or None
        else:
            # No header — format: "गजब छ बा! - अविन"
            print("No title so title taken from description !")
            if " - " in raw_desc:
                parts = raw_desc.split(" - ", 1)
                title = parts[0].strip()
                author = parts[1].strip() or None
            else:
                title = raw_desc or None
                author = None

        # IMAGE
        img_el = card.query_selector(".cartoon-image img")
        image_url = (
            img_el.get_attribute("src") or img_el.get_attribute("data-src")
        ) if img_el else None

        return {"title": title, "image_url": image_url, "author": author}

    except Exception as e:
        print(f"Cartoon extraction failed: {e}")
        return {"title": None, "image_url": None, "author": None}

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Set a realistic user agent to avoid bot detection
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
        # Safe access — won't crash if None returned
        if cartoon:
            print(f"  Cartoon title: {cartoon.get('title')}")

        output = {
            "entertainment_news": entertainment,
            "cartoon_of_the_day": cartoon
        }

        # Save JSON — ensure_ascii=False preserves Nepali (Devanagari) script
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("\n✅ Saved to output.json")
        browser.close()

main()
