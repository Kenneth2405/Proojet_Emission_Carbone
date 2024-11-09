from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import googlemaps
import openai
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from dotenv import load_dotenv
from googlemaps.exceptions import ApiError
import groq
from groq import Client
import deepl
import json
import os

load_dotenv()

# Configurer la clé API OpenAI globalement
openai.api_key = os.getenv("OPENAI_API_KEY")

class Carbone:
    def __init__(self, ville_depart, ville_arrivee, langue):
        load_dotenv()
        self.depart = ville_depart
        self.arrivee = ville_arrivee
        self.langue = langue
        self.coefficients = {"avion": 260, "train": 3, "voiture": 220, "moto": 190}
        self.gmaps_client = googlemaps.Client(os.getenv("GOOGLE_MAPS_API_KEY"))
        self.groq_client = Client(api_key=os.getenv("GROQ_API_KEY"))
        self.deepl_client = deepl.Translator(os.getenv("DEEPL_API_KEY"))
        self.modes = {
            "avion": "driving",  
            "train": "transit",
            "voiture": "driving",
            "moto": "driving",
        }

    def moyen_disponibles(self):
        input_text = (
            f"List the available means of transportation to get from {self.depart} to {self.arrivee} "
            f"from the following list: {self.modes}. Return the result as a JSON object with a single key "
            "'modes_disponibles'. The value should be an array of the available transportation modes."
        )

        try:
            response = openai.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "user",
                        "content": input_text,
                    },
                ],
            )
            response_content = response.choices[0].message.content.strip()

            # Nettoyer la réponse pour extraire le JSON s'il y a du texte supplémentaire
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("La réponse ne contient pas de JSON valide.")
            
            response_content = response_content[json_start:json_end]

            # Convertir la réponse en dictionnaire Python
            try:
                dico = json.loads(response_content)
                if not isinstance(dico, dict) or 'modes_disponibles' not in dico:
                    raise ValueError("Le JSON ne contient pas la clé 'modes_disponibles'.")
                return dico['modes_disponibles']
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Réponse invalide: {response_content}")
            except ValueError as e:
                raise HTTPException(status_code=500, detail=str(e))

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'appel à l'API: {str(e)}")
    def obtenir_distance(self, mode):
        if mode not in self.modes:
            raise HTTPException(status_code=400, detail=f"Mode de transport non supporté: {mode}")

        try:
            if mode == "avion":
                distance = self.obtenir_distance_avion()
                return distance
            else:
                directions = self.gmaps_client.directions(self.depart, self.arrivee, mode=self.modes[mode])
                if directions:
                    distance = directions[0]['legs'][0]['distance']['value'] / 1000
                    return distance
                else:
                    directions = self.gmaps_client.directions(self.depart, self.arrivee, mode="driving")
                    distance = directions[0]['legs'][0]['distance']['value'] / 1000
                    return distance
        except ApiError as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'appel à Google Maps: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur inattendue: {str(e)}")

    def obtenir_coordonnees(self, ville):
        geolocator = Nominatim(user_agent="Carbone")
        location = geolocator.geocode(ville)
        return (location.latitude, location.longitude)

    def obtenir_distance_avion(self):
        coordonnees_depart = self.obtenir_coordonnees(self.depart)
        coordonnees_arrivee = self.obtenir_coordonnees(self.arrivee)
        distance = geodesic(coordonnees_depart, coordonnees_arrivee).kilometers
        return distance

    def calcul_emission(self):
        moyens_disponibles = self.moyen_disponibles()
        emissions = {}

        for mode in moyens_disponibles:
            google_mode = self.modes.get(mode)
            if google_mode:
                distance = self.obtenir_distance(mode)
                emission = (distance * self.coefficients.get(mode, 0)) / 1000
                emissions[mode] = emission

        meilleur_mode = min(emissions, key=emissions.get)
        meilleur_emission = f"{round(emissions[meilleur_mode], 3)} kgCO2"

        valeurs = {mode: round(emission, 3) for mode, emission in emissions.items()}
        input_text = (
            f"Based on the carbon emissions in kgCO2 for transport {valeurs}. "
            f"Provide explanatory details of these values. The result should be in HTML BODY format."
        )

        response = openai.chat.completions.create(
    model="chatgpt-4o-latest",
    messages=[
        {
            "role": "user",
            "content": input_text,
        },
    ],
)

        details = response.choices[0].message.content
        if self.langue != "EN-US":
            result = self.deepl_client.translate_text(details, target_lang=self.langue)
            details = result.text

        return meilleur_mode, meilleur_emission, valeurs, details

    def generer_recommandation_par_llama(self, emission):
        input_text = (
            f"The carbon footprint from {self.depart} to {self.arrivee} is {emission} kgCO2. "
            f"What do you recommend to reduce the environmental impact of this journey while considering these values? "
            f"The result should be in HTML body format."
        )

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": input_text}
                ],
                model="llama-3.1-70b-versatile",
                
            )
            recommandation = chat_completion.choices[0].message.content

            if self.langue != "EN-US":
                result = self.deepl_client.translate_text(recommandation, target_lang=self.langue)
                recommandation = result.text

            return recommandation
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calling Groq or DeepL: {str(e)}")
