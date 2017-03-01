#!/usr/bin/env python3
import re
import math

non_b = ['[A-Z].', 'etc.', 'Mr.', 'Mrs.']
non_b_str = '|'.join(non_b)

pre_b = ['.', '?', '!', '\]', '\n']
pre_b_str = r'(?<=[' + r''.join(pre_b) + r'])'

post_b = ['\(?[A-Z]', '\([a-z]']
post_b_str = r'(?=(' + r')|('.join(post_b) + r'))'

boundary_pattern = re.compile(r'{}([\"\']?[\s|\r\n]+[\"\']?){}'.format(
    pre_b_str, post_b_str
))

def split_text(text):
    """
    Function for splitting text into sentences.

    :param text: text to split into sentences
    :return: list of sentences
    """
    boundaries = re.finditer(boundary_pattern, text)
    sentences = []
    # append sentences
    start = 0
    for x in boundaries:
        span = x.span()
        new_sent = text[start:span[0]]
        new_sent_words = new_sent.split()
        if new_sent_words:
            last_word = new_sent_words[-1]
        else:
            continue
        if re.fullmatch(non_b_str, last_word):
            continue
        else:
            sentences.append(new_sent)
            start = span[1]
    sentences.append(text[start:])
    return sentences


def count_syllables(word):
    """
    Count syllables in a word. The assumption is that each group of consecutive
    vowels.

    :param word: word
    :return:
    """
    vowels = 'aeouiy'
    syllable_pattern = r'[{}]+'.format(vowels)
    indicative_vowel_groups = re.findall(syllable_pattern, word)
    num_syllables = len(indicative_vowel_groups)
    if (word[-1] == 'e' and len(word) > 3 and
                word[-2] not in vowels and word[-3] in vowels):
        num_syllables -= 1
    return num_syllables


def get_ari(text):
    """
    ari stands for automatic readability index, see
    https://en.wikipedia.org/wiki/Automated_readability_index

    :param text:
    :return: float
    """
    num_chars = len(re.findall('[a-zA-Z0-9]', text))
    num_words = len(text.split())
    num_sentences = len(split_text(text))
    ari = 4.71*(num_chars/num_words) + 0.5*(num_words/num_sentences) - 21.43
    return ari


def get_smog(text):
    """
    SMOG index relies on number of sentences and polysyllables.

    :param text:
    :return: float
    """
    num_sentences = len(split_text(text))
    words = text.split()
    num_polysyl = 0
    for word in words:
        num_syllables = count_syllables(word)
        if num_syllables >= 3:
            num_polysyl += 1
    smog = 1.043*math.sqrt(num_polysyl*30/num_sentences) + 3.1291
    return smog


def get_cli(text):
    """
    https://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index

    :param text:
    :return: float
    """
    num_chars = len(re.findall('[a-zA-Z0-9]', text))
    num_words = len(text.split())
    num_sentences = len(split_text(text))
    av_char = num_chars / num_words
    av_sent = num_sentences / num_words
    cli = 5.88*av_char - 29.6*av_sent - 15.8
    return cli


def get_fkgl(text):
    """
    https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#
    Flesch.E2.80.93Kincaid_Grade_Level

    :param text:
    :return: float
    """
    num_sentences = len(split_text(text))
    words = text.split()
    num_words = len(words)
    num_syllables = 0
    for word in words:
        num_syllables += count_syllables(word)
    fkgl = (0.39 * (num_words/num_sentences) +
            11.8 * (num_syllables/num_words) - 15.59)
    return fkgl


def get_stats(text):
    """
    Get different stats about the text.

    :param text:
    :return: tuple
    """
    num_chars = len(re.findall('[a-zA-Z0-9]', text))
    num_sentences = len(split_text(text))
    words = text.split()
    num_unique_words = len(set(words))
    num_words = len(words)
    num_syllables = 0
    num_polysyl = 0
    for word in words:
        num_syllables_word = count_syllables(word)
        num_syllables += num_syllables_word
        if num_syllables_word >= 3:
            num_polysyl += 1
    av_chars_word = num_chars / num_words
    av_syllables_word = num_syllables / num_words
    av_words_sentence = num_words / num_sentences
    return (num_words, num_unique_words, num_polysyl,
            num_chars, num_syllables, num_sentences,
            av_chars_word, av_syllables_word, av_words_sentence)



if __name__ == '__main__':
    import numpy as np
    from nltk.corpus import gutenberg

    def get_prf(tp, tpfp, tpfn):
        precision = tp / tpfp
        recall = tp / tpfn
        f1 = 2 * (precision*recall) / (precision + recall)
        return precision, recall, f1

    def benchmark_sbd():
        ps = []
        rs = []
        f1s = []
        c = 0
        for fileid in gutenberg.fileids():
            c += 1
            copy_sents_gold = gutenberg.sents(fileid)
            sents_gold = [s for s in copy_sents_gold]
            for sent_i in range(len(sents_gold)):
                new_sent = [w for w in sents_gold[sent_i] if w.isalpha()]
                sents_gold[sent_i] = new_sent
            text = gutenberg.raw(fileid)
            sents_obtained = split_text(text)
            copy_sents_obtained = sents_obtained.copy()
            for sent_i in range(len(sents_obtained)):
                new_sent = [w.group()
                            for w in re.finditer(r'\w+', sents_obtained[sent_i])
                            if w.group().isalpha()]
                sents_obtained[sent_i] = new_sent
            c_common = 0
            for sent in sents_obtained:
                if sent in  sents_gold:
                    c_common += 1
            p, r, f1 = get_prf(c_common, len(sents_obtained), len(sents_gold))
            print('\n\n', fileid)
            print('Precision: {:0.2f}, Recall: {:0.2f}, F1: {:0.2f}'.format(p, r, f1))
            ps.append(p)
            rs.append(r)
            f1s.append(f1)

        print('\n\nPrecision stats: {:0.3f} +- {:0.4f}'.format(np.mean(ps),
                                                           np.std(ps)))
        print('Recall stats: {:0.3f} +- {:0.4f}'.format(np.mean(rs),
                                                        np.std(rs)))
        print('F1 stats: {:0.3f} +- {:0.4f}'.format(np.mean(f1s),
                                                    np.std(f1s)))
        print(len(f1s))

        good_ps = [p for p in ps if p >= 0.8]
        good_rs = [r for r in rs if r >= 0.8]
        good_f1s = [f1 for f1 in f1s if f1 >= 0.8]
        print('\n Good precision stats: {:0.3f} +- {:0.4f}'.format(np.mean(good_ps),
                                                           np.std(good_ps)))
        print('Good Recall stats: {:0.3f} +- {:0.4f}'.format(np.mean(good_rs),
                                                        np.std(good_rs)))
        print('Good F1 stats: {:0.3f} +- {:0.4f}'.format(np.mean(good_f1s),
                                                    np.std(good_f1s)))
        print(len(good_f1s))

    ##########################################
    def benchmark_reads(articles):
        def text_stats(texts):
            for assessment in [get_ari, get_smog, get_fkgl, get_cli]:
                print('\nScore: ', assessment)
                scores = [assessment(article.text)
                          for article in texts]
                print('Average: {:0.2f}, std: {:0.3f}, '
                      'max: {:0.2f}, min: {:0.2f}'.format(
                    np.mean(scores), np.std(scores), max(scores), min(scores)
                ))
            stats = list(zip(*[get_stats(article.text)
                               for article in texts]))
            num_unique_words = stats[1]
            num_polysyl = stats[2]
            num_words = stats[0]
            av_syls = stats[7]
            av_words = stats[8]
            print('Unique words: average: {}, std: {}'.format(
                np.mean(num_unique_words), np.std(num_unique_words)
            ))
            print('Polysyls: average: {}, std: {}'.format(
                np.mean(num_polysyl), np.std(num_polysyl)
            ))
            print('Number of words: average: {}, std: {}'.format(
                np.mean(num_words), np.std(num_words)
            ))
            print('Syllables per word: average: {}, std: {}'.format(
                np.mean(av_syls), np.std(av_syls)
            ))
            print('Words per sentence: average: {}, std: {}'.format(
                np.mean(av_words), np.std(av_words)
            ))

        print('\n\nAll together')
        text_stats(articles)
