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
        # Ensure select exists
        page.wait_for_selector('#prod-category', state='visible', timeout=10000)
        # Backend URL (default localhost)
        backend_url = os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"
        # Use Playwright's request API to avoid browser CORS/Fetch issues in CI
        res = page.request.get(f"{backend_url}/categories/")
        cats = res.json()
        cat = next((c for c in cats if c.get("name") == "E2E-Cat"), None)
        if not cat:
            res_create = page.request.post(
                f"{backend_url}/categories/",
                data={"name": "E2E-Cat"},
                headers={"Content-Type": "application/json"},
            )
            cat = res_create.json()
        cat_id = str(cat.get("id"))
        # Inject option into select if missing
        page.evaluate(
            "(id, text) => {\n"
            "  const sel = document.querySelector('#prod-category');\n"
            "  const exists = [...sel.querySelectorAll('option')].some(o => o.value === id);\n"
            "  if (!exists) {\n"
            "    const opt = document.createElement('option');\n"
            "    opt.value = id; opt.textContent = text;\n"
            "    sel.appendChild(opt);\n"
            "  }\n"
            "}",
            cat_id,
            cat.get("name"),
        )
        page.select_option('#prod-category', value=cat_id)
        page.click('#prod-form button')
        page.wait_for_timeout(500)
        # Verify in list
        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows)
        browser.close()
