import os

import isodate
from flask import json
from googleapiclient.discovery import build

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

dir_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(dir_path, 'creds/developer_key.json')

# DEVELOPER_KEY = json.loads(open(file_path).read()).get('api_key')
DEVELOPER_KEY = os.environ['RED_DEV_KEY']
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)


def search_by_keyword(es, options):
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
    return get_videos_by_ids(es, query, video_ids=",".join(videos_list_ids))


def get_videos_by_ids(es, query, video_ids):
    video_response = youtube.videos().list(
        id=video_ids,
        part='snippet, contentDetails, status, statistics, topicDetails, liveStreamingDetails, recordingDetails'
    ).execute()

    return insert_into_es(es, query, video_response)


def insert_into_es(es, query, video_response):
    try:
        for video_meta in video_response.get("items", []):

            channel_response = youtube.channels().list(
                part='statistics',
                id=video_meta['snippet']['channelId']
            ).execute()
            channel_item = channel_response['items'][0]
            video_meta['channel'] = channel_item['statistics']
            video_meta['query'] = query
            video_meta['contentDetails']['duration'] = int(
                isodate.parse_duration(video_meta['contentDetails']['duration'])
                    .total_seconds())
            print json.dumps(video_meta)
            es.index(index='video', doc_type='meta', body=(
                video_meta
            ))
        return 'Inserted ' + str(len(video_response.get("items", []))) + ' records'

    except Exception as ex:
        print "Error:", ex
        return 'Error inserting records into ES'


def get_channel_info(channel_id):
    channel_response = youtube.channels().list(
        part='statistics',
        id=channel_id
    ).execute()

    return channel_response


def get_video_by_id(video_id):
    video_response = youtube.videos().list(
        id=video_id,
        part='statistics, snippet'
    ).execute()
    video_item = video_response['items'][0]
    print video_item
    channel_id = video_item['snippet']['channelId']
    print channel_id
    channel_response = youtube.channels().list(
        part='statistics',
        id=channel_id
    ).execute()
    channel_item = channel_response['items'][0]
    print channel_item
    features = {}
    likes = {}
    result = {}
    features['num_views'] = video_item['statistics']['viewCount']
    features['num_comments'] = video_item['statistics']['commentCount']
    features['num_dislikes'] = video_item['statistics']['dislikeCount']
    features['num_favourites'] = video_item['statistics']['favoriteCount']
    features['num_channel_videos'] = channel_item['statistics']['videoCount']
    features['num_channel_subscribers'] = channel_item['statistics']['subscriberCount']

    likes['actual_likes'] = video_item['statistics']['likeCount']

    result['input'] = features
    result['output'] = likes

    return result


