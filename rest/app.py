import logging
import os
import re

from logging.handlers import TimedRotatingFileHandler

from flask import Flask, jsonify, abort, request, make_response
from json.decoder import JSONDecoder

import pdfparser
import pdfparser.summarizer as pdfsummarizer
import pdfparser.text_extractor as text_extractor
from pdfparser import logger, _config

fh = TimedRotatingFileHandler(filename=os.path.join(_config.get('LOGGING', 'output_dir'), 'rest_pdf_summarizer.log'),
                              when='D',
                              interval=1,
                              backupCount=30)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


"""Rest-API for Summary generation

"""

PDF_ROOT_FOLDER = _config.get('SUMMARIZER', 'PDF_ROOT_FOLDER')
OUTPUT_FOLDER = _config.get('REST', 'OUTPUT_FOLDER')
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
    try:
        summary = generate(document_path)
        return jsonify({'result': {'document_path': document_path,
                                   'summary': summary}})
    except Exception as ex:
        abort(400)


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
        # First check if summary was already generated
        summary = load_saved_summary(pdf_path)
        if summary:
            return summary

        pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_path)
        logger.debug('Complete file path: {}'.format(pdf_file_path))

        extractor = text_extractor.PDFTextExtractor(logger=logger)
        json_result = extractor.extract_text(pdf_file_path, mode=EXTRACT_MODE)
        logger.debug("Extracted text:")
        logger.debug(json_result)
        pdf_txt = get_text_from_json(json_result)
        sentences = extract_sentences(pdf_txt)
        logger.debug("Nb sentences extracted: {}".format(len(sentences)))
        summarizer = pdfsummarizer.PDFSummarizer()
        results = summarizer.generate_summary(sentences)
        summary = results
        logger.debug('summary:' + ''.join(summary))
        try:
            save_summary(pdf_path, summary)
        except Exception as ex:
            logger.exception('[EXCEPTION] while saving summary: {}'.format(ex))
        return summary

    except Exception as ex:
        logger.exception("[EXCEPTION] while processing file {}\n{}".format(pdf_path, ex))
        raise ex
    finally:
        logger.info('-' * 20)
        logger.info('End processing file {jt}'.format(jt=pdf_path))
        logger.info('-' * 20)


def load_saved_summary(pdf_path):
    summary = None
    if not os.path.isfile(os.path.join(OUTPUT_FOLDER, pdf_path)):
        logger.debug('Previously generated summary not found for {}'.format(os.path.join(OUTPUT_FOLDER, pdf_path)))
        return None
    logger.debug('Previously generated summary found for {}'.format(pdf_path))
    with open(os.path.join(OUTPUT_FOLDER, pdf_path), mode='rb') as in_file:
        summary = in_file.read()
    return summary


def save_summary(pdf_path, summary):
    create_folders(pdf_path)
    with open(os.path.join(OUTPUT_FOLDER, pdf_path), mode='wb') as out_file:
        out_file.write(summary)


def create_folders(pdf_path):
    complete_folder = OUTPUT_FOLDER
    folder_structure = pdf_path.split('/')
    for folder in folder_structure[:-1]:
        complete_folder += '/' + folder
        if os.path.exists(complete_folder):
            logger.debug('{} already exists'.format(complete_folder))
        else:
            logger.debug('{} does not exist. Creating.'.format(complete_folder))
            os.mkdir(complete_folder)


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
    if not frag or len(frag) <= 0:
        return frag
    if not re.match(ptrn_punct, frag[-1]):
        frag += '.'
    frag += '\n'
    return frag


if __name__ == '__main__':
    pass
