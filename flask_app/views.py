import urlparse, numpy as np
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

if os.path.isfile(model_path):
    linear_reg.load_model()

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
    output = {}
    try:
        url = request.form['url']
        print url
        url_data = urlparse.urlparse(url)
        query = urlparse.parse_qs(url_data.query)
        video_id = query["v"][0]
        print video_id
        result = youtube_util.get_video_by_id(video_id)
        # print 'result->input: ',np.array(result['input'], dtype=np.int64)

        output['status'] = True
        output['num_views'] = result['input']['num_views']
        output['num_comments'] = result['input']['num_comments']
        output['num_dislikes'] = result['input']['num_dislikes']
        output['num_favourites'] = result['input']['num_favourites']
        output['num_channel_videos'] = result['input']['num_channel_videos']
        output['num_channel_subscribers'] = result['input']['num_channel_subscribers']
        output['actual_likes'] = result['output']['actual_likes']
        output['predicted_likes'] = int(linear_reg.test(np.array(result['input'].values(), dtype=np.int64))[0][0])
    except Exception as e:
        output['status'] = False
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
