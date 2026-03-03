# Nike Data Scraper

A Python-based web scraper that collects product data (names, prices, colours, and URLs) from the Nike Philippines storefront using Playwright to capture live API endpoints and `requests` to paginate through them.

---

## Files

| File | Description |
|---|---|
| `main_v1_nike.py` | Main scraper — hunts for Nike's internal API, crawls all pages, and saves results to an Excel file. |
| `diag_nike_us.py` | Diagnostic helper — opens the Nike US page and logs any captured API requests to the console. |

---

## Requirements

- Python 3.9+
- [Playwright](https://playwright.dev/python/) (Chromium)
- `requests`
- `pandas`
- `openpyxl`

### Install dependencies

```bash
pip install playwright requests pandas openpyxl
playwright install chromium
```

---

## Usage

### Run the main scraper

```bash
python main_v1_nike.py
```

Output is saved to `Nike_PH_Final_Modular.xlsx` in the current directory.

### Run the diagnostic tool

```bash
python diag_nike_us.py
```

Prints any captured Nike API request URLs to the console — useful for debugging when the scraper stops finding endpoints.

---

## Notes

- The scraper works by intercepting XHR/fetch requests made by the browser rather than parsing HTML, so it is resilient to layout changes.
- No API keys or authentication tokens are required; the scraper reuses the headers that the browser naturally sends.
- Output files (`.xlsx`, `.csv`, `.json`) and secrets (`.env`, `credentials.json`, etc.) are excluded from version control via `.gitignore`.
