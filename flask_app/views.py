import urlparse
import os
import es_util
import youtube_util
from flask import request, jsonify, render_template
from flask_app import app
from googleapiclient.errors import HttpError
from linear_regression import LinearRegression
from regression_helper import RegressionHelper

es = es_util.init()

model_path = os.path.dirname(os.path.abspath(__file__)) + '/../creds/model'
reg_helper = RegressionHelper(es)
linear_reg = LinearRegression(model_path)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/train', methods=['GET'])
def train():
    if not os.path.isfile(model_path):
        reg_helper.get_videos_data()
        data, output = reg_helper.get_data()
        print output
        linear_reg.train(data, output)
        return jsonify({'status': 'new model trained'})
    else:
        linear_reg.load_model()
        return jsonify({'status': 'model loaded'})


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


@app.route('/search_url', methods=['POST'])
def search_url():
    url = request.form['url']
    url_data = urlparse.urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    video_id = query["v"][0]
    print video_id
    output = {}
    output['status'] = True
    output['num_views'] = 0
    output['num_comments'] = 0
    output['num_dislikes'] = 0
    output['num_favourites'] = 0
    output['num_channel_videos'] = 0
    output['num_channel_subscribers'] = 0
    output['actual_likes'] = 0
    output['predicted_likes'] = 0

    return jsonify(output)


@app.route('/channel', methods=['POST'])
def update_channel_info():
    try:
        fields = ["snippet.channelId"]
        response = es_util.get_all_documents(es, fields)
        for hit in response['hits']['hits']:
            channel_meta = youtube_util.get_channel_info(hit['_source']['snippet']['channelId'])
            doc_id = hit['_id']
            for channel_item in channel_meta['items']:
                channel_stats = channel_item['statistics']
                channel_info = {"channel": channel_stats}
                es_util.update_channel_info(es, doc_id, channel_info)
        return str(response['hits']['total'])
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        return 'Failure'


@app.route('/stats', methods=['GET'])
def get_video_stats():
    result = reg_helper.get_video_stats()
    return jsonify(result)
