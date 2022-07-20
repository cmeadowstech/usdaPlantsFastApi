import logging, os
import queue
import azure.functions as func
from FastAPIApp import app  # Main API application
import nest_asyncio

import azure.cosmos.documents as documents
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

nest_asyncio.apply()

# Cosmos API Settings

HOST = os.environ['host']
MASTER_KEY = os.environ['master_key']
DATABASE_ID = os.environ['database_id']
CONTAINER_ID = os.environ['container_id']

async def getItem(id):
  async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    return await container.read_item(id, partition_key=id)

async def itemQuery(query):
  async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    results = container.query_items(
        query="SELECT c.Symbol,c.ScientificName,c.CommonName FROM c WHERE c.CommonName LIKE @name OR c.ScientificName LIKE @name",
        parameters=[
            { "name":"@name", "value": "%" + query + "%"}
        ]
    )

    item_list = [item async for item in results]
    return item_list

# API Stuff

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/plants/{plantId}")
async def read_item(plantId):
    return await getItem(plantId)

@app.get("/plants/")
async def read_item(name : str):
    return await itemQuery(name)

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.AsgiMiddleware(app).handle(req, context)
