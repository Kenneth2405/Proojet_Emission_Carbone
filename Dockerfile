FROM python:3.11.9-slim

WORKDIR /app

COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

EXPOSE 8080

CMD ["uvicorn", "fast:app", "--host", "0.0.0.0", "--port", "8080"]
