# Gebruik een lichte Python-basis
FROM python:3.10-slim

# Werkdirectory
WORKDIR /app

# Kopieer requirements.txt en installeer afhankelijkheden
COPY requirements.txt /app/requirements.txt
# Install Gunicorn in addition to other dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn


# Kopieer de rest van de bestanden
COPY . /app

# Expose poort 8000
EXPOSE 8000

# Start de applicatie
# CMD ["python", "app.py"]

# Start the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
