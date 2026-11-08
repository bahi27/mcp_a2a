"""
EXERCICE 1 : Serveur MCP de conversion de devises

OBJECTIF : un serveur MCP qui expose UN outil, `get_exchange_rate`.

API (gratuite, sans clé) : Frankfurter
    GET https://api.frankfurter.dev/v1/latest?from=USD&to=EUR
    -> JSON avec une clé "rates", ex : {"rates": {"EUR": 0.92}, ...}
    Date précise : /v1/2025-01-15?from=USD&to=EUR
"""
import asyncio
import logging
import os

import httpx
from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)


# TODO 1 (facile) : crée l'instance du serveur dans `mcp`.
# Indice : classe FastMCP, elle prend un nom (str).
mcp = FastMCP("myMcpServer")


# TODO 2 (moyen) : transforme cette fonction en OUTIL MCP.
# Indices :
#   - un décorateur sur l'objet `mcp`
#   - la DOCSTRING est lue par le LLM pour décider d'appeler l'outil :
#     écris-la bien (rôle + Args + Returns)
#   - valeurs par défaut : "USD", "EUR", "latest"
#   - ajoute les annotations de type (str) sur les paramètres
@mcp.tool()
def get_exchange_rate(currency_from:str="USD", currency_to:str="EUR", currency_date : str ="latest"):
    """
    use this to get curency exchenge rate 
    Args:
        currency_from: The currency to convert from (e.g., "USD").
        currency_to: The currency to convert to (e.g., "EUR").
        currency_date: The date for the exchange rate or "latest". Defaults to "latest".
    Returns
        A dictionary containing the exchange rate data, or an error message if the request fails.
    """
    logger.info(f"Outil appelé : {currency_from} -> {currency_to}")

    try:
        response = httpx.get(f"https://api.frankfurter.dev/v1/{currency_date}" , 
                            params={"from" : currency_from  , "to": currency_to})

        # TODO 4a (facile) : lève une exception si le code HTTP est 4xx/5xx
        # Indice : méthode de `response` qui commence par raise_
        response.raise_for_status()

        # TODO 4b (moyen) : convertis la réponse en dictionnaire Python
        data = response.json()

        # TODO 4c (moyen) : si "rates" n'est pas dans `data`,
        #   log une erreur et renvoie {"error": "Invalid API response format."}
        if "rates" not in data:
            logger.error(" rates not in data")
            return {"error": "Invalid  API format"}

        # TODO 4d : log un succès et renvoie `data`
        return data 
    except httpx.HTTPError as e:
        # TODO 5a (moyen) : erreurs réseau/HTTP de httpx (httpx.HTTPError)
        #   -> log + renvoie {"error": "..."}
        logger.error(f"[-] Erreur HTTP {e}")
        return {"error": f"erreur http {e}"}
    except ValueError:
        # TODO 5b (moyen) : JSON invalide (ValueError)
        #   -> log + renvoie {"error": "..."}
        logger.error("Invalid JSON")
        return {"error" : "Invalid JSON"}


if __name__ == "__main__":
    # TODO 6 (difficile) : lance le serveur.
    # Contraintes :
    #   - port lu dans la variable d'environnement PORT, défaut 8080 (os.getenv puis int())
    #   - host "0.0.0.0" (obligatoire sur Cloud Run : à toi de trouver pourquoi,
    #     ça touche au réseau)
    #   - transport "http"
    #   - la méthode de FastMCP est asynchrone : cherche `run_async` et `asyncio.run`
    port = int(os.getenv("PORT" ,8080))
    logger.info(f"starting server at {port}")
    asyncio.run(
        mcp.run_async(
            host="0.0.0.0",
            port= port ,
            transport="http"
        )
    )

