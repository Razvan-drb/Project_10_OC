from locust import HttpUser, task, between
import random


class GUDLFTUser(HttpUser):
    wait_time = between(1, 3)  # Temps d'attente entre les requêtes

    def on_start(self):
        """Exécuté au début de chaque session utilisateur"""
        self.clubs = [
            {"email": "john@simplylift.co", "name": "Simply Lift"},
            {"email": "admin@irontemple.com", "name": "Iron Temple"},
            {"email": "kate@shelifts.co.uk", "name": "She Lifts"}
        ]
        self.competitions = [
            {"name": "Spring Festival"},
            {"name": "Fall Classic"}
        ]

    @task(3)  # Poids de la tâche (3x plus fréquent)
    def test_homepage(self):
        """Test de la page d'accueil"""
        self.client.get("/")

    @task(2)
    def test_points_page(self):
        """Test du tableau des points"""
        self.client.get("/points")

    @task(1)
    def test_booking_flow(self):
        """Test complet du flux de réservation"""
        # 1. Connexion
        club = random.choice(self.clubs)
        self.client.post("/showSummary", data={"email": club["email"]})

        # 2. Accès page booking
        competition = random.choice(self.competitions)
        self.client.get(f"/book/{competition['name']}/{club['name']}")

        # 3. Réservation (1-3 places)
        places = random.randint(1, 3)
        self.client.post("/purchasePlaces", data={
            "club": club["name"],
            "competition": competition["name"],
            "places": places
        })