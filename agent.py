import sys
import time
from playwright.sync_api import sync_playwright

# --- KONFIGURACJA TESTU ---
URL = "https://dobierzswiatlowod.netradar.pl/"

# Dane do formularza
MIASTO = "Warszawa"
ULICA = "Gandhi"
NUMER_DOMU = "27"
KOD_POCZTOWY = "02-776"
IMIĘ = "Test"
NAZWISKO = "Agent"
EMAIL = "test.agent.leads@example.com"
TELEFON = "509090444"

def run_agent():
    print(f"🚀 [START] Uruchamiam agenta dla: {URL}")
    
    with sync_playwright() as p:
        # Uruchamiamy przeglądarkę Chromium
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. Wejście na stronę
            page.goto(URL, timeout=40000, wait_until="networkidle")
            print("✅ Strona załadowana pomyślnie.")

            # Akceptacja cookies/RODO (jeśli występuje popup)
            try:
                cookie_btn = page.query_selector('button:has-text("Akceptuję"), button:has-text("Zgoda"), #accept-cookies, .cookie-accept')
                if cookie_btn and cookie_btn.is_visible():
                    cookie_btn.click()
                    print("✅ Zamknięto banner cookies.")
            except Exception:
                pass

            # 2. Krok 1: Wypełnienie adresu / lokalizacji
            print("⏳ Wypełniam dane lokalizacji...")
            
            # Wyszukujemy pola adresu (używamy elastycznych selektorów dopasowanych do nazewnictwa w landing page'ach)
            miasto_input = page.locator('input[name*="city" i], input[name*="miasto" i], input[placeholder*="Miasto" i]').first
            ulica_input = page.locator('input[name*="street" i], input[name*="ulica" i], input[placeholder*="Ulica" i]').first
            nr_input = page.locator('input[name*="house" i], input[name*="numer" i], input[placeholder*="Numer" i]').first
            kod_input = page.locator('input[name*="zip" i], input[name*="kod" i], input[placeholder*="Kod" i]').first

            if miasto_input.is_visible():
                miasto_input.fill(MIASTO)
            if ulica_input.is_visible():
                ulica_input.fill(ULICA)
            if nr_input.is_visible():
                nr_input.fill(NUMER_DOMU)
            if kod_input.is_visible():
                kod_input.fill(KOD_POCZTOWY)

            print("✅ Adres wprowadzony.")

            # Przejście do następnego kroku lub przesłanie
            next_btn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Dalej"), button:has-text("Sprawdź"), button:has-text("Wyszukaj")').first
            next_btn.click()
            page.wait_for_timeout(2000)

            # 3. Krok 2: Wypełnienie danych kontaktowych
            print("⏳ Wypełniam dane kontaktowe...")

            email_input = page.locator('input[type="email"], input[name*="email" i]').first
            phone_input = page.locator('input[type="tel"], input[name*="phone" i], input[name*="telefon" i]').first
            name_input = page.locator('input[name*="name" i], input[name*="imie" i], input[placeholder*="Imię" i]').first

            if email_input.is_visible():
                email_input.fill(EMAIL)
            if phone_input.is_visible():
                phone_input.fill(TELEFON)
            if name_input.is_visible():
                name_input.fill(IMIĘ + " " + NAZWISKO)

            # Zaznaczenie wymaganych zgód/checkboxów RODO (jeśli istnieją)
            checkboxes = page.locator('input[type="checkbox"]')
            count = checkboxes.count()
            for i in range(count):
                cb = checkboxes.nth(i)
                if cb.is_visible() and not cb.is_checked():
                    cb.check(force=True)
            print("✅ Dane kontaktowe i zgody uzupełnione.")

            # 4. Wysyłka formularza
            submit_btn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Wyślij"), button:has-text("Zamów"), button:has-text("Dalej")').first
            submit_btn.click()
            
            print("⏳ Czekam na odpowiedź po wysłaniu formularza...")
            page.wait_for_timeout(4000)

            # 5. Weryfikacja wyniku
            content = page.content().lower()
            success_keywords = ["dziękujemy", "podsumowanie", "sukces", "otrzymaliśmy", "potwierdzenie", "dziękuję", "skontaktujemy"]
            
            is_success = any(keyword in content for keyword in success_keywords)

            if is_success:
                print("🎉 [SUKCES] Formularz na dobierzswiatlowod.netradar.pl został pomyślnie wysłany i przetworzony!")
            else:
                # Jeśli strona nie wyświetliła oczekiwanego słowa kluczowego, zapisujemy zrzut ekranu
                raise Exception("❌ Brak jednoznacznego potwierdzenia sukcesu na stronie końcowej.")

        except Exception as e:
            print(f"\n❌ [BŁĄD AGENTA]: {e}")
            page.screenshot(path="error.png", full_page=True)
            print("📸 Zapisano zrzut ekranu do pliku error.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_agent()
