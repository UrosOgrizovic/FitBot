from lxml import etree
from lxml.etree import tostring
import re
from unidecode import unidecode
import nltk
from constants import STOP_WORDS, LETTERS
from string import printable


def match_regex(sent):
    """Gets link text. Links are formatted as [[Wikipedia article title|link text]].
    Examples: 1. [[sagittal plane|sagittal-plane]]
    2. [[vertebral column|disc of the spine]].
    I only want to keep the link text.

    This does avoid things with more than one vertical slash, such as:
    [[File:Natalia Zabolotnaya 2012b.jpg|thumb|180px|[[Natalia Zabolotnaya]].
    That is expected behavior.

    Args:
        sent (string)
    Returns:
        string: sentence with "[[Wikipedia article title|link text]]" parts turned
        to "link text"
    """
    regex = r"\[\[(.[^\|]*)\|(.[^\|]*)\]\]"
    match = re.findall(regex, sent) # list of tuples
    match = [tup[1] for tup in match]   # get link text
    # nested re.subs
    for i in range(len(match)):
        '''The last param in sub() is how many replacements to do.
        Since I want to replace with a different string each time,
        I'm only doing 1 replacement.'''
        sent = re.sub(regex, match[i], sent, 1)
    return sent


def lemmatization(sent):
    """Lemmatize sentence, removew stop words and non-english words

    Args:
        sent (sent): sentence to modify

    Returns:
        string: modified sentence
    """
    lemmatizer = nltk.stem.WordNetLemmatizer()
    new_sent = ""
    sent = sent.split(" ")
    for i in range(len(sent)):
        word = sent[i]
        cnt = word.count("|")
        if cnt > 1:
            continue
        elif cnt == 1:
            word = word.split("|")[1]
        filtered_word = ''.join(filter(lambda x: x in printable, word))
        # eliminate stop words and non-english words, such as ὀρθός
        if len(word) > 0 and word not in STOP_WORDS and len(filtered_word) == \
                len(word):
            punctuation = ""

            '''if the word ends in a punctuation mark,
            don't lemmatize the punctuation mark'''
            if word[-1] not in LETTERS:
                punctuation = word[-1]
                word = word[:-1]
            word = lemmatizer.lemmatize(word)
            new_sent += word + punctuation + " "

    return new_sent


def read_data(input_file_path):
    tree = etree.parse(input_file_path)
    root = tree.getroot()

    document_dictionaries = []
    # iterate through all the titles
    for text_node in root.findall(".//text", namespaces=root.nsmap)[:20]:
        document_dictionaries.append({'text': text_node.text, 'meta': None})

    for doc_dict in document_dictionaries:

        doc_dict["text"] = doc_dict["text"].replace("'''", "")  # remove bold text
        # remove tags and the text they contain, e.g. <ref>some text</ref>
        doc_dict["text"] = re.sub(r'[<>].*[<>]', '', doc_dict["text"])
        # remove curly brackets and the text they contain, e.g. <ref>some text</ref>
        doc_dict["text"] = re.sub(r'[{{}}].*[{{}}]', '', doc_dict["text"])
        doc_dict["text"] = re.sub(r'[#].*[|]', ' ', doc_dict["text"])   # remove # before |
        doc_dict["text"] = re.sub(r'[==].*[==]', '', doc_dict["text"])
        doc_dict["text"] = re.sub(' +', ' ', doc_dict["text"])  # remove multiple spaces
        doc_dict["text"] = doc_dict["text"].replace("\n", " ")
        # Remove accented characters from text, e.g. café
        doc_dict["text"] = unidecode(doc_dict["text"])
        text_sents = nltk.tokenize.sent_tokenize(doc_dict["text"])
        new_sents = []
        for sent in text_sents:
            new_sents.append(match_regex(sent))
            new_sents[-1] = re.sub(r'\[\[File:.*\]\]', '', new_sents[-1])
            new_sents[-1] = re.sub(r'Category:.*', '', new_sents[-1])

        text_sents = new_sents
        new_sents = []
        for sent in text_sents:
             # remove brackets, i.e. links
            sent = sent.replace("[[", "")
            sent = sent.replace("]]", "")

            new_sents.append(lemmatization(sent))
        doc_dict["text"] = "".join(new_sents)

    return document_dictionaries


if __name__ == "__main__":
    input_file_path = "data/Wikipedia-Strength-Training.xml"
    document_dictionaries = read_data(input_file_path)
