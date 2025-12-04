from playwright.sync_api import sync_playwright

# Simple E2E: assumes API running at 127.0.0.1:8000 and frontend opened via file or local server

def test_e2e_create_category_product_and_list():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Open local frontend via simple server, adjust if needed
        page.goto("http://127.0.0.1:5500/frontend/index.html")
        # Create category
        page.fill('#cat-name', 'E2E-Cat')
        page.click('#cat-form button')
        page.wait_for_timeout(500)
        # Create product
        page.fill('#prod-name', 'E2E-Prod')
        page.fill('#prod-desc', 'desc')
        page.fill('#prod-price', '9.99')
        page.fill('#prod-stock', '5')
        # Select last category
        page.select_option('#prod-category', label='E2E-Cat')
        page.click('#prod-form button')
        page.wait_for_timeout(500)
        # Verify in list
        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows)
        browser.close()
