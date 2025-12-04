from playwright.sync_api import sync_playwright
from pathlib import Path
import os
import time

def _ensure_category(page, backend_url: str, name: str, timeout_sec: int = 30):
    """Create category if missing and return it."""
    # Check existing
    res = page.request.get(f"{backend_url}/categories/")
    assert res.ok, f"Backend not responding: {res.status}"
    cats = res.json()
    target = next((c for c in cats if c.get("name") == name), None)
    if target:
        return target

    # Create
    res = page.request.post(
        f"{backend_url}/categories/",
        data={"name": name},  # o json={"name": name} según tu backend
    )
    # Algunos backends esperan JSON en lugar de form-data:
    if not res.ok:
        res = page.request.post(
            f"{backend_url}/categories/",
            headers={"Content-Type": "application/json"},
            data=f'{{"name": "{name}"}}',
        )
    assert res.ok, f"Failed to create category: {res.status}"
    cat = res.json()

    # Poll until GET sees it
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        res2 = page.request.get(f"{backend_url}/categories/")
        if res2.ok:
            cats2 = res2.json()
            target2 = next((c for c in cats2 if c.get("name") == name), None)
            if target2:
                return target2
        time.sleep(0.5)
    return cat  # fallback; debería tener id y name

def test_e2e_create_category_product_and_list():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
            frontend_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
            frontend_url = frontend_path.as_uri()

        page.goto(frontend_url)

        backend_url = os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"

        # Asegura categoría en backend (evita depender del flujo UI)
        cat = _ensure_category(page, backend_url, "E2E-Cat", timeout_sec=30)

        # Rellena campos de producto
        page.fill('#prod-name', 'E2E-Prod')
        page.fill('#prod-desc', 'desc')
        page.fill('#prod-price', '9.99')
        page.fill('#prod-stock', '5')

        # Asegurar que el select exista
        page.wait_for_selector('#prod-category', state='visible', timeout=10000)

        # Inyectar opción en el select con el id/name del backend
        page.evaluate(
            """(cat) => {
                const sel = document.querySelector('#prod-category');
                const existing = [...sel.options].find(o => o.value === String(cat.id));
                if (!existing) {
                    const opt = document.createElement('option');
                    opt.value = String(cat.id);
                    opt.textContent = cat.name;
                    sel.appendChild(opt);
                }
            }""",
            cat,
        )

        # Seleccionar por value para ser determinista
        page.select_option('#prod-category', value=str(cat["id"]))

        # Enviar producto por UI
        page.click('#prod-form button')
        page.wait_for_timeout(500)

        # Verificar en lista
        rows = page.query_selector_all('#products-body tr')
        assert any('E2E-Prod' in r.inner_text() for r in rows), "Product not found in list"

        browser.close()