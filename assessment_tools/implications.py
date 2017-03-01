import os
import numpy as np

from sklearn.externals import joblib

import fca
import error_checker.error_finder as ef

from assessment_tools.cpts import Article, get_isoweek_articles

dirpath = os.path.dirname(os.path.abspath(__file__))
basedirpath = os.path.dirname(dirpath)


def articles2cxt(articles, features=None):
    if features is None:
        atts = list({cpt for article in articles
                     for cpt in article.cpt_freqs})
    else:
        atts = features
    table = [[cpt in article.cpt_freqs for cpt in atts]
             for article in articles]
    objs = list(range(len(articles)))
    return fca.Context(table, objs, atts)


if __name__ == '__main__':
    import cProfile

    annotated = joblib.load(os.path.join(basedirpath, 'annotated_articles.pkl'))
    week_lag = 3
    for week_n in range(week_lag, 52):
        new = get_isoweek_articles(annotated, 2015, week_n, 1)
        old = get_isoweek_articles(annotated, 2015, week_n - week_lag, week_lag)
        n_new = len(new)
        n_old = len(old)
        all_cxt = articles2cxt(old + new)
        old_cxt = articles2cxt(old, all_cxt.attributes)
        print('Len new: ', len(new), ' Len old: ', len(old))
        print('N tokens :', len(all_cxt.attributes))

        new_cxt = fca.Context(all_cxt.table[n_old:],
                              all_cxt.objects[n_old:],
                              all_cxt.attributes)
        print('Min old support: ', round(len(old)/7))
        print('Min new support: ', int(round(np.sqrt(len(new)))))
        broken_dependencies = ef.inspect_frequent(old_cxt,
                              new_cxt,
                              min_supp_old=round(len(old)/7),
                              min_supp_new=int(round(np.sqrt(len(new)))),
                              min_conf=0.7, min_conf_new=0.8)

        stmt = '''broken_dependencies = ef.inspect_frequent(old_cxt,
                              new_cxt,
                              min_supp_old=round(len(old)/10),
                              min_supp_new=round(len(new)/10),
                              min_conf=0.8, min_conf_new=0.8)'''
        # cProfile.run(stmt)
        print()
        print('Broken dependencies are:')
        for dep in broken_dependencies:
            print(dep[0], len(dep[1]), dep[2])
        pos_conc_dict = dict()
        neg_conc_dict = dict()
        for dep in broken_dependencies:
            dep, support, conf, new_support = dep
            if isinstance(dep, fca.NegativeImplication):
                for att in dep.conclusion:
                    try:
                        neg_conc_dict[att] |= new_support
                    except KeyError:
                        neg_conc_dict[att] = new_support.copy()
            else:
                for att in dep.conclusion:
                    try:
                        pos_conc_dict[att] |= new_support
                    except KeyError:
                        pos_conc_dict[att] = new_support.copy()
        print('\n\nNegative trends:')
        for att in pos_conc_dict:
            print(att, len(pos_conc_dict[att]))
        print('\n\nPositive trends:')
        for att in neg_conc_dict:
            print(att, len(neg_conc_dict[att]))
        input()
