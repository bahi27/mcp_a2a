"""
EXERCICE 2 : Agent de devises (ADK) branché sur le serveur MCP, exposé en A2A

OBJECTIF : un agent LLM qui
  - récupère ses outils depuis le serveur MCP de l'exercice 1 (via MCP)
  - est joignable par d'autres agents (via A2A), sur le port 8081 par défaut
"""
import logging
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()


# TODO 1 (facile) : écris le prompt système dans SYSTEM_INSTRUCTION.
# Il doit dire à l'agent :
#   - qu'il est spécialisé dans les conversions de devises
#   - que son seul but est d'utiliser l'outil 'get_exchange_rate'
#   - de refuser poliment tout sujet hors devises
#   - de ne pas utiliser d'outils pour autre chose
SYSTEM_INSTRUCTION =( 
  "tu est un agent assistatn dans la conversions de devises, ton seul"
  "ton seul but est d'utiliser l'outil 'get_exchange_rate'." 
  "refuse mechament tout sujet hors devises"
  "n'utilise pas d'outils pour autre chose."
)

# TODO 2 (moyen) : récupère l'URL du serveur MCP.
# Contraintes :
#   - lue dans la variable d'environnement MCP_SERVER_URL
#   - défaut : "http://localhost:8080/mcp"
#   - si l'URL ne finit pas par "/mcp", ajoute-le (attention à ne pas
#     produire "//mcp" si l'URL finit déjà par "/")
mcp_server_url = os.getenv("MCP_SERVER_URL" ,"http://localhost:8080/mcp")
if not mcp_server_url.endswith("/mcp"):
    mcp_server_url=f"{mcp_server_url.rstrip('/')}/mcp"

logger.info(f"--- 🔧 Loading MCP tools from MCP Server at {mcp_server_url}... ---")
logger.info("--- 🤖 Creating ADK Currency Agent... ---")


# TODO 3 (moyen) : crée l'agent dans `root_agent`.
# Indices :
#   - classe LlmAgent
#   - paramètres : model, name, description, instruction, tools
#   - name = "currency_agent" (le travel_agent s'en servira plus tard)
#   - model : prends celui de ton fichier d'origine
#   - tools est une LISTE contenant un McpToolset
#   - McpToolset prend connection_params=StreamableHTTPConnectionParams(url=...)
root_agent = LlmAgent(
    model="gemini-3.8-flash",
    name="currency_agent" ,
    description="an agent that can help with currency conversion" ,
    instruction=SYSTEM_INSTRUCTION ,
    tools=[McpToolset(connection_params=StreamableHTTPConnectionParams(url=mcp_server_url))])


# --- Partie A2A ---
PORT = int(os.getenv("PORT", 8081))
AGENT_URL = os.getenv("AGENT_URL")  # None en local, défini sur Cloud Run

# TODO 4 (difficile) : détermine protocol, host et port que l'agent
# annoncera dans sa carte d'agent A2A.
# Cas 1 : AGENT_URL est défini (ex: "https://currency-agent-xxx.run.app")
#   -> décompose l'URL avec urlparse et déduis :
#      protocol = le schéma (défaut "https")
#      host     = le nom d'hôte
#      port     = le port de l'URL, ou 443 s'il n'y en a pas
if AGENT_URL:
    parsed =urlparse(AGENT_URL)
    host = parsed.hostname 
    protocol = parsed.scheme or "https"
    port = parsed.port or 443 
# Cas 2 : AGENT_URL n'est pas défini
#   -> protocol = "http", host = "localhost", port = PORT
else:
  protocol = "http"
  host = "localhost"
  port = PORT 

# TODO 5 (moyen) : transforme root_agent en application A2A.
# Indice : la fonction to_a2a importée plus haut prend l'agent
#          + host, port et protocol en arguments nommés.
a2a_app = to_a2a(root_agent,host=host , port=port , protocol= protocol)


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting currency_agent on port {PORT}")
    # TODO 6 (facile) : lance a2a_app avec uvicorn.
    # Contraintes : host "0.0.0.0", port = PORT
    # Question à te poser : pourquoi PORT pour écouter, mais `port` pour annoncer ?
    uvicorn.run(a2a_app , host="0.0.0.0" , port= PORT )
  