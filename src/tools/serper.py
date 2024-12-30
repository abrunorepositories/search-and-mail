from langchain.tools import BaseTool
from pydantic import PrivateAttr
import requests

class SerperSearchTool(BaseTool):

    name: str = "serper_search_tool"
    description: str = "Realiza buscas no Google utilizando a API do Serper. Útil para obter informações atualizadas e resultados de pesquisa."

    _api_key: str = PrivateAttr()

    def __init__(self, api_key: str):
        super().__init__()
        self._api_key = api_key

    def _run(self, query: str) -> str:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self._api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            if "organic" in data and len(data["organic"]) > 0:
                snippets = []
                for result in data["organic"]:
                    title = result.get("title", "No title")
                    link = result.get("link", "No link")
                    snippet = result.get("snippet", "No snippet")
                    snippets.append(f"Título: {title}\nLink: {link}\nTrecho: {snippet}\n")
                return "\n\n".join(snippets)
            else:
                return "Não foram encontrados resultados relevantes."

        except Exception as e:
            return f"Erro ao consultar a API do Serper: {str(e)}"

    async def _arun(self, query: str) -> str:
       raise NotImplementedError("Serper não suporta consultas assíncronas neste exemplo.")