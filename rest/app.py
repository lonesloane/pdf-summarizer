#!/usr/bin/python2.7
import logging
import os
import re

import sys
from flask import Flask, jsonify, abort, request, make_response
from json.decoder import JSONDecoder

import pdfparser
import pdfparser.summarizer as pdfsummarizer
import pdfparser.text_extractor as text_extractor
from pdfparser import logger, _config

# create logging file handler
fh = logging.FileHandler(os.path.join(_config.get('LOGGING', 'output_dir'), 'rest_pdf_summarizer.log'), mode='ab')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


"""Rest-API for Summary generation

"""

PDF_ROOT_FOLDER = _config.get('SUMMARIZER', 'PDF_ROOT_FOLDER')
OUTPUT_FOLDER = _config.get('SUMMARIZER', 'OUTPUT_FOLDER')
EXTRACT_MODE = text_extractor.ExtractMode.LAYOUT
EXTRACT_SUMMARY = _config.getboolean('SUMMARIZER', 'EXTRACT_SUMMARY')
NB_PROCESSES = _config.getint('SUMMARIZER', 'NB_PROCESSES')
CHUNK_SIZE = _config.getint('SUMMARIZER', 'CHUNK_SIZE')

app = Flask(__name__, static_url_path='', static_folder=_config.get('MAIN', 'static_folder'))


@app.errorhandler(404)
def not_found(error):
    """

    :param error:
    :return:
    """
    return make_response(jsonify({'error': 'Not Found'}), error.code)


@app.errorhandler(400)
def bad_request(error):
    """

    :param error:
    :return:
    """
    return make_response(jsonify({'error': 'Bad Request'}), error.code)


@app.route('/')
def root():
    """Serve root HTML file for single page application

    :return:
    """
    return app.send_static_file('index.html')


@app.route('/summarizer/1.0/generate', methods=['POST'])
def generate_summary():
    """

    :return:
    """
    if not request.json or 'document_path' not in request.json:
        abort(400)

    document_path = request.json['document_path']
    logging.info('get_document_details for: ' + document_path)
    summary = generate(document_path)
    return jsonify({'result': {'document_path': document_path,
                               'summary': summary}})


def generate(pdf_path):
    """
    Generate summary for given pdf file

    First, "clean" text is extracted, then individual sentences are passed to
    PDFSummarizer library to produce the summary

    :param pdf_path: path of PDF file to summarize
    :return:
    """
    logger.info('=' * 40)
    logger.info('Processing file {jt}'.format(jt=pdf_path))
    logger.info('found at {pdf_path}'.format(pdf_path=pdf_path))
    logger.info('=' * 40)
    try:
        pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_path)

        extractor = text_extractor.PDFTextExtractor(logger=logger)
        json_result = extractor.extract_text(pdf_file_path, mode=EXTRACT_MODE)
        pdf_txt = get_text_from_json(json_result)
        sentences = extract_sentences(pdf_txt)
        logger.debug("Nb sentences extracted: {}".format(len(sentences)))
        summarizer = pdfsummarizer.PDFSummarizer()
        results = summarizer.generate_summary(sentences)
        summary = '\n'.join([sentence._text.encode('utf-8') for sentence in results])
        logger.debug('summary:' + summary)
        return summary

    except Exception as ex:
        logger.exception("[EXCEPTION] while processing file {}\n{}".format(pdf_path, ex))
        return ex.message
    finally:
        logger.info('-' * 20)
        logger.info('End processing file {jt}'.format(jt=pdf_path))
        logger.info('-' * 20)


def extract_sentences(pdf_text):
    pdf_sentences = pdfparser.summarizer.extract_sentences(pdf_text)
    for sentence in pdf_sentences:
        sentence = sentence.strip()  # Todo: is this correct?
    return pdf_sentences


def get_text_from_json(json_content):
    decoder = JSONDecoder()
    json_pdf = decoder.decode(json_content)
    pdf_txt = ''

    if EXTRACT_SUMMARY and text_extractor.FragmentType.SUMMARY in json_pdf.keys():
        for frag in json_pdf[text_extractor.FragmentType.SUMMARY]:
            pdf_txt += concat_with_punctuation(frag)
    elif text_extractor.FragmentType.TEXT in json_pdf.keys():
        for frag in json_pdf[text_extractor.FragmentType.TEXT]:
            pdf_txt += concat_with_punctuation(frag)

    return pdf_txt


def concat_with_punctuation(frag):
    """
    Ensures each text fragment (i.e. sentence) is properly ended with some punctuation mark.

    :param frag:
    :return:
    """
    ptrn_punct = '[.!?:]'
    frag = frag.strip()
    if not re.match(ptrn_punct, frag[-1]):
        frag += '.'
    frag += '\n'
    return frag


if __name__ == '__main__':
    pass
    # app.run(debug=True, port=int(os.environ.get("PORT", 3000)))
