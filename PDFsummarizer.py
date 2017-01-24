#!env/bin/python2.7
import re
import sys
import platform
import os
import argparse
import logging
import multiprocessing as mp
from multiprocessing import freeze_support

from json.decoder import JSONDecoder

import pdfparser
import pdfparser.summarizer as pdfsummarizer
import pdfparser.text_extractor as text_extractor
from pdfparser import logger, _config

PDF_ROOT_FOLDER = _config.get('SUMMARIZER', 'PDF_ROOT_FOLDER')
OUTPUT_FOLDER = _config.get('SUMMARIZER', 'OUTPUT_FOLDER')
EXTRACT_MODE = text_extractor.ExtractMode.LAYOUT
EXTRACT_SUMMARY = _config.getboolean('SUMMARIZER', 'EXTRACT_SUMMARY')
NB_PROCESSES = _config.getint('SUMMARIZER', 'NB_PROCESSES')
CHUNK_SIZE = _config.getint('SUMMARIZER', 'CHUNK_SIZE')


def generate_summaries():
    """
    Generate PDF summaries in parallel mode using NB_PROCESSES concurrent processes

    PDFs to summarize are "produced" by the generator function parse_folders
    \nThe use of imap ensures the file generator is not loaded completely in memory
    \nunordered since the order of the results does not matter
    \nCHUNK_SIZE controls the number of files to prepare in advance per process
    :return: None
    """
    logger.info('Creating a pool of {} processes'.format(NB_PROCESSES))
    pool = mp.Pool(processes=NB_PROCESSES)
    try:
        logger.info('Begin processing files. Chunk size = {}'.format(CHUNK_SIZE))
        # TODO: there's got to be a better way than this!!!
        for _ in pool.imap_unordered(generate_summary, parse_folders(), chunksize=CHUNK_SIZE):
            pass
    finally:
        #  Always good practice to do a little cleanup
        pool.close()
        pool.join()


def parse_folders():
    """
    Generator function which produces information about the pdf files found under PDF_ROOT_FOLDER


    :return: Tuple (jt, folder_structure, pdf_path)
    """
    nb_processed_files = 0
    for root, dirs, files_list in os.walk(get_pdf_folder()):
        for pdf_file in files_list:
            if os.path.isfile(os.path.join(root, pdf_file)):
                jt, extension = pdf_file.split('.')[0], pdf_file.split('.')[1]
                if extension.lower() != 'pdf':
                    logger.debug('{} is not a pdf'.format(pdf_file))
                    continue
                pdf_path = os.path.join(root, pdf_file)
                folder_structure = root
                if '\\' in root:
                    folder_structure = root[2:].replace('\\', "_")
                logger.debug('folder_structure: {}'.format(folder_structure))
                nb_processed_files += 1
                if nb_processed_files % 100 == 0:
                    logger.info('{} files analyzed...'.format(nb_processed_files))
                yield (jt, folder_structure, pdf_path)
            else:
                logger.debug('{}/{} is not a file'.format(root, pdf_file))


def get_pdf_folder():
    start_folder = get_arguments()
    pdf_folder = PDF_ROOT_FOLDER
    if start_folder:
        pdf_folder = os.path.join(PDF_ROOT_FOLDER, start_folder)
    return pdf_folder


def generate_summary(info):
    """
    Generate summary for given pdf file

    First, "clean" text is extracted, then individual sentences are passed to
    PDFSummarizer library to produce the summary

    :param info: contains details about PDF file to summarize
    :return:
    """
    jt, folder_structure, pdf_path = info[0], info[1], info[2]
    proc_logger, log_file_handler = configure_logger()
    output_file = OUTPUT_FOLDER + 'summary_' + folder_structure + '_' + jt + '.pdf'
    with open(output_file, mode='wb') as out_file:
        log_begin_process(jt, pdf_path, proc_logger)
        try:
            pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_path)

            extractor = text_extractor.PDFTextExtractor(logger=proc_logger)
            json_result = extractor.extract_text(pdf_file_path, mode=EXTRACT_MODE)
            pdf_txt = get_text_from_json(json_result)
            sentences = extract_sentences(pdf_txt)
            proc_logger.debug("Nb sentences extracted: {}".format(len(sentences)))
            summarizer = pdfsummarizer.PDFSummarizer()
            results = summarizer.generate_summary(sentences)
            for sentence in results:
                out_file.write(sentence._text.encode('utf-8') + '\n\n')

            log_end_process(jt, proc_logger)
        except Exception:
            print('exception!!!')
            proc_logger.exception("[EXCEPTION] while processing file {}".format(jt))
        finally:
            # Required to avoid race conditions where the next "iteration" of the process tries to write
            # in the log file before the previous process is done working with it...
            log_file_handler.flush()
            log_file_handler.close()
            proc_logger.removeHandler(log_file_handler)


def configure_logger():
    """
    Configure dedicated logger per process to avoid concurrent access problems


    :return: logger, file handler
    """
    logging_level = getattr(logging, _config.get('LOGGING', 'level').upper(), None)
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % _config.get('LOGGING', 'level'))
    proc_logger = logging.getLogger(str(os.getpid()))
    proc_logger.setLevel(logging_level)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.join(_config.get('LOGGING', 'output_dir'), 'summarizer_'+str(os.getpid())+'.log'),
                             mode='ab')
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    proc_logger.addHandler(fh)
    return proc_logger, fh


def get_arguments():
    """
    Get arguments from command line

    Folder: appended to the PDF_ROOT_FOLDER to allow for more "selective" runs
    :return:
    """
    parser = argparse.ArgumentParser(
        description='Generate summaries for pdf files in specified folder and sub-folders'
    )
    # Add argument
    parser.add_argument(
        '-f', '--folder', type=str, help='Root folder for pdf files', required=False
    )
    args = parser.parse_args()
    if args.folder:
        folder = args.folder
        logger.info("Processing folder {}".format(folder))
        return folder
    return None


def log_end_process(jt, proc_logger):
    proc_logger.info('-' * 20)
    proc_logger.info('End processing file {jt}'.format(jt=jt))
    proc_logger.info('-' * 20)


def log_begin_process(jt, pdf_path, proc_logger):
    proc_logger.info('')
    proc_logger.info('=' * 40)
    proc_logger.info('Processing file {jt}'.format(jt=jt))
    proc_logger.info('found at {pdf_path}'.format(pdf_path=pdf_path))
    proc_logger.info('=' * 40)


def get_summary_or_toc(json_content):
    decoder = JSONDecoder()
    json_pdf = decoder.decode(json_content)
    pdf_txt = ''
    key = None

    if text_extractor.FragmentType.SUMMARY in json_pdf.keys():
        key = text_extractor.FragmentType.SUMMARY
    elif text_extractor.FragmentType.TABLE_OF_CONTENTS in json_pdf.keys():
        key = text_extractor.FragmentType.TABLE_OF_CONTENTS

    if key:
        for frag in json_pdf[key]:
            pdf_txt += frag + '\n'

    return pdf_txt


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


def print_pdf_summary(json_pdf_text, out_file):
    # If 'Summary' or 'Table of Content' found in pdf
    pdf_summary = get_summary_or_toc(json_pdf_text)
    if pdf_summary and len(pdf_summary) > 0:
        out_file.write("*" * 40 + "\n")
        out_file.write('\nSummary found in pdf\n')
        out_file.write("*" * 40 + "\n")
        out_file.write(pdf_summary.encode('utf-8'))


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


def extract_sentences(pdf_text):
    pdf_sentences = pdfparser.summarizer.extract_sentences(pdf_text)
    for sentence in pdf_sentences:
        sentence = sentence.strip()  # Todo: is this correct?
    return pdf_sentences


if __name__ == '__main__':
    if platform.system() == 'Windows':
        freeze_support()  # required on windows platform to allow multi-processing
    sys.exit(generate_summaries())
