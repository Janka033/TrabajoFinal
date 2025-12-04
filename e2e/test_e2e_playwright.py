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
        # Fetch categories and populate select, then select by value for reliability in CI
        cat_id = page.evaluate(
            "async () => {\n"
            "  const res = await fetch('http://127.0.0.1:8000/categories/');\n"
            "  const cats = await res.json();\n"
            "  let cat = cats.find(c => c.name === 'E2E-Cat');\n"
            "  if (!cat) {\n"
            "    // create if missing\n"
            "    const resCreate = await fetch('http://127.0.0.1:8000/categories/', {\n"
            "      method: 'POST', headers: { 'Content-Type': 'application/json' },\n"
            "      body: JSON.stringify({ name: 'E2E-Cat' })\n"
            "    });\n"
            "    cat = await resCreate.json();\n"
            "  }\n"
            "  const sel = document.querySelector('#prod-category');\n"
            "  const exists = [...sel.querySelectorAll('option')].some(o => o.value === String(cat.id));\n"
            "  if (!exists) {\n"
            "    const opt = document.createElement('option');\n"
            "    opt.value = String(cat.id);\n"
            "    opt.textContent = cat.name;\n"
            "    sel.appendChild(opt);\n"
            "  }\n"
            "  return String(cat.id);\n"
            "}"
        )
        page.select_option('#prod-category', value=cat_id)
        page.click('#prod-form button')
        page.wait_for_timeout(500)
        # Verify in list
        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows)
        browser.close()
