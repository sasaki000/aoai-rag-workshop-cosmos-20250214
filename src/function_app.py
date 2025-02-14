import os
import azure.functions as func
import logging
from openai import AzureOpenAI
from azure.cosmos import CosmosClient

aoai_client = AzureOpenAI(
        azure_endpoint=os.environ.get("AI_ENDPOINT"),
        api_key=os.environ.get("AI_API_KEY"),
        api_version=os.environ.get("AI_API_VERSION")
)
cosmos_client = CosmosClient.from_connection_string(os.environ.get("COSMOS_CONNECTION"))
container_client = cosmos_client.get_database_client("ai").get_container_client("azure")
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="indexer")
def indexer(req: func.HttpRequest) -> func.HttpResponse:
        docs = req.get_json()
        for doc in docs:
               content = doc["content"]
               content_vector = aoai_client.embeddings.create(input=content, model=os.environ.get("AI_DEPLOYMENT_EMBEDDING")).data[0].embedding
               item = {
                        "id": doc["id"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "content": content,
                        "contentVector": content_vector
               }
               container_client.upsert_item(item)

        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )