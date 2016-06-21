import requests
from collections import Counter
import os
import time
import pickle
from sklearn.externals import joblib

from sklearn.linear_model import LogisticRegressionCV

stw_pid = '1DDFA806-D0B2-0001-34D2-1429D0BC1000'


def extract_cpts(text, pid=stw_pid):
    data = {
        'numberOfConcepts': 1000,
        'text': text,
        'projectId': pid,
        'language': 'en',
        'useTransitiveBroaderConcepts': True,
        'useRelatedConcepts': True
    }
    r = requests.post('http://profit.poolparty.biz/extractor/api/extract',
                      auth=('revenkoa', 'revenkpp'),
                      data=data)
    assert r.status_code == 200
    extr_cpts = []
    if 'concepts' in r.json():
        attributes = ['prefLabel', 'frequencyInDocument', 'uri',
                      'transitiveBroaderConcepts', 'relatedConcepts']
        for cpt_json in r.json()['concepts']:
            cpt = dict()
            for attr in attributes:
                if attr in cpt_json:
                    cpt[attr] = cpt_json[attr]
                else:
                    cpt[attr] = []
            extr_cpts.append(cpt)
        return extr_cpts
    else:
        return extr_cpts


def compactness(extr_cpts):
    broaders = Counter()
    relateds = Counter()
    for cpt in extr_cpts:
        for broader_cpt in cpt['transitiveBroaderConcepts']:
            broaders[broader_cpt] += 1
        for related_cpt in cpt['relatedConcepts']:
            relateds[related_cpt] += 1
        broaders[cpt['uri']] += 1
        relateds[cpt['uri']] += 1
    # filter related
    for cpt in list(relateds.keys()):
        if relateds[cpt] < 2:
            del relateds[cpt]
    broaders += relateds
    common = 0
    total = 0
    for cpt in broaders:
        cpt_score = broaders[cpt]
        if cpt_score > 1:
            common += cpt_score
        total += cpt_score
    return common / total


def teach_clf(texts_root):
    """
    It is expected that in the texts_root folder there are several folders
    representing the classes and holding the respective texts.
    """
    dirs = os.listdir(texts_root)
    Z = [] # set descriptions of data
    y = []
    start = time.time()
    for cls in dirs:
        cls_root = os.path.join(texts_root, cls)
        file_names = os.listdir(cls_root)
        for file_name in file_names:
            file_path = os.path.join(cls_root, file_name)
            text = open(file_path).read()
            text_cpts = extract_cpts(text)
            Z.append([cpt['prefLabel'] for cpt in text_cpts])
            y.append(cls)
    print('Time taken for extraction: {0:.2f} s'.format(time.time() - start))
    joblib.dump(Z, os.path.join(os.path.dirname(texts_root),
                                'raw_extraction.pkl'))
    joblib.dump(y, os.path.join(os.path.dirname(texts_root),
                                'classes.pkl'))
    features = list({x for row in Z for x in row})
    X = [[cpt in row for cpt in features] for row in Z]
    joblib.dump(features, os.path.join(os.path.dirname(texts_root),
                                       'features.pkl'))
    logit = LogisticRegressionCV(penalty='l2', solver='liblinear')
    logit.fit(X, y)
    joblib.dump(logit, os.path.join(os.path.dirname(texts_root),
                                    'trained_logit.pkl'))


if __name__ == '__main__':
    # project_root = os.path.dirname(
    #     os.path.dirname(
    #         os.path.abspath(__file__))
    # )
    # texts_root = os.path.join(project_root, 'Financial_Corpus')
    # teach_clf(texts_root)
    pass
