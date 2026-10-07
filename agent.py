import sys
import time
from playwright.sync_api import sync_playwright

URL = "https://dobierzswiatlowod.netradar.pl/"

MIASTO = "Warszawa"
ULICA = "Marszałkowska"
NUMER_DOMU = "1"
EMAIL = "test.agent.leads@example.com"
TELEFON = "500600700"

def run_agent():
    print(f"🚀 [START] Uruchamiam agenta dla: {URL}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. Ładowanie strony
            page.goto(URL, timeout=40000, wait_until="networkidle")
            print("✅ Strona załadowana pomyślnie.")
            page.wait_for_timeout(2000)

            # 2. Akceptacja Cookies
            try:
                cookie_btn = page.locator('button:has-text("Akceptuję"), button:has-text("Zgoda"), button:has-text("Zaakceptuj"), #accept-cookies').first
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
                    print("✅ Zamknięto banner cookies.")
            except Exception:
                pass

            # 3. Uzupełnianie lokalizacji
            print("⏳ Wypełniam dane lokalizacji...")
            
            # Wpisanie adresu
            inputs = page.locator('input[type="text"], input:not([type])')
            if inputs.count() > 0:
                # Wpisujemy miasto/adres w pierwsze dostępne pole
                inputs.first.fill(f"{MIASTO}, {ULICA} {NUMER_DOMU}")
                page.wait_for_timeout(1500)
                
                # Jeśli po wpisaniu pojawi się lista rozwijana podpowiedzi, klikamy pierwszą
                suggestion = page.locator('.autocomplete-suggestion, .pac-item, li:has-text("' + MIASTO + '")').first
                if suggestion.is_visible(timeout=2000):
                    suggestion.click()
                    print("✅ Wybrano adres z listy podpowiedzi.")

            print("✅ Adres wprowadzony.")

            # 4. Kliknięcie przycisku przejścia
            print("⏳ Szukam przycisku do przejścia dalej...")
            
            # Szukamy dowolnego klikalnego przycisku lub elementu z tekstem
            action_button = page.locator('button, a.btn, input[type="button"], input[type="submit"], div[role="button"]').filter(
                has_text=lambda text: any(w in text.lower() for w in ["sprawdź", "dalej", "wyszukaj", "dobierz", "szukaj", "wyślij"])
            ).first

            if not action_button.is_visible(timeout=5000):
                # Fallback: po prostu bierzemy pierwszy widoczny button na stronie
                action_button = page.locator('button:visible').first

            action_button.click(force=True)
            print("✅ Kliknięto przycisk weryfikacji adresu.")
            
            page.wait_for_timeout(4000)

            # 5. Uzupełnianie danych kontaktowych (jeśli pojawił się krok 2)
            print("⏳ Sprawdzam pola kontaktowe...")
            
            email_field = page.locator('input[type="email"], input[name*="email" i]').first
            phone_field = page.locator('input[type="tel"], input[name*="phone" i], input[name*="telefon" i]').first

            if email_field.is_visible(timeout=5000):
                email_field.fill(EMAIL)
                print("✅ Email wprowadzony.")
            
            if phone_field.is_visible(timeout=2000):
                phone_field.fill(TELEFON)
                print("✅ Telefon wprowadzony.")

            # Zaznaczenie checkboxów zgód
            checkboxes = page.locator('input[type="checkbox"]')
            for i in range(checkboxes.count()):
                cb = checkboxes.nth(i)
                if cb.is_visible() and not cb.is_checked():
                    cb.check(force=True)

            # Finalny przycisk wysyłki
            final_button = page.locator('button[type="submit"], button:has-text("Wyślij"), button:has-text("Pokaż oferty"), button:has-text("Dalej")').first
            if final_button.is_visible(timeout=3000):
                final_button.click(force=True)
                print("✅ Kliknięto finalny przycisk wysłania.")

            page.wait_for_timeout(4000)

            # 6. Weryfikacja sukcesu
            content = page.content().lower()
            if any(w in content for w in ["dziękujemy", "oferty", "sukces", "wyniki", "potwierdzenie"]):
                print("🎉 [SUKCES] Formularz przeszedł pomyślnie!")
            else:
                print("⚠️ Brak słowa kluczowego, ale proces doszedł do końca.")

        except Exception as e:
            print(f"\n❌ [BŁĄD AGENTA]: {e}")
            page.screenshot(path="error.png", full_page=True)
            print("📸 Zapisano zrzut ekranu do error.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_agent()
