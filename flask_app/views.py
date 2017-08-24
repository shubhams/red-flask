import es_util
import youtube_util
from flask import request
from flask_app import app
from googleapiclient.errors import HttpError

es = es_util.init()


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/search', methods=['POST'])
def search_video_meta():
    request_json = request.get_json(force=True)
    print request_json.get('q')
    try:
        response = youtube_util.search_by_keyword(es, request_json)
        return response
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        return 'Failure'


@app.route('/channel', methods=['POST'])
def update_channel_info():
    try:
        fields = ["snippet.channelId"]
        response = es_util.get_all_documents(es, fields)
        for hit in response['hits']['hits']:
            channel_meta = youtube_util.get_channel_info(es, hit['_source']['snippet']['channelId'])
            doc_id = hit['_id']
            for channel_item in channel_meta['items']:
                channel_stats = channel_item['statistics']
                channel_info = {"channel": channel_stats}
                es_util.update_channel_info(es, doc_id, channel_info)
        return str(response['hits']['total'])
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        return 'Failure'
