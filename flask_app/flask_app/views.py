from flask import request
from flask_app import app

import youtube_util
from googleapiclient.errors import HttpError


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/search', methods=['POST'])
def search_video_meta():
    request_json = request.get_json(force=True)
    print request_json.get('q')
    try:
        response = youtube_util.search_by_keyword(request_json)
        return response
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        return 'Failure'
