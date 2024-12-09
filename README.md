# iCal Urenberekening

Deze applicatie stelt je in staat om iCal-bestanden te uploaden, specifieke afspraken te filteren op basis van een zoekwoord, en berekeningen te maken van de totale uren per maand. 

## Functies
- Upload een iCal-bestand.
- Filter afspraken op basis van een zoekwoord in de titel.
- Bereken totaal aantal gewerkte uren per maand.
- Bekijk gedetailleerde afspraken inclusief titel, datum, en uren.

## Vereisten
- Python 3.10 of hoger
- Pip-pakketten:
  - `Flask`
  - `pandas`
  - `icalendar`
  - `Werkzeug`

## Installatie
1. Clone de repository:
   ```bash
   git clone https://github.com/<jouw-gebruikersnaam>/ical-urenberekening.git
   cd ical-urenberekening
   ```

2. Maak een virtuele omgeving:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Voor Windows: venv\Scripts\activate
   ```

3. Installeer de afhankelijkheden:
   ```bash
   pip install -r requirements.txt
   ```

## Gebruik
1. Start de applicatie:
   ```bash
   python app.py
   ```

2. Open je browser en ga naar [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. Upload een iCal-bestand en voer een zoekwoord in om de afspraken te filteren.

## Projectstructuur
```
ical-urenberekening/
├── app.py               # Hoofdapplicatie
├── templates/
│   └── index.html       # HTML-interface
├── uploads/             # Tijdelijke opslag voor geüploade bestanden
├── requirements.txt     # Vereiste Python-pakketten
├── .gitignore           # Git uitsluitingen
└── README.md            # Projectdocumentatie
```

## Licentie
Dit project wordt verspreid onder de MIT-licentie. Zie `LICENSE` voor meer informatie.

## Contributie
Voel je vrij om pull requests te openen of problemen te melden in de issue-tracker. Feedback en verbeteringen zijn altijd welkom!
