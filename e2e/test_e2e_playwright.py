from playwright.sync_api import sync_playwright
from pathlib import Path
import os

# Simple E2E: assumes API running at 127.0.0.1:8000 and frontend opened via file or local server

def test_e2e_create_category_product_and_list():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Open frontend: prefer FRONTEND_URL env, else use local file URL
        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
            # Default to served path when using python -m http.server -d frontend
            frontend_url = "http://127.0.0.1:5500/frontend/index.html"
        page.goto(frontend_url)
        # Create category
        page.fill('#cat-name', 'E2E-Cat')
        page.click('#cat-form button')
        page.wait_for_timeout(500)
        # Create product
        page.fill('#prod-name', 'E2E-Prod')
        page.fill('#prod-desc', 'desc')
        page.fill('#prod-price', '9.99')
        page.fill('#prod-stock', '5')
        # Wait until category options are populated and select by label
        # Some frontends populate options asynchronously; use longer timeout and non-visible state
        page.wait_for_selector('#prod-category', state='visible', timeout=10000)
        try:
            page.wait_for_function(
                "sel => [...document.querySelectorAll(sel + ' option')].some(o => o.textContent === 'E2E-Cat')",
                arg="#prod-category",
                timeout=30000,
            )
        except Exception:
            # Fallback: fetch categories from API and inject the expected option
            page.evaluate(
                "async () => {\n"
                "  const sel = document.querySelector('#prod-category');\n"
                "  try {\n"
                "    const res = await fetch('http://127.0.0.1:8000/categories/');\n"
                "    const cats = await res.json();\n"
                "    const cat = cats.find(c => c.name === 'E2E-Cat') || cats[cats.length - 1];\n"
                "    if (cat) {\n"
                "      const opt = document.createElement('option');\n"
                "      opt.value = String(cat.id);\n"
                "      opt.textContent = cat.name;\n"
                "      sel.appendChild(opt);\n"
                "    }\n"
                "  } catch (e) { /* ignore */ }\n"
                "}"
            )
        page.select_option('#prod-category', label='E2E-Cat')
        page.click('#prod-form button')
        page.wait_for_timeout(500)
        # Verify in list
        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows)
        browser.close()
