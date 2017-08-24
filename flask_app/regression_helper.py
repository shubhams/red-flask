import es_util
import json
import numpy as np
from googleapiclient.errors import HttpError


class RegressionHelper(object):
    def __init__(self, es):
        self.es = es

    def get_videos_data(self):
        r = self.get_video_stats()
        data = r

        regresstion_data = []
        actual_output= []
        for item in data:
            input = np.array(item['input'].values(), dtype=np.int64)
            regresstion_data.append(input)
            actual_output.append(item['output'].values())
        self.input = np.array(regresstion_data)
        self.actual_output = np.array(actual_output)
        print self.actual_output
        print 'data fetched'

    def get_data(self):
        return (self.input, self.actual_output)

    def get_video_stats(self):
        es = self.es
        try:
            fields = ["statistics.viewCount", "statistics.commentCount", "statistics.dislikeCount",
                      "statistics.favoriteCount", "channel.videoCount", "channel.subscriberCount",
                      "statistics.likeCount"]
            es_response = es_util.get_all_documents(es, fields)
            response = []
            print es_response['hits']['total']
            for hits in es_response['hits']['hits']:
                print hits['_id']
                features = {}
                actual_likes = {}
                stats = {}

                features['num_views'] = hits['_source']['statistics']['viewCount']
                features['num_comments'] = hits['_source']['statistics']['commentCount']
                features['num_dislikes'] = hits['_source']['statistics']['dislikeCount']
                features['num_favourites'] = hits['_source']['statistics']['favoriteCount']
                features['num_channel_videos'] = hits['_source']['channel']['videoCount']
                features['num_channel_subscribers'] = hits['_source']['channel']['subscriberCount']

                actual_likes['actual_likes'] = hits['_source']['statistics']['likeCount']

                stats['input'] = features
                print stats
                stats['output'] = actual_likes
                print stats
                response.append(stats)
                print response
            return response
        except HttpError, e:
            print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            return None


if __name__ == "__main__":
    es = es_util.init()
    r = RegressionHelper(es)
    r.get_videos_data()