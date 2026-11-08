"""
EXERCICE 4 : Agent de voyage (orchestrateur)

OBJECTIF : un agent LLM qui n'a AUCUN outil métier lui-même, mais qui délègue :
  - les questions de devises -> au currency_agent, REMOTE (A2A, via HTTP)
  - les questions de météo   -> au weather_agent, LOCAL (import Python)
Il peut aussi se lancer seul avec l'interface web ADK.
"""
import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

# TODO 1 (moyen) : importe weather_agent depuis son module, avec un repli.
# Contrainte : essaie d'abord `travel_agent.subagents.weather_agent`
# (cas où on lance depuis le dossier parent), et si ça échoue avec un
# ImportError, essaie `subagents.weather_agent` (cas où on lance depuis le
# dossier de l'agent, ex : dans Docker).
# Indice : bloc try / except ImportError.
# Question : pourquoi ce double chemin est-il nécessaire ?

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()


# TODO 2 (moyen) : écris le prompt système.
# Il doit dire à l'agent :
#   - qu'il est un assistant de voyage (planifier des voyages, recommander des
#     lieux, répondre aux questions de voyage)
#   - de déléguer les questions de taux de change / conversions à l'outil 'currency_agent'
#   - de déléguer les questions de météo / climat / prévisions à l'outil 'weather_agent'
# Attention : les noms entre quotes doivent être EXACTEMENT les `name` des agents.
SYSTEM_INSTRUCTION = (
  "Tu est un assistant de voyage ton bon but est de planifier des voyage, recommender dees lieux."
  "Repond aux question de taux de change en utilisant l'outil 'currency_agent'."
  "Repond aux question de météo en utilisant l'outil 'weather_agent'."
)


# TODO 3 (facile) : lis l'URL de l'agent de devises dans la variable
# d'environnement CURRENCY_AGENT_URL (défaut "http://localhost:8081").
# Enlève le "/" final s'il y en a un (méthode de str : rstrip).
CURRENCY_AGENT_URL = os.getenv("URL" ,"http://localhost:8081" ).rstrip('/')

logger.info("--- 🔗 Connecting to Remote A2A Currency Agent at %s... ---", CURRENCY_AGENT_URL)


# TODO 4 (difficile) : crée la représentation de l'agent distant.
# Indices :
#   - classe RemoteA2aAgent
#   - name = "currency_agent" (c'est ce nom que le LLM voit)
#   - description : à quoi sert cet agent (lu par le LLM pour choisir)
#   - agent_card : l'URL complète de la carte d'identité A2A de l'agent distant
#     = CURRENCY_AGENT_URL + AGENT_CARD_WELL_KNOWN_PATH (constante importée)
# Question : que contient cette carte et qui la sert ? (regarde l'exercice 2)
currency_remote_agent = ...

logger.info("--- 🤖 Creating ADK Travel Agent... ---")


# TODO 5 (moyen) : crée l'agent principal dans `root_agent`.
# Indices :
#   - classe LlmAgent, name = "travel_agent"
#   - description : mentionne ce qu'il sait faire (voyages, météo via l'agent
#     local, devises via l'agent distant)
#   - tools : liste de deux AgentTool, un par agent
#     (AgentTool(agent=...) enveloppe un agent pour que le LLM le voie comme un outil)
# Question : quelle différence avec l'exercice 3, où tools contenait une fonction ?
root_agent = ...


if __name__ == "__main__":
    import uvicorn
    from google.adk.cli.fast_api import get_fast_api_app

    # TODO 6 (moyen) : lance l'interface web ADK.
    # Contraintes :
    #   - PORT lu dans l'environnement, défaut 8082 (os.getenv puis int)
    #   - app = get_fast_api_app(web=True, allow_origins=["*"], agents_dir=...)
    #     où agents_dir est le dossier contenant CE fichier
    #     (indice : os.path.dirname(__file__), avec "." si la chaîne est vide)
    #   - uvicorn.run(app, host="0.0.0.0", port=PORT)
    pass