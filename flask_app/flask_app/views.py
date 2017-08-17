from flask_app import app
from flask import request
from flask import jsonify
import youtube_util


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/search', methods=['POST'])
def search_video_meta():
    request_json = request.get_json()
    print request_json.get('q')
    return 'Success'
    # youtube_util.youtube_search()
