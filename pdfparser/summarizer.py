# -*- coding: utf8 -*-
import os
from nltk import PunktSentenceTokenizer

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
# from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer

from pdfparser import _config


PROJECT_FOLDER = _config.get('MAIN', 'project_folder')
PDF_ROOT_FOLDER = os.path.join(PROJECT_FOLDER, 'pdfs')
LANGUAGE = "english"  # TODO: identify pdf language
SENTENCES_COUNT = _config.getfloat('MAIN', 'SENTENCES_COUNT')  # TODO: make parameter based on length of submitted text
STOP_WORDS_FOLDER = _config.get('SUMMARIZER', 'STOP_WORDS_FOLDER')


class PDFSummarizer:

    def __init__(self):
        pass

    def generate_summary(self, pdf_sentences):
        if len(pdf_sentences) < SENTENCES_COUNT:
            print('Less than {} sentences extracted, returning entire text'.format(SENTENCES_COUNT))
            return pdf_sentences
        pdf_string = '\n'.join((sentence.encode('utf-8') for sentence in pdf_sentences))
        parser = PlaintextParser.from_string(pdf_string, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        summary = summarizer(parser.document, SENTENCES_COUNT)
        summary = remove_repetition(summary)
        summary = '\n'.join([sentence._text.encode('utf-8') for sentence in summary])
        return summary


def get_stop_words(language):
    with open(os.path.join(STOP_WORDS_FOLDER, "english.txt")) as open_file:
        return parse_stop_words(open_file.read())


def parse_stop_words(data):
    return frozenset(w.rstrip() for w in data.splitlines() if w)


def remove_repetition(summary):
    results = set(summary)
    return results


def extract_sentences(pdf_text):
    pdf_sentences = PunktSentenceTokenizer().tokenize(pdf_text)
    return pdf_sentences


if __name__ == '__main__':
    pass
