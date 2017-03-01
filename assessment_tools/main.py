import dateutil.parser
import os

from sklearn.externals import joblib

from pp_api import virtuoso_calls as virtuoso
from pp_api import pp_api_calls as pp_api
import assessment_tools as at
from artem_revenko_space.settings.base import BASE_DIR

spql_profit_endpoint = 'https://profit-virtuoso.poolparty.biz/sparql'
profit_pid = '1DE00088-2B4C-0001-9BB3-1C5234FF8640'
profit_server = 'http://profit.poolparty.biz'
auth_data = ('profit', 'PPprofit')
ld_graphs = {
    'http://www.telegraph.co.uk/business/rss.xml': 'text',
    'http://feeds.bbci.co.uk/news/business/your_money/rss.xml': 'text',
    'https://content.guardianapis.com/money': 'body',
    'https://content.guardianapis.com/business': 'body',
    'http://rssfeeds.usatoday.com/usatodaycommoney-topstories&x=1': 'text',
    'https://us.spindices.com/rss': 'text',
    'http://www.ecb.europa.eu/home/html/rss': 'text',
    # 'https://www.washingtonpost.com/news/get-there/feed/': 'text',  # any texts???
    'http://rss.cnn.com/rss/money_pf': 'text',
    'http://rss.cnn.com/rss/money_autos': 'text',
    'http://rss.cnn.com/rss/money_funds': 'text',
    'http://rss.cnn.com/rss/money_pf_college': 'text',
    'http://rss.cnn.com/rss/money_pf_insurance': 'text',
    'http://rss.cnn.com/rss/money_pf_taxes': 'text',
    'http://rss.cnn.com/rss/money_retirement': 'text',
    'http://www.dailymail.co.uk/money/index.html': 'text',
    'http://www.dailymail.co.uk/money/markets/index.html': 'text',
    'http://www.dailymail.co.uk/money/saving/index.html': 'text',
    'http://www.dailymail.co.uk/money/investing/index.html': 'text',
    'http://www.dailymail.co.uk/money/cars/index.html': 'text',
    'http://www.dailymail.co.uk/money/holidays/index.html': 'text',
    'http://www.dailymail.co.uk/money/cardsloans/index.html': 'text',
    'http://www.dailymail.co.uk/money/pensions/index.html': 'text',
    'http://www.dailymail.co.uk/money/mortgageshome/index.html': 'text',
    'http://www.dailymail.co.uk/money/experts/index.html': 'text',
    'http://www.dailymail.co.uk/money/investingshow/index.html': 'text',
    'http://www.nytimes.com/services/xml/rss/nyt/YourMoney.xml': 'text',
    'http://europa.eu/newsroom/rss-feeds': 'text'
}
# replace with your folder!
data_folder = os.path.join(BASE_DIR, 'text_assessment_app',
                           'text_assessment_app', 'data')
n_topics = 30


def get_most_recent_articles(graph_name, text_p='text', n=30):
    q = """
select distinct ?s SAMPLE(?texts) as ?text SAMPLE(?dates) as ?date where
{{
  ?s <http://schema.semantic-web.at#{text_p}> ?texts .
  ?s <http://schema.semantic-web.at#date> ?dates
}}
ORDER BY DESC(?date) LIMIT {n}
    """.format(text_p=text_p, n=n)
    r = virtuoso.query_sparql_endpoint(
        sparql_endpoint=spql_profit_endpoint,
        graph_name=graph_name,
        auth_data=auth_data,
        query=q
    )
    logger.info('Graph: {}, number of recent articles: {}'.format(graph_name,
                                                                  len(r)))
    corpus = []
    for entry in r:
        name = entry['s']['value']
        text = entry['text']['value']
        date = dateutil.parser.parse(entry['date']['value'])
        artcl = at.article.Article(
            title=name, text=text, category=graph_name, date=date
        )
        corpus.append(artcl)
    return corpus


def get_articles_in_interval(start_date, end_date, graph_name, text_p='text'):
    q = """
select distinct ?s SAMPLE(?texts) as ?text SAMPLE(?dates) as ?date where
{{
  ?s <http://schema.semantic-web.at#{text_p}> ?texts .
  ?s <http://schema.semantic-web.at#date> ?dates .
  FILTER (?dates >= "{start_date}"^^xsd:dateTime)
  FILTER (?dates < "{end_date}"^^xsd:dateTime)
}} limit 5000
""".format(text_p=text_p, start_date=start_date, end_date=end_date)
    r = virtuoso.query_sparql_endpoint(
        sparql_endpoint=spql_profit_endpoint,
        graph_name=graph_name,
        auth_data=auth_data,
        query=q
    )
    logger.info('Graph: {}, number of articles in time interval: {}'.format(
        graph_name,
        len(r)
    ))
    corpus = []
    for entry in r:
        name = entry['s']['value']
        text = entry['text']['value']
        date = dateutil.parser.parse(entry['date']['value']).date()
        artcl = at.article.Article(
            title=name, text=text, category=graph_name, date=date
        )
        corpus.append(artcl)
    return corpus


def remove_duplicates(articles):
    corpus = {x.text: x for x in articles}
    return set(corpus.values())


if __name__ == '__main__':
    import time
    import logging
    import datetime

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    today = datetime.date.today()
    ago_1week = today - datetime.timedelta(weeks=1)
    ago_2weeks = today - datetime.timedelta(weeks=2)
    corpus_today_2weeksago = sum(
        [get_articles_in_interval(
            ago_2weeks.isoformat(),
            today.isoformat(),
            graph_name=ld_graph,
            text_p=text_p
         )
         for ld_graph, text_p in ld_graphs.items()],
        []
    )
    # remove empty articles
    corpus_today_2weeksago = [x for x in corpus_today_2weeksago if x.text]
    # remove duplicates
    corpus_today_2weeksago = remove_duplicates(corpus_today_2weeksago)
    logger.info('Articles collected in the 2 previous weeks: {}'.format(
        len(corpus_today_2weeksago)))
    for article in corpus_today_2weeksago:
        article.tag(auth_data=auth_data, server=profit_server, pid=profit_pid)

    corpus_today_1weekago = [
        article for article in corpus_today_2weeksago
        if article.date > ago_1week
        ]
    logger.info('Last week docs collected: {}'.format(len(corpus_today_1weekago)))
    corpus_1weekago_2weeksago = [
        article for article in corpus_today_2weeksago
        if article.date <= ago_1week
        ]
    logger.info('Two weeks ago docs collected: {}'.format(len(corpus_1weekago_2weeksago)))
    features, X, y, tfidf = at.article.vectorize(
        list(corpus_today_2weeksago),
        use_terms=False,
        # use_broaders=True,
        use_idf=True
    )
    logger.info('Number of features: {}'.format(len(features)))

    _, X0, y = at.article.vectorize(
        list(corpus_today_1weekago),
        features=features,
        use_idf=False
    )
    X0 = tfidf.transform(X0)
    _, H_0, _ = at.topics.get_topics(X0, n_topics=n_topics)
    _, X1, _ = at.article.vectorize(
        list(corpus_1weekago_2weeksago),
        features=features,
        use_idf=False
    )
    X1 = tfidf.transform(X1)
    _, H_1, _ = at.topics.get_topics(X1, n_topics=n_topics)
    # topic transitions
    M = at.topics.get_topic_transition(H_0, H_1)

    top_uris0 = at.topics.get_top_words(H_0, features)
    ticks0 = []
    for topic_words in top_uris0:
        pref_labels = pp_api.get_prefLabels(
            topic_words, profit_pid, profit_server,
            auth_data=auth_data
        )
        topic_str = ', '.join(pref_labels)
        ticks0.append(topic_str)
    top_uris1 = at.topics.get_top_words(H_1, features)
    ticks1 = []
    for topic_words in top_uris1:
        pref_labels = pp_api.get_prefLabels(
            topic_words, profit_pid, profit_server,
            auth_data=auth_data
        )
        topic_str = ', '.join(pref_labels)
        ticks1.append(topic_str)
    fig_div = at.topics.draw_topic_transition(M, ticks1, ticks0, show=False)
    fig_path = os.path.join(data_folder, 'topic_transitions', 'fig_div.txt')
    with open(fig_path, 'w') as fig_f:
        fig_f.write(fig_div)
    logger.info('Loading articles took: {:0.3f}s'.format(time.time() -
                                                         start_time))

    # get the most recent corpus
    start_time = time.time()
    corpus = set()
    for ld_graph, text_p in ld_graphs.items():
        ld_graph_corpus = get_most_recent_articles(ld_graph,
                                                   text_p=text_p,
                                                   n=30)
        corpus |= set(ld_graph_corpus)
    logger.info('Loading articles took: {:0.3f}s'.format(time.time() -
                                                         start_time))
    logger.info('Total articles loaded: {}'.format(len(corpus)))
    corpus_time = time.time()
    # remove empty articles
    corpus = [x for x in corpus if x.text]
    corpus = remove_duplicates(corpus)
    # tag articles
    for article in corpus:
        article.tag(auth_data=auth_data, server=profit_server, pid=profit_pid)
    features, X, y, tfidf = at.article.vectorize(
        list(corpus),
        use_terms=False,
        use_broaders=True,
        use_idf=True
    )
    logger.info('Tagging took: {:0.3f}s'.format(time.time() - start_time))
    tag_time = time.time()
    # train (logit) clf and NMF
    clf = at.article.prepare_clf(X, y)
    W, H, nmf = at.topics.get_topics(X, n_topics=n_topics)
    logger.info('Training took: {:0.3f}s'.format(time.time() - tag_time))
    # persist results
    joblib.dump(nmf, os.path.join(data_folder, 'nmf', 'nmf.pkl'))
    joblib.dump(clf, os.path.join(data_folder, 'clf', 'clf.pkl'))
    joblib.dump(tfidf, os.path.join(data_folder, 'tfidf', 'tfidf.pkl'))
    joblib.dump(features, os.path.join(data_folder, 'features', 'features.pkl'))
