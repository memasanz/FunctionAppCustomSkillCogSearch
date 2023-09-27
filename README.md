# Cognitive Search Index Setup

This repo will provide you with 2 search indexes.  
The first index will have the name that is in your .env file, "COG_SEARCH_INDEX"
The second index will be the name that is in your.nev file "COG_SEARCH_INDEX" with "-vector" added to the end of it.

Azure Cognitive Service Indexers manage updates/inserts and now deletes (in preview to your index).

The following code will handle:
1. Inserts/Updates to your index.
2. In the event that a file is deleted from your index, an additional function is required to handle deleting from the second index.  **This is not yet implemented.**
This will be a function triggered when a delete occurs from blob storage to delete the item from the second index.

# Cog Search Index Configuration

This repo holds 2 items.
1. An Azure Function to be leveraged as a custom skill for Cog Search
2. A notebook for configuring your Azure Cognitive Search index.

After cloning the notebook create a .env file in your directory, this will hold parameters.

To be able to run the notebook, you will need to do a pip install python-dotenv library

```
pip install python-dotenv
```
The .env file should contain the following items:

```
AZURE_OPENAI_ENDPOINT="https://xmm.openai.azure.com/"
AZURE_OPENAI_KEY="XXXXXXXX"
TEXT_EMBEDDING_ENGINE="text-embedding-ada-002"
COG_SEARCH_RESOURCE="mmx-cog-search" 
COG_SEARCH_KEY="YYYYYYY" 
COG_SEARCH_INDEX="myindex"

#function app configuration
STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=mmxcogstorage;AccountKey=4bKKMUnJjxdYN+DUo3WMJ6Sqm+AStDmU2EA==;EndpointSuffix=core.windows.net"
STORAGE_ACCOUNT="mmxcogstorage" 
STORAGE_CONTAINER="test"
STORAGE_KEY="XXXXU2EA=="
COG_SERVICE_KEY="786XXXXXf06f"
DEBUG="1"
functionAppUrlAndKey="https://funcationapp.azurewebsites.net/api/HttpTrigger1?code=1xVGCqCG3Txs0r6Q=="```

```

# Deploy Instructions
0. Create a storage account if you don't have one already.  This will be the storage account that Cognitive Search will target with the indexer.
1. Azure Cognitive Search - enable Semantic Config
2. Deploy Azure AI services in **SAME** region as Azure Cog Search
2. Deploy Azure Function App - python linux in **SAME** region as Azure Cog Search
3. In VS Code editor right click on "HttpTrigger1" and selected deploy.
4. Configure you Azure Function App to connect
    - Restart your function app.
    - On your overview - you will see the function "HttpTrigger1".  Click on it and go "Code + Test"
    - Click on "Get function URL" copy and save the URL.  You will need it to configure Cognitive Search.

    Example:
    ```https://mygithubfuncryh.azurewebsites.net/api/Embeddings?code=6zKqoduc-ezFurl==```

```
{
  "IsEncrypted": false,
  "Values": {
    "API_BASE": "https://mmx-openai.openai.azure.com/",
    "API_KEY": "XXXXX",
    "API_TYPE": "azure",
    "API_VERSION": "2022-12-01",
    "APPINSIGHTS_INSTRUMENTATIONKEY": "YYYYY",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;Ac;AccountKey=udK0239QU4j6cwQ==;EndpointSuffix=core.windows.net",
    "COG_SEARCH_KEY": "FOo5exG5D3bLg1QEfW8",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "FUNCTIONS_REQUEST_BODY_SIZE_LIMIT": "360000000",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "INDEX_NAME": "ithelpdeskv6-vector",
    "SERVICE_ENDPOINT": "https://mmx-cog.search.windows.net",
    "TEXT_EMBEDDING_MODEL": "text-embedding-ada-002",
    "STORAGE_ACCOUNT": "storage"
    "STORAGE_ACCOUNT_CONTAINER": "container"
  },
  "ConnectionStrings": {}
}
```



