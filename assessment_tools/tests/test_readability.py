import nose
from nose.tools import *

from assessment_tools.readability import *


def test_sbd_easy():
    lorem = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat?
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
    """
    sents = split_text(lorem)
    assert len(sents) == 4
    print(sents[0])
    assert sents[0].split() == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'.split()


def test_sbd_dots_questions():
    lorem = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua!?! Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat??!
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur... Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
    """
    sents = split_text(lorem)
    assert len(sents) == 4
    print(sents[0])
    assert sents[0].split() == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua!?!'.split()


def test_sbd_non_bounds():
    lorem = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua!?! Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat??!
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur Mr... Excepteur Mr. sint occaecat A.B. cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
    """
    sents = split_text(lorem)
    print(sents)
    assert_equal(len(sents), 4)
    print(sents[0])
    assert_equal(sents[0].split(),
                 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua!?!'.split())


def test_syllables_easy():
    word = 'readability'
    num_syllab = count_syllables(word)
    print(num_syllab)
    assert_equal(num_syllab, 5)


def test_syllables_take():
    word = 'take'
    num_syllab = count_syllables(word)
    print(num_syllab)
    assert_equal(num_syllab, 1)


def test_syllables_ease():
    word = 'ease'
    num_syllab = count_syllables(word)
    print(num_syllab)
    assert_equal(num_syllab, 1)


def test_syllables_stable():
    word = 'stable'
    num_syllab = count_syllables(word)
    print(num_syllab)
    assert_equal(num_syllab, 2)


def test_syllables_stale():
    word = 'stale'
    num_syllab = count_syllables(word)
    print(num_syllab)
    assert_equal(num_syllab, 1)

wiki_about = """
People of all ages, cultures and backgrounds can add or edit article prose,
references, images and other media here. What is contributed is more important
than the expertise or qualifications of the contributor. What will remain
depends upon whether the content is free of copyright restrictions and
contentious material about living people, and whether it fits within
Wikipedia's policies, including being verifiable against a published reliable
source, thereby excluding editors' opinions and beliefs and unreviewed
research. Contributions cannot damage Wikipedia because the software allows
easy reversal of mistakes and many experienced editors are watching to help
ensure that edits are cumulative improvements. Begin by simply clicking the
Edit link at the top of any editable page!
"""


def test_ari():
    ari = get_ari(wiki_about)
    assert 16 < ari < 18


def test_smog():
    smog = get_smog(wiki_about)
    print(smog)
    assert 16 < smog < 18


def test_cli():
    cli = get_cli(wiki_about)
    print(cli)
    assert 16 < cli < 18


def test_fkgl():
    fkgl = get_fkgl(wiki_about)
    print(fkgl)
    assert 16 < fkgl < 18


if __name__ == '__main__':
    nose.main()
