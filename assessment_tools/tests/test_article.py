import os
import time
import requests

import nose
from nose.tools import *
from sklearn.externals import joblib

from assessment_tools.article import *
from assessment_tools.main import profit_pid, profit_server, auth_data

test_corpus_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data', 'corpus'
)


def collect_all_filepaths(path):
    filepaths = []
    names = os.listdir(path)
    pathnames = [os.path.join(path, name) for name in names]
    for pathname in pathnames:
        if os.path.isdir(pathname):
            filepaths += collect_all_filepaths(pathname)
        elif os.path.isfile(pathname):
            filepaths.append(pathname)
    return filepaths


def test_tag_article():
    category = os.listdir(test_corpus_folder)[0]
    category_path = os.path.join(test_corpus_folder, category)
    title = os.listdir(category_path)[0]
    article_path = os.path.join(category_path, title)
    with open(article_path) as f:
        text = f.read()
    article = Article(title, text, category)
    article.tag(pid=profit_pid, server=profit_server, auth_data=auth_data)
    assert list(article.cpt_freqs.keys())
    for cpt in article.cpt_freqs:
        assert article.cpt_freqs[cpt] > 0
    assert list(article.cpt_freqs_broader.keys())
    assert list(article.cpt_freqs_related.keys())
    assert article.extraction_response.json()
