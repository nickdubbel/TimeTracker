
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import pandas as pd
from icalendar import Calendar
from datetime import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
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
                events.append({'title': title, 'date': start.strftime('%Y-%m-%d'), 'duration': duration})
    
    df = pd.DataFrame(events)
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
        result = process_ical(file_path, event_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(file_path)

print("Applicatie start...")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
