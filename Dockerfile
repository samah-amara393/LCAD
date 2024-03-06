#  une image de base avec Python et Flask
FROM python:3.10.4-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY . .

# Installation des dépendances
RUN pip install -r requirements.txt

# le port sur lequel votre application Flask s'exécute
EXPOSE 5000

# Démarrage de l'application Flask
CMD ["python", "app.py"]
