import os
import numpy as np

from sklearn.linear_model import LogisticRegressionCV, LogisticRegression, Lasso
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import StratifiedKFold, cross_val_score
from sklearn.feature_selection import SelectFromModel
from sklearn.utils.extmath import density

import assessment_tools.article as at_article

this_folder = os.path.dirname(os.path.abspath(__file__))
corpus_folder = '/home/artem/local_data/profit/investingcom/Financial_Corpus'

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Vectorize documents.")
    parser.add_argument('corpus_path', type=str,
                        help="The path to corpus folder.")
    parser.add_argument('server', type=str,
                        help="Protocol and url of the server.")
    parser.add_argument('pid', type=str,
                        help="ID of the thesaurus on the server.")
    parser.add_argument('username', type=str,
                        help="Username")
    parser.add_argument('pw', type=str,
                        help="Password")
    parser.add_argument('-c', '--concepts', dest='use_cpts',
                        default=False, action='store_true',
                        help="Extracted concepts taken into account?.")
    parser.add_argument('-b', '--broaders', dest='use_broaders',
                        default=False, action='store_true',
                        help="Extracted broaders taken into account?.")
    parser.add_argument('-r', '--relateds', dest='use_relateds',
                        default=False, action='store_true',
                        help="Extracted relateds taken into account?.")
    parser.add_argument('-t', '--terms', dest='use_terms',
                        default=False, action='store_true',
                        help="Terms taken into account?.")
    parser.add_argument('-d', '--idf', dest='use_idf',
                        default=False, action='store_true',
                        help="IDF taken into account?.")

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    corpus = at_article.tag_categorized_corpus(args.corpus_path)
    # Classification starts here. Just a corpus with Articles needed.
    clf, corpus, features = at_article.prepare_clf(
        corpus, args.auth_data, server=args.server, pid=args.pid,
        use_cpts=args.use_cpts,
        use_broaders=args.use_broaders,
        use_relateds=args.use_relateds,
        use_terms=args.use_terms,
        use_idf=args.use_idf
    )
    # Classification ends here. clf is trained classifier instance.
    out = ''
    out += "Next Case!\n"
    out += "cpts: {}, broaders: {}, relateds: {}, terms: {}, idf: {}\n".format(
        args.use_cpts, args.use_broaders, args.use_relateds, args.use_terms,
        args.use_idf
    )
    out += "Density of classifier: {:0.3f}, nnz: {}\n".format(
        density(clf.best_estimator_.coef_),
        len(clf.best_estimator_.coef_.nonzero()[0])
    )
    out += 'Number of features: {}\n'.format(len(features))

    scores = [x.cv_validation_scores for x in clf.grid_scores_]
    mean_str = ' '.join(['{:0.3f}'.format(x) for x in np.mean(scores, 1)])
    std_str = ' '.join(['{:0.3f}'.format(x) for x in np.std(scores, 1)])
    out += '\nScores average: ' + mean_str
    out += '\nScores stddev: ' + std_str
    out += '\nBest score: {:0.3f}, best param: {}\n'.format(clf.best_score_,
                                                            clf.best_params_)
    print(out)
    out += '\n'*5 + '*'*80 + '\n'
    with open(os.path.join(args.corpus_path, 'results.txt'), 'a') as f_results:
        f_results.write(out)
