import datetime

import nose
from nose.tools import *

from assessment_tools.main import *

today = datetime.date.today()
ago_1week = today - datetime.timedelta(weeks=1)
ago_2weeks = today - datetime.timedelta(weeks=2)

def test_articles_exist_in_each_graph():
    for ld_graph, text_p in ld_graphs.items():
        assert len(get_most_recent_articles(graph_name=ld_graph, text_p=text_p)) > 0, print(
            'For graph {} no articles crawled.'.format(ld_graph)
        )

def test_recent_articles_exist():
    for ld_graph, text_p in ld_graphs.items():
        corpus = get_articles_in_interval(
            ago_2weeks.isoformat(),
            today.isoformat(),
            graph_name=ld_graph,
            text_p=text_p
        )
        if len(corpus) == 0:
            print(
                'For graph {} no articles crawled '
                'in previous 2 weeks.'.format(ld_graph)
            )
