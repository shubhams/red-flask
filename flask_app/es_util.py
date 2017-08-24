import certifi
import os
from elasticsearch import Elasticsearch


def init():
    # es_cred_file = os.path.join(dir_path, 'creds/es_creds.json')

    # with open(es_cred_file) as cred_file:
    #     es_creds = json.load(cred_file)
    es = Elasticsearch(http_auth=(os.environ['ES_USER'], os.environ['ES_SECRET']))
    # es = Elasticsearch(
    #     ['https://3d33da5b17c8ed0c90d3d831d3cccc9e.us-east-1.aws.found.io'],
    #     # http_auth=(es_creds.get('user'), es_creds.get('secret')),
    #     http_auth=(os.environ['ES_USER'], os.environ['ES_SECRET']),
    #     port=9243,
    #     use_ssl=True,
    #     verify_certs=True,
    #     ca_certs=certifi.where(),
    # )
    print "Connected", es.info()
    return es


def get_all_documents(es, source_fields):
    return es.search(index='video', body={
        'query': {
            'match_all': {}
        },
        "_source": source_fields
    })


def update_channel_info(es, doc_id, channel_stats):
    es.update(
        index='video',
        doc_type='meta',
        id=doc_id,
        body={"doc": channel_stats}
    )
