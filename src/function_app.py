import json
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


@app.route(route="chat")
def chat(req: func.HttpRequest) -> func.HttpResponse:
        question = req.params.get("q")
        content = vector_search(question)
        answer = generate_answer(question, content)
        return func.HttpResponse(
             answer,
             status_code=200
        )


def vector_search(question):
        question_vector = aoai_client.embeddings.create(input=question, model=os.environ.get("AI_DEPLOYMENT_EMBEDDING")).data[0].embedding
        search_results = container_client.query_items( 
                query='SELECT TOP @k c.id, c.title, c.content, VectorDistance(c.contentVector,@embedding) AS SimilarityScore FROM c ORDER BY VectorDistance(c.contentVector,@embedding)', 
                parameters=[ 
                        {"name": "@k", "value": 3},
                        {"name": "@embedding", "value": question_vector}
                ], 
                enable_cross_partition_query=True)
        return json.dumps(list(search_results), ensure_ascii=False)

system_message ="""
あなたはMicrosoftAzureの専門家です。MicrosoftAzureの質問にのみ回答してください。
回答には、以下の content からのみ回答してください。

## content
{content}
"""

def generate_answer(question, content):
        messages = [
                {"role": "system", "content": system_message.format(content=content)},
                {"role": "user", "content": question}
        ]
        response = aoai_client.chat.completions.create(
                messages=messages,
                model = os.environ.get("AI_DEPLOYMENT_CHAT")
        )
        return response.choices[0].message.content