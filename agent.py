import sys
import time
from playwright.sync_api import sync_playwright

URL_FORMULARZA = "https://e-pasazeu.involve.me/internet-swiatlowodowy"

MIASTO = "Warszawa"
ULICA = "Marszałkowska"
NUMER_DOMU = "1"
EMAIL = "test.agent.leads@example.com"
TELEFON = "500600700"

def run_agent():
    print(f"🚀 [START] Uruchamiam agenta dla formularza: {URL_FORMULARZA}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(URL_FORMULARZA, timeout=40000, wait_until="networkidle")
            print("✅ Formularz załadowany pomyślnie.")
            page.wait_for_timeout(2000)

            first_input = page.locator('input[type="text"], textarea').first
            if first_input.is_visible(timeout=5000):
                first_input.fill(f"{MIASTO}, {ULICA} {NUMER_DOMU}")
                print("✅ Wpisano adres.")
            
            next_btn = page.locator('button, div[role="button"]').filter(has_text="Dalej").first
            if next_btn.is_visible(timeout=3000):
                next_btn.click()
            else:
                page.keyboard.press("Enter")
            
            page.wait_for_timeout(2000)

            email_input = page.locator('input[type="email"]').first
            if email_input.is_visible(timeout=3000):
                email_input.fill(EMAIL)
                print("✅ Email uzupełniony.")

            phone_input = page.locator('input[type="tel"]').first
            if phone_input.is_visible(timeout=2000):
                phone_input.fill(TELEFON)
                print("✅ Telefon uzupełniony.")

            checkboxes = page.locator('input[type="checkbox"]')
            for i in range(checkboxes.count()):
                cb = checkboxes.nth(i)
                if cb.is_visible() and not cb.is_checked():
                    cb.check(force=True)

            submit_btn = page.locator('button[type="submit"], button:has-text("Wyślij"), button:has-text("Zobacz"), button:has-text("Sprawdź")').first
            if submit_btn.is_visible(timeout=3000):
                submit_btn.click(force=True)
                print("✅ Kliknięto przycisk wysyłania.")
            else:
                page.keyboard.press("Enter")

            page.wait_for_timeout(4000)
            print("🎉 [SUKCES] Proces ukończony!")

        except Exception as e:
            print(f"\n❌ [BŁĄD AGENTA]: {e}")
            page.screenshot(path="error.png", full_page=True)
            print("📸 Zapisano zrzut ekranu do error.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_agent()
