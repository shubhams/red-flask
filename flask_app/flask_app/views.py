from flask import request
from flask_app import app

import youtube_util


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/search', methods=['POST'])
def search_video_meta():
    request_json = request.get_json(force=True)
    print request_json.get('q')
    youtube_util.youtube_search(request_json)
    return 'Success'
