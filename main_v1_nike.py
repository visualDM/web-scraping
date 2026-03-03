import pandas as pd
import requests
from playwright.sync_api import sync_playwright
import time

# ==========================================
# STANDARD / REUSABLE SCRAPING FRAMEWORK
# ==========================================

def generic_hunt_api(start_url, api_filter_str, headless=True):
    """
    Standard function to hunt for an API endpoint using Playwright.
    """
    print(f"Step 1: Hunting for API on {start_url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless) 
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        candidates = []

        def handle_request(request):
            if api_filter_str in request.url:
                candidates.append({"url": request.url, "headers": request.headers})

        page.on("request", handle_request)
        
        try:
            page.goto(start_url, wait_until="commit", timeout=60000)
            page.wait_for_timeout(10000) 
            # Basic scrolling to trigger lazy loading
            for _ in range(5):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Browser interaction finished: {e}")
        finally:
            browser.close()
        
        return candidates

def generic_crawl_api(initial_captured, extract_fn, next_url_fn, sleep_time=1):
    """
    Standard loop to crawl a paginated API until finished.
    """
    all_data = []
    current_url = initial_captured["url"]
    headers = initial_captured["headers"]
    page_count = 1
    
    print("Step 2: Starting crawl loop...")
    
    while current_url:
        print(f"  Scraping page {page_count}...")
        try:
            response = requests.get(current_url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ API Request failed on page {page_count}: {e}")
            break

        # Site-specific extraction
        page_items = extract_fn(data)
        all_data.extend(page_items)
        print(f"    Found {len(page_items)} items.")
        
        # Site-specific pagination
        next_path = next_url_fn(data)
        if next_path:
            # Handle relative vs absolute URLs
            if next_path.startswith('/'):
                from urllib.parse import urlparse
                parsed = urlparse(current_url)
                current_url = f"{parsed.scheme}://{parsed.netloc}{next_path}"
            else:
                current_url = next_path
                
            page_count += 1
            time.sleep(sleep_time)
        else:
            current_url = None
            
    return all_data, page_count

# ==========================================
# NIKE-SPECIFIC CONFIGURATION
# ==========================================

def nike_extract_logic(data):
    """How to pull products out of Nike's specific JSON structure."""
    items = []
    product_groupings = data.get('productGroupings', [])
    for group in product_groupings:
        products = group.get('products', [])
        for item in products:
            copy = item.get('copy', {})
            price_data = item.get('prices', {})
            pdp_url_data = item.get('pdpUrl', {})
            color_data = item.get('displayColors', {})
            
            # Identify color
            color_desc = color_data.get('colorDescription', 'N/A')
            simple_color = color_data.get('simpleColor', {}).get('label', '')
            final_color = f"{simple_color} ({color_desc})" if simple_color and color_desc != 'N/A' else color_desc

            # Status logic: Generally if it's on the wall, it's in stock. 
            # We can check if prices are present as a proxy if no explicit flag is found.
            is_in_stock = "In Stock" if price_data.get('currentPrice') else "Out of Stock"

            items.append({
                "Name": copy.get('title', 'Unknown'),
                "Category": copy.get('subTitle', 'Unknown'),
                "Color": final_color,
                "Price": f"₱{price_data.get('currentPrice', 0):,.0f}" if price_data.get('currentPrice') else "N/A",
                "Original": f"₱{price_data.get('initialPrice', 0):,.0f}" if price_data.get('initialPrice') else "N/A",
                "Status": is_in_stock,
                "URL": pdp_url_data.get('url', 'N/A')
            })
    return items

def nike_get_next_url(data):
    """How to find the next page in Nike's specific JSON structure."""
    pages_info = data.get('pages', {})
    return pages_info.get('next')

def run_nike_scraper():
    """Main execution flow for Nike."""
    category_url = "https://www.nike.com/ph/w/mens-shoes-nik1zy7ok"
    # 1. Hunt for the API
    candidates = generic_hunt_api(category_url, "api.nike.com/discover")
    
    if not candidates:
        print("❌ No Nike API candidates found.")
        return
        
    # Prefer the PRODUCTS query
    captured = next((c for c in candidates if "queryType=PRODUCTS" in c["url"]), candidates[0])

    # 2. Scrape everything using the generic crawler
    final_list, pages = generic_crawl_api(
        captured, 
        extract_fn=nike_extract_logic, 
        next_url_fn=nike_get_next_url
    )

    # 3. Save results
    if final_list:
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(final_list).drop_duplicates(subset=['Name', 'URL'])
        output_file = "Nike_PH_Final_Modular.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✨ SUCCESS! Crawled {pages} pages.")
        print(f"✨ Found {len(df)} unique products. Saved to {output_file}")
    else:
        print("⚠️ No products found.")

if __name__ == "__main__":
    run_nike_scraper()