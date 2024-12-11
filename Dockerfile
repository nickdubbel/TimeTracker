# Gebruik een lichte Python-basis
FROM python:3.10-slim

# Werkdirectory
WORKDIR /app

# Kopieer alle bestanden
COPY . /app

# Install Gunicorn in addition to other dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Expose poort 8000
EXPOSE 8000

# Start de applicatie met behulp van Flask
# CMD ["python", "app.py"]

# Start the application using Gunicorn (beter voor productie)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
