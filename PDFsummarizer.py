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
REST_OUTPUT_FOLDER = _config.get('REST', 'OUTPUT_FOLDER')
EXTRACT_MODE = text_extractor.ExtractMode.LAYOUT
EXTRACT_SUMMARY = _config.getboolean('SUMMARIZER', 'EXTRACT_SUMMARY')
NB_PROCESSES = _config.getint('SUMMARIZER', 'NB_PROCESSES')
CHUNK_SIZE = _config.getint('SUMMARIZER', 'CHUNK_SIZE')
FAILED_SUMMARY_FOLDER = _config.get('SUMMARIZER', 'FAILED_SUMMARY_FOLDER')

target, source, root_folder, year = 'rest', 'olis', None, None


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
        for _ in pool.imap_unordered(generate_summary, generate_files_list(), chunksize=CHUNK_SIZE):
            pass
    finally:
        #  Always good practice to do a little cleanup
        pool.close()
        pool.join()


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
    output_file = get_output_file(info)
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
            out_file.write(results)

            log_end_process(jt, proc_logger)
        except Exception as ex:
            print('exception!!!')
            proc_logger.exception("[EXCEPTION] while processing file {} - {}".format(jt, ex.message))
        finally:
            # Required to avoid race conditions where the next "iteration" of the process tries to write
            # in the log file before the previous process is done working with it...
            log_file_handler.flush()
            log_file_handler.close()
            proc_logger.removeHandler(log_file_handler)


def get_output_file(info):
    jt, folder_structure, pdf_path = info[0], info[1], info[2]
    logger.debug('[get_output_file] target: {}, jt: {}, folder_structure: {}, pdf_path: {}'.format(target, jt, folder_structure, pdf_path))
    if target == 'bulk':
        output_file = OUTPUT_FOLDER + 'summary_' + folder_structure + '_' + jt + '.json'
    elif target == 'rest':
        complete_folder = create_folders(folder_structure)
        output_file = os.path.join(complete_folder, jt + '.pdf')
    else:
        raise Exception('Invalid target value. Unable to generate output file')
    return output_file


def create_folders(pdf_path):
    complete_folder = REST_OUTPUT_FOLDER
    folder_structure = pdf_path.split('_')
    for folder in folder_structure:
        complete_folder = os.path.join(complete_folder, folder)
        if os.path.exists(complete_folder):
            logger.debug('{} already exists'.format(complete_folder))
        else:
            logger.debug('{} does not exist. Creating.'.format(complete_folder))
            os.mkdir(complete_folder)
    logger.debug('[create_folders] complete folder: {}'.format(complete_folder))
    return complete_folder


def generate_files_list():
    if source == 'olis':
        return parse_folders()
    else:
        return parse_files()


def parse_files():
    logger.info('Parsing failed summaries files list in folder {}'.format(FAILED_SUMMARY_FOLDER))
    for input_file in os.listdir(FAILED_SUMMARY_FOLDER):
        file_year = int(input_file.split('.')[0])
        if year and file_year != year:
            logger.debug('Ignoring year {}'.format(file_year))
            continue
        logger.debug('Processing failed summaries from file: {}'.format(input_file))
        with open(os.path.join(FAILED_SUMMARY_FOLDER, input_file), 'rb') as input_list:
            for file_path in input_list:
                logger.debug('file path: {}'.format(file_path))
                file_path = file_path.replace('\\\\', '\\').rstrip()
                logger.debug('file path: {}'.format(file_path))
                components = file_path.split('\\')
                logger.debug('components: {}'.format(components))
                jt = components[3].split('.')[0]
                logger.debug('jt: {}'.format(jt))
                folder_structure = '_'.join(components[:3])
                logger.debug('folder_structure: {}'.format(folder_structure))
                if summary_available((jt, folder_structure, file_path)):
                    logger.info('Summary file found. Ignoring...')
                    continue
                logger.info('Generating summary for file: {}'.format(file_path))
                yield (jt, folder_structure, file_path)


def summary_available(info):
    if os.path.isfile(get_output_file(info)):
        logger.debug('Summary file found')
        return True
    logger.debug('Summary file not found')
    return False


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
                logger.debug('root: {}'.format(folder_structure))
                if '\\' in root:
                    folder_structure = root[2:].replace('\\', "_")
                else:
                    # 34 = len('/media/stephane/Storage/OECD/pdfs/')
                    folder_structure = root[34:].replace('/', "_")
                logger.debug('folder_structure: {}'.format(folder_structure))
                nb_processed_files += 1
                if nb_processed_files % 100 == 0:
                    logger.info('{} files analyzed...'.format(nb_processed_files))
                if summary_available((jt, folder_structure, pdf_path)):
                    continue
                yield (jt, folder_structure, pdf_path)
            else:
                logger.debug('{}/{} is not a file'.format(root, pdf_file))


def get_pdf_folder():
    pdf_folder = PDF_ROOT_FOLDER
    if root_folder:
        pdf_folder = os.path.join(PDF_ROOT_FOLDER, root_folder)
    return pdf_folder


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
    target, source, root_folder, year = None, None, None, None
    parser = argparse.ArgumentParser(
        description='Generate summaries for pdf files in specified folder and sub-folders'
    )
    # Target, i.e. Rest Service or Bulk Import
    parser.add_argument(
        '-t', '--target', type=str, help='Target mode: rest (default) or bulk', required=False, default='rest'
    )
    # Source, i.e. where to get the list of pdfs to generate the summaries
    parser.add_argument(
        '-s', '--source', type=str, help='Source of pdf list: olis (default) or report', required=False, default='olis'
    )
    # PDFs folder
    parser.add_argument(
        '-rf', '--root_folder', type=str, help='Root folder for pdf files', required=False
    )
    # Year
    parser.add_argument(
        '-y', '--year', type=int, help='Restrict processing to given year', required=False
    )
    args = parser.parse_args()
    if args.root_folder:
        root_folder = args.root_folder
        logger.info("Folder argument: {}".format(root_folder))
    if args.target:
        target = args.target
        logger.info("Target argument: {}".format(target))
    if args.source:
        source = args.source
        logger.info("Source argument: {}".format(source))
    if args.year:
        year = args.year
        logger.info("Year argument: {}".format(year))
    return target, source, root_folder, year


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
    if not frag or len(frag) <= 0:
        return frag
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

    target, source, root_folder, year = get_arguments()
    sys.exit(generate_summaries())
