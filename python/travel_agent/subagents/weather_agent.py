"""
EXERCICE 3 : Agent météo local (sous-agent du travel_agent)

OBJECTIF : un agent LLM avec un outil qui est une SIMPLE FONCTION PYTHON
(pas de MCP ici). ADK transforme la fonction en outil à partir de son nom,
de ses types et de sa docstring.

API (gratuite, sans clé) : wttr.in
    GET https://wttr.in/Paris?format=j1
    -> JSON dont la clé "current_condition" est une LISTE : on lit son 1er élément.
    Champs utiles dans cet élément : "weatherDesc" (liste de {"value": ...}),
    "temp_C", "temp_F", "humidity", "windspeedKmph"
    L'API demande un en-tête User-Agent de type curl : "curl/7.68.0"
"""
import logging

import httpx
from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)


# TODO 1 (facile) : écris le prompt système.
# Il doit dire à l'agent :
#   - qu'il est spécialisé dans la météo des destinations de voyage
#   - que son seul but est d'utiliser l'outil 'get_weather'
#   - de répondre par des résumés clairs et courts (conditions, températures,
#     prévisions) pour aider à préparer sa valise
SYSTEM_INSTRUCTION = (
    "Tu est un agent specialiser dans la météo des destinations de voyage."
    "Ton seul but est d'utiliser l'outil 'get_weather'."
    "Tu dois repondre avec des resumer clairs et courts ( conditions , température , previsions) pour aider a preparer sa valise."
)


# TODO 2 (facile) : complète la signature de l'outil.
# Indices :
#   - paramètre `location` de type str, valeur par défaut "London"
#   - type de retour : dict
#   - ADK lit la docstring pour décrire l'outil au LLM : écris-la (rôle, Args, Returns)
def get_weather(location:str="London"):
    """
    role: 
        permet de donner la meteo en fonction de la ville
    Args: 
        prend en argument la ville pour la quelle on cherche la meteo
    Returns: 
        retourne un dictionnaire des conditons 
    """
    logger.info(f"--- 🌤️ Tool: get_weather called for {location} ---")
    try:
        # TODO 3 (moyen) : appelle l'API avec httpx.
        # Contraintes : URL avec la location + ?format=j1, en-tête User-Agent,
        # timeout de 8 secondes.
        response = httpx.get(f"https://wttr.in/{location}?format=j1",
                            timeout=8.0 , 
                            headers={"User-Agent":"curl/7.68.0"})

        # TODO 4a (facile) : lève une exception si le code HTTP est une erreur
        # TODO 4b (facile) : convertis la réponse en dictionnaire Python
        response.raise_for_status()
        data = response.json()

        # TODO 5 (difficile) : extrais les champs depuis data["current_condition"][0].
        # Contraintes :
        #   - description : weatherDesc est une liste de dicts, prends la valeur du 1er
        #     ("Unknown" si absente)
        #   - temp_C, temp_F, humidity, windspeedKmph : "N/A" si absents
        #     (indice : dict.get avec une valeur par défaut)

        current = data["current_condition"][0]
        desc = current.get('weatherDesc')[0].get('value':'Unknown') 
        temp_c = current.get("temp_C" , 'N/A')
        temp_f = current.get("temp_F" ,'N/A')
        humidity = current.get('humidity' , 'N/A')
        wind_speed_kmph = current.get('windspeedKmph' , 'N/A')


        # TODO 6 (facile) : construis et renvoie un dict avec les clés :
        #   location, condition, temperature_celsius (ex "18°C"),
        #   temperature_fahrenheit, humidity (ex "55%"), wind_speed_kmph (ex "10 km/h")
        # N'oublie pas le log de succès avant le return.
        result = {"location": location, 
                  "condition": desc , 
                  "temperature_celsius": temp_c, 
                  "temperature_fahrenheit" : temp_f , 
                  "humidity": humidity , 
                  "wind_speed_kmph": wind_speed_kmph}
        return result 

    except Exception as e:
        logger.error(f" erreur de lecture http {e}")
        return {'error': f"erreur dans le https {e}"}
        # TODO 7 (moyen) : en cas d'échec, log un warning et renvoie un dict
        # de secours avec les mêmes clés que le résultat normal.
        # Question de réflexion : est-ce une bonne idée de renvoyer de FAUSSES
        # données plausibles ? Qu'est-ce que le LLM va faire de ce résultat ?
        # Si tu gardes ce choix, ajoute au moins une clé "note" qui le signale.
        


# TODO 8 (moyen) : crée l'agent dans `weather_agent`.
# Indices :
#   - classe LlmAgent, name = "weather_agent"
#   - description : sert aux AUTRES agents à savoir à quoi il sert
#   - tools : liste contenant directement la FONCTION get_weather
#     (la fonction elle-même, sans parenthèses : on ne l'appelle pas)
weather_agent = LlmAgent(
    name="weather_agent",
    description="donne les condition meteo d'une ville donner",
    model="gemini-3.8-flash",
    instruction=SYSTEM_INSTRUCTION , 
    tools=[get_weather]
)