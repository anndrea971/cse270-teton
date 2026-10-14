import pytest
import json
from build_sentences import (get_seven_letter_word, parse_json_from_file, choose_sentence_structure,
                              get_pronoun, get_article, get_word, fix_agreement, build_sentence, structures)
from build_sentences import pronouns, articles

LETTERS = "abcdefghijklmnopqrstuvwxyz"


def make_data(noun_prefix="noun"):
    """Builds a word list where every part of speech has 26 entries (A-Z),
    so each entry is easy to predict, e.g. the word for 'C' is 'adjc'."""
    return {
        "adjectives": [f"adj{c}" for c in LETTERS],
        "nouns": [f"{noun_prefix}{c}" for c in LETTERS],
        "verbs": [f"verb{c}" for c in LETTERS],
        "adverbs": [f"adv{c}" for c in LETTERS],
        "prepositions": [f"prep{c}" for c in LETTERS],
    }


# ---------------------------------------------------------------------------
# get_seven_letter_word
# ---------------------------------------------------------------------------
def test_get_seven_letter_word(mocker):
    # Mock the input function so the test needs no user at the console
    mock_input = mocker.patch("builtins.input", return_value="seventy")
    result = get_seven_letter_word()
    # The word is returned in upper case
    assert result == "SEVENTY"
    mock_input.assert_called_once_with("Please enter a word with at least 7 letters: ")


def test_get_seven_letter_word_longer_word(mocker):
    mocker.patch("builtins.input", return_value="wonderful")
    assert get_seven_letter_word() == "WONDERFUL"


def test_get_seven_letter_word_too_short(mocker):
    mock_input = mocker.patch("builtins.input", return_value="short")
    # A word with fewer than 7 letters must raise a ValueError
    with pytest.raises(ValueError):
        get_seven_letter_word()
    mock_input.assert_called_once()


# ---------------------------------------------------------------------------
# parse_json_from_file
# ---------------------------------------------------------------------------
def test_parse_json_from_file(tmp_path):
    # Create a temporary JSON file with known data
    test_data = {"nouns": ["apple", "bear"], "verbs": ["run", "jump"]}
    file_path = tmp_path / "test.json"
    with open(file_path, "w") as f:
        json.dump(test_data, f)
    result = parse_json_from_file(file_path)
    assert result == test_data


def test_parse_json_from_file_mock_open(mocker):
    # Patch open() so no real file is needed
    mock_open = mocker.patch("builtins.open",
                             mocker.mock_open(read_data='{"nouns": ["apple"]}'))
    result = parse_json_from_file("word_lists.json")
    assert result == {"nouns": ["apple"]}
    mock_open.assert_called_once_with("word_lists.json", "r")


def test_parse_json_from_file_not_found(tmp_path):
    missing_file = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        parse_json_from_file(missing_file)


def test_parse_json_from_file_invalid_json(tmp_path):
    # A file that does not contain valid JSON
    file_path = tmp_path / "bad.json"
    file_path.write_text("this is { not valid json")
    with pytest.raises(json.JSONDecodeError):
        parse_json_from_file(file_path)


# ---------------------------------------------------------------------------
# choose_sentence_structure
# ---------------------------------------------------------------------------
def test_choose_sentence_structure():
    # Without a mock: the choice must be one of the known structures
    choice = choose_sentence_structure()
    assert choice in structures


def test_choose_sentence_structure_mock(mocker):
    mock_choice = mocker.patch("random.choice", return_value=structures[2])
    assert choose_sentence_structure() == structures[2]
    mock_choice.assert_called_once_with(structures)


# ---------------------------------------------------------------------------
# get_pronoun
# ---------------------------------------------------------------------------
def test_get_pronoun():
    assert get_pronoun() in pronouns


def test_get_pronoun_mock(mocker):
    mock_choice = mocker.patch("random.choice", return_value="she")
    assert get_pronoun() == "she"
    mock_choice.assert_called_once_with(pronouns)


# ---------------------------------------------------------------------------
# get_article
# ---------------------------------------------------------------------------
def test_get_article():
    assert get_article() in articles


def test_get_article_mock(mocker):
    mock_choice = mocker.patch("random.choice", return_value="the")
    assert get_article() == "the"
    mock_choice.assert_called_once_with(articles)


# ---------------------------------------------------------------------------
# get_word
# ---------------------------------------------------------------------------
def test_get_word():
    words = [f"word{i}" for i in range(26)]
    # A=0, B=1, C=2 ... Z=25
    assert get_word("A", words) == "word0"
    assert get_word("B", words) == "word1"
    assert get_word("C", words) == "word2"
    assert get_word("Z", words) == "word25"


# ---------------------------------------------------------------------------
# fix_agreement (mutates the list, returns nothing)
# ---------------------------------------------------------------------------
def test_fix_agreement_he_adds_s_to_verb():
    sentence = ["he", "quickly", "run", "the", "big", "dog", "near", "the", "old", "house"]
    result = fix_agreement(sentence)
    assert result is None
    assert sentence[2] == "runs"


def test_fix_agreement_she_adds_s_to_verb():
    sentence = ["she", "slowly", "walk", "the", "big", "dog", "near", "the", "old", "house"]
    fix_agreement(sentence)
    assert sentence[2] == "walks"


def test_fix_agreement_other_pronoun_unchanged():
    # "they", "I" and "we" do not change the verb
    for pronoun in ["they", "I", "we"]:
        sentence = [pronoun, "quickly", "run", "the", "big", "dog", "near", "the", "old", "house"]
        fix_agreement(sentence)
        assert sentence[2] == "run"


def test_fix_agreement_a_before_vowel_becomes_an():
    sentence = ["they", "slowly", "jump", "a", "red", "apple", "over", "the", "big", "fence"]
    fix_agreement(sentence)
    assert sentence[3] == "an"


def test_fix_agreement_a_before_consonant_unchanged():
    sentence = ["they", "slowly", "jump", "a", "red", "dog", "over", "the", "big", "fence"]
    fix_agreement(sentence)
    assert sentence[3] == "a"


def test_fix_agreement_the_at_start_adds_s_to_verb():
    # Structure: ART ADJ NOUN ADV VERB PREP ART ADJ NOUN
    sentence = ["the", "big", "dog", "slowly", "run", "near", "a", "old", "house"]
    fix_agreement(sentence)
    # Rule 3: the verb four words later gets an 's'
    assert sentence[4] == "runs"


def test_fix_agreement_the_not_at_start_unchanged():
    sentence = ["they", "slowly", "run", "the", "big", "dog", "near", "the", "old", "house"]
    original = list(sentence)
    fix_agreement(sentence)
    # "the" is not at index 0, so nothing should change
    assert sentence == original


def test_fix_agreement_a_at_start_with_vowel_noun():
    # "a" at the start uses the noun two words ahead; "the" rule is not triggered
    sentence = ["a", "big", "owl", "slowly", "run", "near", "the", "old", "house"]
    fix_agreement(sentence)
    assert sentence[0] == "an"
    assert sentence[4] == "run"


# ---------------------------------------------------------------------------
# build_sentence (random helpers are patched so the output is predictable)
# ---------------------------------------------------------------------------
def test_build_sentence_article_structure(mocker):
    # Structure 0: ART ADJ NOUN ADV VERB PREP ART ADJ NOUN (uses 7 letters)
    mock_article = mocker.patch("build_sentences.get_article", return_value="the")
    result = build_sentence("ABCDEFG", structures[0], make_data())
    # Each seed letter picks its word: A=adja, B=nounb, C=advc, D=verbd, E=prepe, F=adjf, G=noung
    # "the" at the start adds an 's' to the verb four words later
    assert result == "The adja nounb advc verbds prepe the adjf noung"
    assert mock_article.call_count == 2


def test_build_sentence_pronoun_structure(mocker):
    # Structure 1: PRO ADV VERB ART ADJ NOUN PREP ART ADJ NOUN (uses 7 letters)
    mock_pronoun = mocker.patch("build_sentences.get_pronoun", return_value="she")
    mock_article = mocker.patch("build_sentences.get_article", return_value="the")
    result = build_sentence("ABCDEFG", structures[1], make_data())
    # "she" adds an 's' to the verb two words ahead
    assert result == "She adva verbbs the adjc nound prepe the adjf noung"
    mock_pronoun.assert_called_once()
    assert mock_article.call_count == 2


def test_build_sentence_a_becomes_an(mocker):
    mocker.patch("build_sentences.get_pronoun", return_value="they")
    mocker.patch("build_sentences.get_article", return_value="a")
    # All nouns start with a vowel, so "a" must become "an"
    data = make_data(noun_prefix="our")
    result = build_sentence("ABCDEFG", structures[3], data)
    assert result == "They adva verbb an adjc ourd prepe an adjf ourg"


def test_build_sentence_all_structures_run(mocker):
    # Every known structure must produce a capitalized sentence
    # (the seed word needs at least as many letters as the words in the structure)
    mocker.patch("build_sentences.get_pronoun", return_value="we")
    mocker.patch("build_sentences.get_article", return_value="the")
    for structure in structures:
        result = build_sentence("ABCDEFGHIJ", structure, make_data())
        assert result[0].isupper()
        assert len(result.split()) == len(structure)