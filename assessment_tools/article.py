import os
import numpy as np
import scipy.sparse as sparse

from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer,\
                                            TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier

from pp_api import pp_api_calls


class Article:
    def __init__(self, title, text, category=None, date=None):
        self.title = title
        self.text = text
        self.category = category
        self.date = date
        self.cpt_freqs = None
        self.sentiment = None
        self.extraction_response = None
        self.cpt_freqs_broader = None
        self.cpt_freqs_related = None
        self.term_freqs = None

    def tag(self, auth_data, pid, server):
        assert self.text, print('Text seems to be empty: ', self.text)
        r = pp_api_calls.extract(self.text, pid, server, auth_data)
        cpts = pp_api_calls.get_cpts_from_response(r)
        cpt_freqs = {cpt['uri']: cpt['frequencyInDocument']
                     for cpt in cpts}
        self.cpt_freqs = cpt_freqs
        term_freqs = {term['textValue']: term['frequencyInDocument']
                     for term in r.json()['freeTerms']}
        self.term_freqs = term_freqs
        broaders = dict()
        relateds = dict()
        for cpt in cpts:
            for broader_uri in cpt['transitiveBroaderConcepts']:
                try:
                    broaders[broader_uri] += cpt['frequencyInDocument']
                except KeyError:
                    broaders[broader_uri] = cpt['frequencyInDocument']
            for related_uri in cpt['relatedConcepts']:
                try:
                    relateds[related_uri] += cpt['frequencyInDocument']
                except KeyError:
                    relateds[related_uri] = cpt['frequencyInDocument']
        self.cpt_freqs_broader = broaders
        self.cpt_freqs_related = relateds
        self.sentiment = pp_api_calls.get_sentiment_from_response(r)
        self.extraction_response = r
        return self


def tag_categorized_corpus(corpus_path):
    corpus = []
    for dirname in os.listdir(corpus_path):
        dir_path = os.path.join(corpus_path, dirname)
        if os.path.isdir(dir_path):
            for doc_name in os.listdir(dir_path):
                doc_path = os.path.join(dir_path, doc_name)
                if os.path.isfile(doc_path):
                    with open(doc_path) as f:
                        text = f.read()
                    new_article = Article(doc_name, text, dirname)
                    corpus.append(new_article)
    return corpus


def get_features(articles, cpts, broaders, relateds):
    features = set()
    for article in articles:
        if cpts:
            article_cpts = set(article.cpt_freqs.keys())
            features |= article_cpts
        if broaders:
            article_broaders = set(article.cpt_freqs_broader.keys())
            features |= article_broaders
        if relateds:
            article_relateds = set(article.cpt_freqs_related.keys())
            features |= article_relateds
    return list(features)


def vectorize(tagged_articles,
              features=None,
              use_cpts=True, use_broaders=False, use_relateds=False,
              use_terms=False,
              use_idf=True):
    if features is None:
        assert use_cpts or use_terms or use_broaders or use_relateds
        term_features = []
        if use_terms:
            all_terms = [artcl.term_freqs for artcl in tagged_articles]
            term_features = list(all_terms)
        cpt_features = get_features(tagged_articles,
                                    use_cpts, use_broaders, use_relateds)
        features_dict = {
            feature: ind
            for ind, feature in enumerate(cpt_features + term_features)
            }
        features = cpt_features + term_features
    else:
        features_dict = {feature: ind for ind, feature in enumerate(features)}

    X_data = []
    X_row = []
    X_col = []
    y = []

    for i in range(len(tagged_articles)):
        article = tagged_articles[i]
        y.append(article.category)
        if use_broaders:
            for cpt in set(article.cpt_freqs_broader) & set(features_dict.keys()):
                X_row.append(i)
                X_col.append(features_dict[cpt])
                X_data.append(article.cpt_freqs_broader[cpt])
        if use_relateds:
            for cpt in set(article.cpt_freqs_related) & set(features_dict.keys()):
                X_row.append(i)
                X_col.append(features_dict[cpt])
                X_data.append(article.cpt_freqs_related[cpt])
        if use_cpts:
            for cpt in set(article.cpt_freqs) & set(features_dict.keys()):
                X_row.append(i)
                X_col.append(features_dict[cpt])
                X_data.append(article.cpt_freqs[cpt])
        if use_terms:
            for term in set(article.term_freqs) & set(features_dict.keys()):
                X_row.append(i)
                X_col.append(features_dict[term])
                X_data.append(article.term_freqs[term])
    X = sparse.coo_matrix((X_data, (X_row, X_col)), shape=(len(tagged_articles),
                                                           len(features)))

    if use_idf:
        tfidf = TfidfTransformer(norm=None)
        X = tfidf.fit_transform(X)
        return features, X, y, tfidf
    else:
        return features, X, y


def prepare_clf(X, y):
    clf = GridSearchCV(LogisticRegression(penalty='l1'),
                       {'C': np.logspace(-4, 2, 10)},
                       scoring='accuracy', cv=5)
    clf.fit(X, y)
    return clf


def prepare_multiclass_clf(X, y):
    clf = GridSearchCV(LogisticRegression(penalty='l1'),
                       {'C': np.logspace(-4, 2, 10)},
                       scoring='accuracy', cv=5)
    multi_clf = OneVsRestClassifier(clf)
    multi_clf.fit(X, y)
    return multi_clf


if __name__ == '__main__':
    pass
