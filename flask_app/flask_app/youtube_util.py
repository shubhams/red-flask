import os
from flask import json
from googleapiclient.discovery import build
from elasticsearch import Elasticsearch
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

dir_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(dir_path, 'creds/developer_key.json')

DEVELOPER_KEY = json.loads(open(file_path).read()).get('api_key')
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)


def search_by_keyword(options):
    # Call the search.list method to retrieve results matching the specified
    # query term.
    query = options.get('q')
    max_results = options.get('max_results')

    search_response = youtube.search().list(
        q=query,
        part="id",
        maxResults=max_results,
        type='video'
    ).execute()

    videos_list_ids = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos_list_ids.append(search_result["id"]["videoId"])

    print "Video IDs retreived:\n", "\n".join(videos_list_ids), "\n"
    get_vides_by_ids(query, video_ids=",".join(videos_list_ids))


def get_vides_by_ids(query, video_ids):
    video_response = youtube.videos().list(
        id=video_ids,
        part='snippet, contentDetails, status, statistics, topicDetails, liveStreamingDetails'
    ).execute()

    insert_into_es(query, video_response)


def insert_into_es(query, video_response):
    es_cred_file = os.path.join(dir_path, 'creds/es_creds.json')

    with open(es_cred_file) as cred_file:
        es_creds = json.load(cred_file)

    es = Elasticsearch(http_auth=(es_creds.get('user'), es_creds.get('secret')))
    for video_meta in video_response.get("items", []):
        video_meta['query'] = query
        print json.dumps(video_meta)
        es.index(index='video', doc_type='meta', body=(
            video_meta
        ))
