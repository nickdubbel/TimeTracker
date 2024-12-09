from flask import Flask, request, jsonify, render_template, send_file, session, after_this_request
from werkzeug.utils import secure_filename
import os
import pandas as pd
from icalendar import Calendar
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'verysecret123768234698579083456'
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
        
        # Reorder the columns
        df = df[['title', 'date', 'start', 'end', 'duration']]

        # Exporteer naar Excel
        export_path = './exports/events.xlsx'
        os.makedirs('./exports', exist_ok=True)
        df.to_excel(export_path, index=False)

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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
