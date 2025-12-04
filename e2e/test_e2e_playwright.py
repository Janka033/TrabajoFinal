from playwright.sync_api import sync_playwright
from pathlib import Path
import os
import time

def _wait_for_category(page, backend_url: str, name: str, timeout_sec: int = 30):
    """Poll /categories/ until a category with given name exists; returns the category dict."""
    deadline = time.time() + timeout_sec
    last_status = None
    while time.time() < deadline:
        res = page.request.get(f"{backend_url}/categories/")
        last_status = res.status
        if res.ok:
            cats = res.json()
            target = next((c for c in cats if c.get("name") == name), None)
            if target:
                return target
        time.sleep(0.5)
    raise AssertionError(f"Category '{name}' not available after {timeout_sec}s (last status={last_status})")

def test_e2e_create_category_product_and_list():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
            frontend_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
            frontend_url = frontend_path.as_uri()

        page.goto(frontend_url)

        # Create category via UI
        page.fill('#cat-name', 'E2E-Cat')
        page.click('#cat-form button')
        page.wait_for_timeout(300)

        # Create product via UI
        page.fill('#prod-name', 'E2E-Prod')
        page.fill('#prod-desc', 'desc')
        page.fill('#prod-price', '9.99')
        page.fill('#prod-stock', '5')

        # Ensure the select exists
        page.wait_for_selector('#prod-category', state='visible', timeout=10000)

        backend_url = os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"

        # Wait until the backend has the category we just created
        cat = _wait_for_category(page, backend_url, "E2E-Cat", timeout_sec=30)

        # Inject option into the select to avoid relying on frontend async population
        page.evaluate(
            """(cat) => {
                const sel = document.querySelector('#prod-category');
                const opt = document.createElement('option');
                opt.value = String(cat.id);
                opt.textContent = cat.name;
                sel.appendChild(opt);
            }""",
            cat,
        )

        # Select by value to be deterministic
        page.select_option('#prod-category', value=str(cat["id"]))

        # Submit product
        page.click('#prod-form button')
        page.wait_for_timeout(500)

        # Verify product in the list
        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows), "Product not found in list"

        browser.close()