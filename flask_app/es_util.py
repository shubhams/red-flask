import certifi
import os
from elasticsearch import Elasticsearch


def init():
    # es_cred_file = os.path.join(dir_path, 'creds/es_creds.json')

    # with open(es_cred_file) as cred_file:
    #     es_creds = json.load(cred_file)
    # es = Elasticsearch(http_auth=(os.environ['ES_USER'], os.environ['ES_SECRET']))
    es = Elasticsearch(
        ['https://3d33da5b17c8ed0c90d3d831d3cccc9e.us-east-1.aws.found.io'],
        # http_auth=(es_creds.get('user'), es_creds.get('secret')),
        http_auth=(os.environ['ES_USER'], os.environ['ES_SECRET']),
        port=9243,
        use_ssl=True,
        verify_certs=True,
        ca_certs=certifi.where(),
    )
    print "Connected", es.info()
    return es


def get_all_documents(es, source_fields):
    return es.search(index='video', body={
        'query': {
            'match_all': {}
        },
        "_source": source_fields,
        "size": 500
    })


def update_channel_info(es, doc_id, channel_stats):
    es.update(
        index='video',
        doc_type='meta',
        id=doc_id,
        body={"doc": channel_stats}
    )


def get_aggregated_likes(es):
    return es.search(index='video', body={
        "size": 0,
        "aggs": {
            "likes_by_keyword": {
                "terms": {
                    "field": "query.keyword"
                },
                "aggs": {
                    "average_likes": {
                        "avg": {
                            "field": "statistics.likeCount"
                        }
                    },
                    "average_dislikes": {
                        "avg": {
                            "field": "statistics.dislikeCount"
                        }
                    }
                }
            }
        }
    })


def get_view_count_range(es):
    return es.search(index='video', body={
        "size": 0,
        "aggs": {
            "view_ranges": {
                "range": {
                    "field": "statistics.viewCount",
                    "ranges": [
                        {
                            "key":"<999",
                            "to": 999
                        },
                        {
                            "key":"1k-10k",
                            "from": 1000,
                            "to": 9999
                        },
                        {
                            "key":"10k-50k",
                            "from": 10000,
                            "to": 49999
                        },
                        {
                            "key":"50k-100k",
                            "from": 49999,
                            "to": 99999
                        },
                        {
                            "key":"100k-200k",
                            "from": 100000,
                            "to": 199999
                        },
                        {
                            "key":"200k-500k",
                            "from": 200000,
                            "to": 499999
                        },
                        {
                            "key":"500k-1m",
                            "from": 500000,
                            "to": 999999
                        },
                        {
                            "key":"1m-10m",
                            "from": 1000000,
                            "to": 9999999
                        },
                        {
                            "key":">10m",
                            "from": 10000000
                        }
                    ]
                },
                "aggs": {
                    "keyword_in_range": {
                        "terms": {"field": "query.keyword"}
                    }
                }
            }
        }
    })


def get_popular_tags(es):
    return es.search(index='video', body={
        "size": 0,
        "aggs": {
            "doc_count": {
                "terms": {
                    "field": "query.keyword"
                },
                "aggs": {
                    "tag_count": {
                        "terms": {
                            "field": "snippet.tags.keyword"
                        }
                    }
                }
            }
        }
    })


def get_date_histogram_data(es):
    return es.search(index='video', body={
        "size": 0,
        "aggs": {
            "videos_publish_interval": {
                "date_histogram": {
                    "field": "snippet.publishedAt",
                    "interval": "month"
                }
            }
        }
    })
