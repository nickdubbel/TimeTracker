## iCal & Google Calendar Urenberekening

Deze applicatie stelt je in staat om iCal-bestanden te uploaden of direct met Google Calendar te koppelen, specifieke afspraken te filteren op basis van een zoekwoord, en berekeningen te maken van de totale uren per maand. Dit helpt je om snel inzicht te krijgen in de gewerkte uren, zowel uit lokaal geüploade iCal-bestanden als uit je primaire Google Calendar.

## Functies
- **iCal-upload:** Upload een lokaal iCal-bestand (`.ics`) en filter afspraken op basis van een zoekwoord.
- **Google Calendar-koppeling:** Autoriseer de applicatie met je Google-account en haal evenementen op uit je primaire agenda.
- **Filteren op zoekwoord:** Zoek op een specifiek trefwoord in de titel van de afspraken.
- **Maandelijkse samenvatting:** Bereken automatisch het totaal aantal gewerkte uren per maand.
- **Gedetailleerd overzicht:** Bekijk een lijst met alle gefilterde afspraken inclusief titel, datum en aantal gewerkte uren.
- **Historische data:** Haal tot 5 jaar terug aan evenementen op uit Google Calendar.
- **Export naar Excel:** Download een Excel-bestand met zowel een maandelijkse samenvatting als een gedetailleerd overzicht.

## Vereisten
- Python 3.10 of hoger
- Pip-pakketten (zie `requirements.txt`):
  - `Flask`
  - `pandas`
  - `icalendar`
  - `Werkzeug`
  - `google-auth-oauthlib`
  - `google-api-python-client`
  - `openpyxl`

Je hebt ook een geldig `google_credentials.json` bestand nodig om Google Calendar te gebruiken. Dit bestand kun je genereren via de [Google Cloud Console](https://console.cloud.google.com/) door een OAuth 2.0-client ID aan te maken.

## limitaties
- De applicatie kan maximaal 1000 evenementen per keer ophalen uit Google Calendar.
- De applicatie kan maximaal 5 jaar aan historische evenementen ophalen uit Google Calendar.
- De applicatie kan alleen evenementen ophalen uit de primaire agenda van je Google-account.

## Installatie
1. Clone de repository:
   ```bash
   git clone https://github.com/nickdubbel/TimeTracker.git
   cd TimeTracker
   ```

## Installatie
1. Clone de repository:
   ```bash
   git clone https://github.com/nickdubbel/TimeTracker.git
   cd TimeTracker
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

## Docker Gebruik
### Applicatie bouwen en uitvoeren met Docker
1. **Bouw de Docker-container**:
   ```bash
   docker build -t ical-urenberekening .
   ```

2. **Start de container**:
   ```bash
   docker run -d -p 8000:8000 ical-urenberekening
   ```

3. **Open de applicatie**:
   Ga naar [http://127.0.0.1:8000](http://127.0.0.1:8000) in je browser.


### Docker Compose
Je kunt ook `docker-compose` gebruiken om de applicatie te bouwen en uit te voeren:
1. **Zorg dat Docker en Docker Compose zijn geïnstalleerd.**

2. **Plaats je `google_credentials.json` bestand in de projectmap.**

3. **Bouw en start de applicatie**:
```bash
docker-compose up -d
```
-d zorgt er voor dat de container in de achtergrond draait.

4. **Open de applicatie**:
Ga naar [http://127.0.0.1:8000](http://127.0.0.1:8000) in je browser.

5. **Stop de applicatie**:
```bash
docker-compose down
```



## Projectstructuur
```
TimeTracker/
├── app.py               # Hoofdapplicatie (Flask)
├── templates/
│   └── index.html       # HTML-interface
├── static/
│   ├── script.js        # Client-side JavaScript code
│   └── style.css        # Stylesheet
├── uploads/             # Tijdelijke opslag voor geüploade bestanden
├── exports/             # Opslag voor geëxporteerde Excel-bestanden
├── requirements.txt     # Vereiste Python-pakketten
├── Dockerfile           # Docker configuratie
├── docker-compose.yml   # Optioneel gebruik van docker-compose
├── google_credentials.json # OAuth client secrets voor Google Calendar (niet in repo)
├── .gitignore           # Git uitsluitingen
└── README.md            # Projectdocumentatie
```

## Licentie
Dit project wordt verspreid onder de MIT-licentie. Zie `LICENSE` voor meer informatie.

## Contributie
Voel je vrij om pull requests te openen of problemen te melden in de issue-tracker. Feedback en verbeteringen zijn altijd welkom!

