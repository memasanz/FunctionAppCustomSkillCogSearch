import logging
import azure.functions as func
import uuid
import json
import openai
from openai.embeddings_utils import get_embedding
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import re
import time
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient 

def push_to_vector_index(data, embeddings, source):
    service_endpoint = os.environ['SERVICE_ENDPOINT']
    index_name = os.environ['INDEX_NAME']
    key = os.environ['COG_SEARCH_KEY']
    credential = AzureKeyCredential(key)
    #index_client = SearchIndexClient(endpoint=service_endpoint, credential=credential)
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    #search_client = SearchIndexClient(service_endpoint, index_name, AzureKeyCredential(key))
    title_embeddings = generate_embeddings(source)

    docs = search_client.search(search_text=f"{source}", search_fields=["path"], include_total_count = True)
    count = docs.get_count()
    delete_docs = []
    if count > 0:
        logging.info('deleting existing documents for index')
        for x in docs:
            delete_docs.append({"key" : x['key']})
            logging.info(delete_docs)
        result = search_client.delete_documents(documents=delete_docs)
        for i in range (0, len(result)):
            if result[0].succeeded  == False:
                raise ValueError('A very specific bad thing happened.')
        logging.info('deletion occured:'  + str(len(result)))
    else:
        logging.info('no documents to delete')


    for i in range(len(data)):
        text = data[i]
        title_embeddings = title_embeddings
        embedd = embeddings[i]
        random_str = uuid.uuid4()
        logging.info(len(title_embeddings))
        logging.info(len(embedd))
        path = "https://" + os.environ['STORAGE_ACCOUNT'] + ".blob.core.windows.net/" + os.environ['STORAGE_ACCOUNT_CONTAINER'] + "/" + source
        path = path.replace(' ', '%20')
        document = {
            "key": f"{random_str}",
            "title": f"{source}",
            "content": f"{text}",
            "path": f"{path}",
            "contentVector": embedd,
            "titleVector": title_embeddings
        }

        logging.info(document)
        result = search_client.upload_documents(documents=document)
        logging.info("Upload of new document succeeded: {}".format(result[0].succeeded))
        logging.info('**************************************')
        json_string = json.dumps(document)
        logging.info(json_string)



def generate_embeddings(text):
    engine = os.environ['TEXT_EMBEDDING_MODEL']
    response = openai.Embedding.create(
    input=text, engine=engine) #engine = deployment name of your ada-0002 model
    embeddings = response['data'][0]['embedding']
    return embeddings

def text_split_embedd(relevant_data):
    logging.info('text_split_embedd')

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(relevant_data)

    df = pd.DataFrame(texts, columns =['text'])
    
    engine = os.environ['TEXT_EMBEDDING_MODEL']
    logging.info('engine = ' + engine)
    start = 0
    df_result = pd.DataFrame()
    for i, g in df.groupby(df.index // 1):
        try:
            logging.info(g)
            logging.info(type(g))
            logging.info('_' * 15)
            g['curie_search'] = g["text"].apply(lambda x : get_embedding(x, engine =  engine))

            df_result = pd.concat([df_result,g], axis=0)

        except Exception as e:
            logging.info(e)
            logging.info('Error in get_embedding')
            continue
        finally:
            logging.info('finally')
            continue

    df_result
    logging.info(len(df_result))

    embeddings = []
    data = []

    for index, row in df_result.iterrows():
        embeddings.append(row['curie_search'])
        data.append(row['text'])


    return data, embeddings


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
def compose_response(json_data):
    logging.info('compose response')
    values = json.loads(json_data)['values']

    results = {}
    results["values"] = []

    for value in values:
        logging.info('about to transform value')
        outputRecord = transform_value(value)
        if outputRecord != None:
            results["values"].append(outputRecord)
        else:
            logging.info('outputRecord is None')
    # Keeping the original accentuation with ensure_ascii=False

    logging.info('**************************')
    logging.info('results')
    logging.info(results)
    return json.dumps(results, ensure_ascii=False)

def transform_value(value):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']   
        assert ('text' in data), "'text' field is required in 'data' object."
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "data":{},
            "errors": [ { "message": "Error:" + error.args[0] }   ]
            })
 

    try:                
        # Getting the items from the values/data/text
        logging.info('getting text data')
        searchresults = value['data']['text']
        source = value['data']['source']
        logging.info(searchresults)

        logging.info('source')
        logging.info(source)

        API_BASE = os.environ["API_BASE"]
        API_KEY = os.environ["API_KEY"]
        API_VERSION = os.environ["API_VERSION"]
        API_TYPE = os.environ["API_TYPE"]
        

        openai.api_type = API_TYPE
        openai.api_base = API_BASE
        openai.api_version = API_VERSION
        openai.api_key  = API_KEY
        
        logging.info(openai.api_key)
        logging.info(openai.api_base)
        logging.info(openai.api_version)
        logging.info(openai.api_type)

        data, embeddings = text_split_embedd(searchresults)

        push_to_vector_index(data, embeddings, source)

        logging.info('**********data********************')
        logging.info(data)

        logging.info('**********embeddings********************')
        logging.info(embeddings)
    except Exception as e:
        logging.info(e)
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Could not complete operation for record."  } , {e}  ]
            })

    return ({
            "recordId": recordId,
            "data": {
                "embeddings_text": data,
                "embeddings": embeddings
                    }
            })
