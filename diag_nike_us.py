from playwright.sync_api import sync_playwright
import time

def diagnose_nike_us():
    url = "https://www.nike.com/w/mens-shoes-nik1zy7ok"
    print(f"Diagnosing {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        found = []
        
        def handle_request(request):
            if "nike.com" in request.url and ("discover" in request.url or "objects" in request.url):
                print(f" FOUND: {request.url[:100]}...")
                found.append(request.url)
        
        page.on("request", handle_request)
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            print("Page loaded. Scrolling...")
            for i in range(10):
                page.mouse.wheel(0, 1000)
                time.sleep(2)
            
            # Try to trigger more by clicking "Show More" if it exists
            try:
                if page.is_visible("button:has-text('Show More')"):
                    page.click("button:has-text('Show More')")
                    time.sleep(5)
            except:
                pass
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
            
    if found:
        print("\nCaptured Requests:")
        for r in set(found):
            print(f" - {r}")
    else:
        print("\nNo requests captured.")

if __name__ == "__main__":
    diagnose_nike_us()
