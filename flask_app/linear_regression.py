import cPickle
from sklearn import linear_model


class LinearRegression(object):
    def __init__(self, model_path):
        self.model_path = model_path
        self.reg = linear_model.LinearRegression()

    def train(self, data, actual_output):
        self.reg.fit(data, actual_output)
        self.save_model()

    def test(self, data):
        return self.reg.predict([data])

    def save_model(self):
        with open(self.model_path, 'wb') as fid:
            cPickle.dump(self.reg, fid)

    def load_model(self):
        with open(self.model_path) as fid:
            self.reg = cPickle.load(fid)


if __name__ == '__main__':
    from regression_helper import RegressionHelper

    rh = RegressionHelper()
    rh.get_videos_data()
    data, output = rh.get_data()
    print output
    lr = LinearRegression()
    lr.train(data, output)
    print lr.test([0, 9, 1475943, 3479, 0, 537])
    print 'finished'
