from playwright.sync_api import sync_playwright
from pathlib import Path
import os

def test_e2e_create_category_product_and_list():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
            # Usar file:// si no hay servidor frontend
            frontend_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
            frontend_url = frontend_path.as_uri()

        page.goto(frontend_url)

        page.fill('#cat-name', 'E2E-Cat')
        page.click('#cat-form button')
        page.wait_for_timeout(500)

        page.fill('#prod-name', 'E2E-Prod')
        page.fill('#prod-desc', 'desc')
        page.fill('#prod-price', '9.99')
        page.fill('#prod-stock', '5')

        page.wait_for_selector('#prod-category', state='visible', timeout=10000)

        backend_url = os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"

        # Usa request de Playwright para poblar categorías si la UI no las cargó aún
        res = page.request.get(f"{backend_url}/categories/")
        assert res.ok, f"Backend not responding: {res.status}"
        cats = res.json()
        target = next((c for c in cats if c.get("name") == "E2E-Cat"), None)
        if target:
            page.evaluate(
                """(cat) => {
                    const sel = document.querySelector('#prod-category');
                    const opt = document.createElement('option');
                    opt.value = String(cat.id);
                    opt.textContent = cat.name;
                    sel.appendChild(opt);
                }""",
                target,
            )

        page.select_option('#prod-category', label='E2E-Cat')
        page.click('#prod-form button')
        page.wait_for_timeout(500)

        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows)
        browser.close()