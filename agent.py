name: Codzienny Agent Testowy

on:
  schedule:
    # Uruchamiaj codziennie o 07:00 UTC (8:00/9:00 czasu polskiego)
    - cron: '0 7 * * *'
  workflow_dispatch:

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Pobierz kod
        uses: actions/checkout@v4

      - name: Skonfiguruj Pythona
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Zainstaluj biblioteki i przeglądarkę
        run: |
          pip install playwright
          playwright install --with-deps chromium

      - name: Uruchom agenta
        run: python agent.py

      # --- E-MAIL W PRZYPADKU SUKCESU ---
      - name: Wyślij e-mail o sukcesie
        if: success()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: ${{ secrets.MAIL_SERVER }}
          server_port: 465
          secure: true
          username: ${{ secrets.MAIL_USERNAME }}
          password: ${{ secrets.MAIL_PASSWORD }}
          subject: "✅ [RAPORT] Landing Page dobierzswiatlowod.netradar.pl działa prawidłowo!"
          to: michal@e-pasaz.eu
          from: Agent Testowy <${{ secrets.MAIL_USERNAME }}>
          body: |
            Cześć Michał,

            Twój automatyczny agent właśnie przeszedł cały proces na stronie dobierzswiatlowod.netradar.pl.
            Formularz został pomyślnie wypełniony i przesłany.

            Data testu: ${{ github.event.repository.updated_at }}
            Status: SUKCES (100% sprawności)

            Pozdrawiamy,
            Twój Agent AI na GitHubie

      # --- E-MAIL W PRZYPADKU AWARII/BŁĘDU ---
      - name: Wyślij e-mail o błędzie
        if: failure()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: ${{ secrets.MAIL_SERVER }}
          server_port: 465
          secure: true
          username: ${{ secrets.MAIL_USERNAME }}
          password: ${{ secrets.MAIL_PASSWORD }}
          subject: "🚨 [ALARM] Błąd na stronie dobierzswiatlowod.netradar.pl!"
          to: michal@e-pasaz.eu
          from: Agent Testowy <${{ secrets.MAIL_USERNAME }}>
          body: |
            Cześć Michał,

            Uwaga! Agent wykrył problem podczas próby wypełnienia formularza na stronie dobierzswiatlowod.netradar.pl.
            W załączniku do tej wiadomości znajdziesz zrzut ekranu z momentu wystąpienia błędu.

            Sprawdź czy serwis działa poprawnie!
          attachments: error.png
