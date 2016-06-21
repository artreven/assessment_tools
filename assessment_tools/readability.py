#!/usr/bin/env python3
import re
import math

non_b = ['[A-Z].', 'etc.', 'Mr.']
non_b_str = '[' + '|'.join(non_b) + ']'

boundary_pattern = re.compile(r'(?<=[.?!])([\s|\r\n]+)(?=\"?[A-Z])')


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
        last_word = new_sent.split()[-1]
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str, help='Text')
    args = parser.parse_args()
    text = args.text

    sentences = split_text(text)
    print('\n\nSentences\n\n')
    for i, sent in enumerate(sentences):
        print(i, sent)
