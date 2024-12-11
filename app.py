from flask import Flask, request, jsonify, render_template, send_file, session, after_this_request
from werkzeug.utils import secure_filename
import os
import pandas as pd
from icalendar import Calendar
from datetime import datetime

# google authentication
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from flask import redirect, url_for, session
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timezone, timedelta
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'verysecret123768234698579083456'
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) #to use cloudflare
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def process_ical(file_path, event_word):
    with open(file_path, 'r', encoding='utf-8') as f:
        cal = Calendar.from_ical(f.read())

    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            title = str(component.get('summary'))
            # Controleer of het woord in de titel voorkomt (hoofdletterongevoelig)
            if event_word.lower() in title.lower():
                start = component.get('dtstart').dt
                end = component.get('dtend').dt
                duration = (end - start).total_seconds() / 3600
                # Voeg de datum toe als een geformatteerde string
                events.append({
                    'title': title,
                    'date': start.strftime('%Y-%m-%d'),
                    'start': start.strftime('%H:%M'),
                    'end': end.strftime('%H:%M'),
                    'duration': duration
                })

    return pd.DataFrame(events)
    

def get_summary(file_path, event_word):
    df = process_ical(file_path, event_word)
    if not df.empty:
        # Converteren naar datetime
        df['start'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Maandelijkse samenvatting
        df['month'] = df['start'].dt.to_period('M')
        monthly_summary = df.groupby('month')['duration'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].dt.strftime('%Y-%m')
        
        # Tabel met gedetailleerde gegevens
        detailed_table = df[['title', 'date', 'duration']].to_dict(orient='records')
        
        return {
            "monthly_summary": monthly_summary.to_dict(orient='records'),
            "detailed_table": detailed_table
        }
    return {
        "monthly_summary": [],
        "detailed_table": []
    }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or 'event_name' not in request.form:
        return jsonify({'error': 'Bestand of evenementnaam ontbreekt'}), 400

    file = request.files['file']
    event_name = request.form['event_name']

    if file.filename == '':
        return jsonify({'error': 'Geen bestand geselecteerd'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)

    try:
        # Process iCal file
        df = process_ical(file_path, event_name)
        if df.empty:
            return jsonify({'error': 'Geen evenementen gevonden'}), 400

        # Sla de DataFrame op als JSON in de sessie
        session['dataframe'] = df.to_dict(orient='records')

        # Maak een samenvatting
        summary = get_summary(file_path, event_name)

        # Verwijder het tijdelijke bestand
        os.remove(file_path)

        return jsonify({'summary': summary, 'message': 'Upload successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export', methods=['GET'])
def export_to_excel():
    # Haal de opgeslagen DataFrame op uit de sessie
    dataframe_json = session.get('dataframe')

    if not dataframe_json:
        return jsonify({'error': 'Geen gegevens om te exporteren'}), 400

    try:
        # Zet JSON om naar een DataFrame
        df = pd.DataFrame(dataframe_json)

        if df.empty:
            return jsonify({'error': 'Geen evenementen gevonden om te exporteren'}), 400

        # Reorder columns for the detailed table
        df = df[['title', 'date', 'start', 'end', 'duration']]

        # Bereken de samenvatting per maand
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.to_period('M')
        monthly_summary = df.groupby('month')['duration'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].dt.strftime('%Y-%m')

        # Formatteer de datumkolom terug
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        # Exporteer naar Excel met 2 sheets
        export_path = './exports/events.xlsx'
        os.makedirs('./exports', exist_ok=True)

        with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
            # Sheet 1: Maandelijkse samenvatting
            monthly_summary.to_excel(writer, sheet_name='Samenvatting per maand', index=False)

            # Sheet 2: Gedetailleerde tabel
            df.to_excel(writer, sheet_name='Gedetailleerde afspraken', index=False)

            # Pas de kolombreedtes aan
            workbook = writer.book
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column_cells in worksheet.columns:
                    max_length = 0
                    column_letter = column_cells[0].column_letter  # Get the column letter
                    for cell in column_cells:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    adjusted_width = max_length + 2  # Extra ruimte
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        # Sla het export pad op in de sessie voor latere cleanup
        session['export_path'] = export_path

        # Stuur het bestand voor download
        return send_file(export_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.teardown_request
def cleanup_file(exception=None):
    # Check if the session contains the export file path
    export_path = session.get('export_path')
    if export_path and os.path.exists(export_path):
        try:
            os.remove(export_path)
            print(f"Bestand verwijderd na sessie: {export_path}")
        except Exception as e:
            print(f"Fout bij verwijderen van bestand na sessie: {e}")

@app.route('/authorize')
def authorize():
    flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    if not state:
        return "Geen state in sessie, probeer opnieuw via /authorize", 400

    flow = InstalledAppFlow.from_client_secrets_file(
        'google_credentials.json', SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # Ga terug naar list-events om de eerder opgevraagde evenementen nu op te halen
    return redirect(url_for('list_events'))

def process_google_calendar_events(events):
    filtered_events = []
    for event in events:
        title = event.get('summary', '')
        start_str = event['start'].get('dateTime') or event['start'].get('date')
        end_str = event['end'].get('dateTime') or event['end'].get('date')

        if start_str and end_str:
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds() / 3600
            filtered_events.append({
                'title': title,
                'date': start_dt.strftime('%Y-%m-%d'),
                'start': start_dt.strftime('%H:%M'),
                'end': end_dt.strftime('%H:%M'),
                'duration': duration
            })

    df = pd.DataFrame(filtered_events)
    return df


@app.route('/list-events', methods=['POST', 'GET'])
def list_events():
    if request.method == 'POST':
        event_name = request.form.get('event_name', '')
        session['requested_event_name'] = event_name
    else:
        event_name = session.get('requested_event_name', '')

    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)

    # now = datetime.now(timezone.utc).isoformat()
    # one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    # one_year_ago_iso = one_year_ago.isoformat()
    five_years_ago = datetime.now(timezone.utc) - timedelta(days=5*365)
    five_years_ago_iso = five_years_ago.isoformat()
    events_result = service.events().list(
        calendarId='primary',
        q=event_name, # Filter op zoekwoord
        timeMin=five_years_ago_iso,
        maxResults=1000,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    # Filteren op het ingevoerde zoekwoord
    filtered_events = [e for e in events if event_name.lower() in (e.get('summary', '').lower())]

    # Verwerk naar DataFrame
    df = process_google_calendar_events(filtered_events)

    # Sla de DataFrame op in de sessie, net als bij iCal
    session['dataframe'] = df.to_dict(orient='records')

    # Gebruik dezelfde samenvattingsmethode als bij iCal
    # Stel dat we dezelfde 'get_summary' functie gebruiken, dan moeten we die iets generieker maken
    # omdat get_summary nu een bestandsnaam en event_word verwacht.
    # We kunnen echter de logica van get_summary ook hier direct toepassen:
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.to_period('M')
        monthly_summary = df.groupby('month')['duration'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].dt.strftime('%Y-%m')
        
        # Zet de data om naar dicts zodat we ze in de template kunnen gebruiken
        monthly_summary_records = monthly_summary.to_dict(orient='records')
        detailed_records = df[['title','date','duration']].to_dict(orient='records')
    else:
        monthly_summary_records = []
        detailed_records = []

    return render_template('index.html', 
                           monthly_summary=monthly_summary_records, 
                           detailed_table=detailed_records)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
