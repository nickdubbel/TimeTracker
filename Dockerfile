# Gebruik een lichte Python-basis
FROM python:3.10-slim

# Werkdirectory
WORKDIR /app

# Kopieer bestanden
COPY . /app

# Installeer vereisten
RUN pip install flask pandas icalendar

# Expose poort 8000
EXPOSE 8000

# Start de applicatie
CMD ["python", "app.py"]
