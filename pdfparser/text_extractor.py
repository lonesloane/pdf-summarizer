# -*- coding: utf8 -*-
import re
from cStringIO import StringIO
from json import JSONEncoder

from xml.etree.ElementTree import Element, SubElement, tostring
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTRect, LTChar
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdfparser import _log_level, _config
from pdfparser.pdf_fragment_type import FragmentType
from pdfparser.pdf_page_filter import PDFPageFilter
from pdfparser.report import Report
from pdfparser.table_edges_extractor import Cell

# LOG Files for debugging and visual analysis purposes
rec_def = None
text_def = None
text_keys = {'Text', 'Summary'}


class ExtractMode:
    def __init__(self):
        pass

    LAYOUT = 'layout'
    TEXT = 'text'


class OutputFormat:
    def __init__(self):
        pass

    JSON = 'json'
    XML = 'xml'
    TEXT = 'txt'


class PDFTextExtractor:

    def __init__(self, report=None, single_page=None, logger=None):
        # todo: review this dynamic import
        if not logger:
            from pdfparser import logger
        self.logger = logger
        self.filter_tables = _config.getboolean('MAIN', 'filter_tables')

        self.contents = dict()
        self.report = report if report else Report()
        self.pdf_filter = PDFPageFilter(logger=self.logger, report=self.report)
        self.previous_p = None
        self.annex_found = False
        self.single_page = int(single_page) if single_page else -1
        self.minx0 = None
        self.maxx1 = None

    def extract_text(self, pdf_file_path, mode=None, format=None):
        # TODO: See if possible to detect that page is in landscape mode instead of regular portrait mode
        #       (eg. IMP19953820ENG)
        # TODO: Take pdf 'type' into account (see JT03366237)
        # TODO: set config parameter to choose output format (i.e. plain text, json, xml)

        output = None
        output_format = format if format else OutputFormat.JSON
        mode = mode if mode else ExtractMode.LAYOUT

        if mode is ExtractMode.LAYOUT:
            self.logger.info('Layout based extraction.')
            self.convert_pdf_layout_to_text(pdf_file_path)

        if mode is ExtractMode.TEXT or self.should_force_raw_extraction():
            self.logger.info('Raw text extraction.')
            self.convert_pdf_to_txt(pdf_file_path)

        if output_format is OutputFormat.TEXT:
            output = ''
            for key in text_keys.intersection(self.contents.keys()):
                for elem in self.contents[key]:
                    output += elem.encode('utf-8')+'\n'

        elif output_format is OutputFormat.JSON:
            encoder = JSONEncoder()
            output = encoder.encode(self.contents)

        elif output_format is OutputFormat.XML:
            top = Element('pdf-content')
            for key in self.contents.keys():
                child = SubElement(top, key.lower())
                for elem in self.contents[key]:
                    sub_child = SubElement(child, 'item')
                    sub_child.text = elem
            output = tostring(top)

        return output

    def should_force_raw_extraction(self):
        """

        :return: True if extracting multiple pages and resulting TEXT is empty
        """
        if self.single_page != -1:
            return False
        elif FragmentType.TEXT not in self.contents or len(self.contents[FragmentType.TEXT]) == 0:
            return True
        else:
            return False

    def convert_pdf_to_txt(self, path):
        rsrcmgr = PDFResourceManager()
        codec = 'utf-8'
        laparams = LAParams()
        fp = file(path, 'rb')
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page_no, page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,
                                                         caching=caching, check_extractable=True)):
            retstr = StringIO()

            page_text = ''
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            try:
                PDFPageInterpreter(rsrcmgr, device).process_page(page)
            except TypeError:
                self.logger.error('TypeError: "NoneType" object has no attribute "__getitem__"')
            else:
                page_text = retstr.getvalue().decode(encoding='utf-8')
            finally:
                device.close()
                retstr.close()

            self.logger.info('=' * 20)
            self.logger.info('Processing page {page_nb}'.format(page_nb=page_no))
            self.logger.info('=' * 20)
            self.add_text_content(page_text, fragment_type=FragmentType.TEXT)

        fp.close()

    def convert_pdf_layout_to_text(self, pdf_doc):
        fp = None
        try:
            # open the pdf file
            fp = open(pdf_doc, 'rb')
            # create a parser object associated with the file object
            parser = PDFParser(fp)
            # create a PDFDocument object that stores the document structure
            doc = PDFDocument(parser)
            # connect the parser and document objects
            parser.set_document(doc)

            if doc.is_extractable:
                self.logger.info("-"*20)
                self.logger.info("Parsing PDF content")
                self.logger.info("-"*20)
                pages = self.parse_pages(doc)

                fragment_type = FragmentType.UNKNOWN
                if self.single_page != -1:  # TODO: See if single page extraction is still working...
                    fragment_type = FragmentType.TEXT
                for page_nb, (page_text, page_cells) in enumerate(pages):
                    if self.single_page != -1:
                        page_nb = self.single_page+1
                    self.logger.debug('-'*20)
                    self.logger.debug('Processing page {page_nb}'.format(page_nb=page_nb))
                    self.logger.debug('-'*20)
                    fragment_type = self.process_page(page_text, page_cells, fragment_type, page_nb)
                # Add any leftover text
                if self.previous_p:
                    self.contents[FragmentType.TEXT].extend({self.previous_p})
            else:
                self.logger.error('Document not extractable')

        except IOError:
            # the file doesn't exist or similar problem
            self.logger.error("Error while processing pdf file.")
        finally:
            # close the pdf file
            if fp:
                fp.close()

    def parse_pages(self, doc):
        """With an open PDFDocument object, get the pages and parse each one
        """
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = []
        for page_number, page in enumerate(PDFPage.create_pages(doc)):
            if self.single_page != -1 and page_number != self.single_page:
                continue
            if _log_level > 2:
                self.logger.debug('\n'+'-'*50)
                self.logger.debug('Processing page {i}'.format(i=page_number))
                self.logger.debug('-'*50)
            try:
                interpreter.process_page(page)
                # receive the LTPage object for this page
                layout = device.get_result()
                # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
                pages.append(self.parse_page_layout(layout))
            except TypeError:
                self.logger.error('TypeError: "NoneType" object has no attribute "__getitem__"')

        return pages

    def parse_page_layout(self, lt_objs):
        """Iterate through the list of LT* objects and capture the text data contained in each"""

        self.minx0 = None
        txt_x0 = None
        txt_x1 = None

        global rec_def, text_def
        if _log_level > 2:
            rec_def = open('rec_def.log', mode='w')
            text_def = open('text_def.log', mode='w')

        page_text = dict()  # k=(x0, y0, x1, y1) of the bbox, v=text within that bbox
        page_cells = []
        for lt_obj in lt_objs:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                if _log_level > 1:
                    self.logger.debug('LTTextBox or LTTextLine')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)  # TODO: change this into page_text.add()
                txt_x0 = lt_obj.bbox[0]
                txt_x1 = lt_obj.bbox[2]
            elif isinstance(lt_obj, LTChar):
                if _log_level > 1:
                    self.logger.debug('LTChar')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)
                txt_x0 = lt_obj.bbox[0]
                txt_x1 = lt_obj.bbox[2]
            elif isinstance(lt_obj, LTRect):
                # store cell coordinates used to identify table boundaries
                x0 = lt_obj.bbox[0]
                y0 = lt_obj.bbox[1]
                x1 = lt_obj.bbox[2]
                y1 = lt_obj.bbox[3]
                cell = Cell(x0, y0, x1, y1, logger=self.logger)
                if cell.rows > 0 or cell.columns > 0:  # ignore 'lines' (i.e. cell without content within)
                    page_cells.append(cell)
                    if _log_level > 1:
                        self.logger.debug('LTRect: [x0={x0}, y0={y0}, x1={x1}, y1={y1}]'.format(x0=x0, y0=y0,
                                                                                                x1=x1, y1=y1))
                        if _log_level > 2:
                            rec_def.write('{x0},{y0},{x1},{y1}\n'.format(x0=x0, y0=y0, x1=x1, y1=y1))
            elif isinstance(lt_obj, LTFigure):
                if _log_level > 1:
                    self.logger.debug('LTFigure -- ignoring')
                # LTFigure objects are containers for other LT* objects, so recurse through the children
                # return self.parse_figure(lt_obj)
                continue
            else:
                # yet another type of Layout object...
                if _log_level > 1:
                    self.logger.debug('Unknown object type: ' + str(type(lt_obj)))

            if not self.minx0 or (txt_x0 and txt_x0 < self.minx0):
                self.minx0 = txt_x0
            if not self.maxx1 or (txt_x1 and txt_x1 > self.maxx1):
                self.maxx1 = txt_x1

        if _log_level > 2:
            rec_def.close()
            text_def.close()

        return page_text, page_cells

    def parse_figure(self, lt_objs):
        page_cells = []
        page_text = dict()  # k=(x0, y0, x1, y1) of the bbox, v=text within that bbox
        for lt_obj in lt_objs:
            if isinstance(lt_obj, LTChar):
                if _log_level > 1:
                    self.logger.debug('LTChar')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)

        return page_text, page_cells

    def process_page(self, page_txt, page_cells, previous_fragment_type, page_nb):
        # TODO: Do some systematic tests to compare the quality of the text extracted from layout
        #       with that of text extracted with "regular" text extraction.
        # TODO: what about very special cases like statistical reports with no text at all? See JT00021419
        # TODO: refactor to submit page only once and validate every options all at the same time.
        # ==> then only decide what type of fragment (i.e. annex or participants list... see JT00124770)
        self.logger.debug('Enter page validation')

        coord = None

        while True:

            # cover is expected to be first page only
            is_cover = False if page_nb > 0 else self.pdf_filter.is_cover(page_txt)
            if is_cover:
                self.logger.debug('MATCH - {Cover Page} found.')
                current_fragment_type = FragmentType.COVER_PAGE
                break

            is_toc = self.pdf_filter.is_toc(page_txt, previous_fragment_type)
            if is_toc:
                self.logger.debug('MATCH - {Table Of Contents} found.')
                current_fragment_type = FragmentType.TABLE_OF_CONTENTS
                break

            # do not report summary found within annex
            is_summary = False if self.report.annex != 0 else self.pdf_filter.is_summary(page_txt)
            if is_summary:
                self.logger.debug('MATCH - {Summary} found.')
                current_fragment_type = FragmentType.SUMMARY
                break

            is_glossary = self.pdf_filter.is_glossary(page_txt, previous_fragment_type)
            if is_glossary:
                self.logger.debug('MATCH - {Glossary} found.')
                current_fragment_type = FragmentType.GLOSSARY
                break

            is_bibliography, coord = self.pdf_filter.is_bibliography(page_txt, previous_fragment_type)
            if is_bibliography:
                self.logger.debug('MATCH - {Bibliography} found.')
                current_fragment_type = FragmentType.BIBLIOGRAPHY
                break

            is_participants_list, coord = self.pdf_filter.is_participants_list(page_txt, previous_fragment_type)
            if is_participants_list:
                self.logger.debug('MATCH - {Participants List} found.')
                current_fragment_type = FragmentType.PARTICIPANTS_LIST
                break

            is_annex = self.pdf_filter.is_annex(page_txt)
            if is_annex:
                self.logger.debug('MATCH - {Annex} found.')
                current_fragment_type = FragmentType.ANNEX
                self.annex_found = True
                break

            # Remove any contents found within tables
            # TODO: keep text from table to identify potential "section" (e.g. Summary or Annex)
            # TODO: make the actual definition of what is a "table" clearer!
            self.pdf_filter.filter_text_tables(page_txt)
            if page_cells and self.filter_tables:
                if self.minx0 and self.maxx1:  # TODO: should not be necessary, something else is wrong !
                    self.pdf_filter.filter_notes(page_txt, page_cells, self.minx0, self.maxx1)
                self.pdf_filter.filter_tables(page_txt, page_cells)

            # Default: plain simple text
            if self.annex_found:
                current_fragment_type = FragmentType.ANNEX
            else:
                current_fragment_type = FragmentType.TEXT
            break

        self.logger.debug('Exit page validation')

        if coord:
            previous_fragment_txt = self.get_previous_fragment_text(page_txt, coord)
            next_fragment_txt = self.get_next_fragment_text(page_txt, coord)
            self.add_fragment(previous_fragment_txt, fragment_type=previous_fragment_type)
            self.add_fragment(next_fragment_txt, fragment_type=current_fragment_type)
        else:
            fragment_txt = self.get_fragment_text(page_txt)
            if current_fragment_type is FragmentType.TEXT:
                fragment_txt = self.strip_paragraph_numbers(fragment_txt)
                fragment_txt = self.strip_page_number(fragment_txt)
                fragment_txt = self.strip_header(fragment_txt)
            self.add_fragment(fragment_txt, fragment_type=current_fragment_type)

        return current_fragment_type

    def add_fragment(self, fragment_txt, fragment_type):
        content_list = list()
        # TODO: investigate problematic page continuation (i.e. page 10) for french document: JT03366982
        ptrn_continued = re.compile('^(?<!\n)([a-zéèêçàù]|[A-Z]{2,})', re.UNICODE)
        # TODO: add all french capitalized accentuated
        ptrn_punct = re.compile('([\.]+|[\?!:])', re.UNICODE)
        ptrn_useless_crlf = re.compile('(?<!\.)\n(?![A-Z][a-z])', re.UNICODE)

        if _log_level > 1:
            self.logger.debug('[add_fragment] Fragment type:{type}'.format(type=fragment_type))

        if fragment_type is FragmentType.TEXT or fragment_type is FragmentType.SUMMARY:
            fragment_txt = self.remove_empty_lines(fragment_txt)
            self.logger.debug('fragment length: {l}'.format(l=len(fragment_txt)))
            for i, p in enumerate(fragment_txt):
                if _log_level > 1:
                    self.logger.debug(u'[START] {i}th sentence: {p}'.format(i=i, p=p))
                p = re.sub(ptrn_useless_crlf, ' ', p)
                p = re.sub(' +', ' ', p)
                p = re.sub('^\s*', '', string=p)
                p = p.strip()
                if not len(p):
                    self.logger.debug('nothing left...')
                    continue
                if self.previous_p:
                    if re.match(ptrn_continued, p[0]) and fragment_type is not FragmentType.SUMMARY:
                        if _log_level > 1:
                            self.logger.debug(u'continued. p[0]:{p}'.format(p=p))
                            self.logger.debug(u'adding previous. :{p}'.format(p=self.previous_p))
                        self.previous_p = self.previous_p + ' ' + p
                        continue
                    else:
                        if _log_level > 1:
                            self.logger.debug(u'not continued. p[0]:{p}'.format(p=p))
                            self.logger.debug(u'adding leftover. :{p}'.format(p=self.previous_p))
                        # if self.previous_p[:-1] != '.':
                        #     self.previous_p += '.'
                        content_list.append(self.previous_p)
                        self.previous_p = p
                else:
                    if _log_level > 2:
                        self.logger.debug('p[-1]: '+p[:-1])
                    if re.match('[.!?]]', p[-1]):
                        content_list.append(p)
                        self.previous_p = None
                    else:
                        self.previous_p = p
                    continue

                # Only for last of page and first of next page...(i.e. if there are notes, we're screwed!!!)
                if i == (len(fragment_txt)-1) and not re.match(ptrn_punct, p[-1]) and not re.match('[0-9]+ \w+.*', p):
                    if _log_level > 1:
                        self.logger.debug(u'not finished. p[0]:{p}'.format(p=p))
                    self.previous_p = p
                    continue
                else:
                    if _log_level > 2:
                        self.logger.debug(u'[END] i != len(fragment_txt)-1 ? ==> {i} != {l} ?'.format(i=i, l=len(fragment_txt)-1))
                        self.logger.debug(u'[END] match(ptrn_punct): {m}'.format(m=re.match(ptrn_punct, p[-1])))
                        self.logger.debug(u'[END] match(ptrn_start_with_number): {m}'.format(m=re.match('[0-9]+ \w+.*', p)))
                        self.logger.debug(u'[END] {i}th sentence: {p}'.format(i=i, p=p))
                    content_list.append(p)
                    self.previous_p = None

                # content_list.append(p)
        else:
            for p in fragment_txt:
                p = re.sub('(?<!\.)\n(?![A-Z])', ' ', p)
                p = re.sub(' +', ' ', p)
                p = p.strip()
                if not len(p):
                    continue
                content_list.append(p)

        if fragment_type not in self.contents:
            self.contents[fragment_type] = content_list
        else:
            self.contents[fragment_type].extend(content_list)

    def add_text_content(self, fragment_txt, fragment_type):
        content_list = list()
        content_list.append(fragment_txt)

        if fragment_type not in self.contents:
            self.contents[fragment_type] = content_list
        else:
            self.contents[fragment_type].extend(content_list)

    def extract_object_text_hash(self, h, lt_obj):
        # TODO: strange behaviour to investigate: see Summary section of JT03380961
        global text_def
        x0 = lt_obj.bbox[0]
        y0 = lt_obj.bbox[1]
        x1 = lt_obj.bbox[2]
        y1 = lt_obj.bbox[3]
        if _log_level > 1:
            self.logger.debug('[x0={x0}, y0={y0}, x1={x1}, y1={y1}]:\n {s}'.format(x0=x0, y0=y0, x1=x1, y1=y1,
                                                                                   s=to_bytestring(lt_obj.get_text())))
        if _log_level > 2:
            text_def.write('{x0}|{y0}|{x1}|{y1}|{s}\n'.format(x0=x0, y0=y0, x1=x1, y1=y1,
                                                              s=to_bytestring(lt_obj.get_text().replace('\n', ' '))))
        h[(x0, y0, x1, y1)] = lt_obj.get_text()
        return h

    def strip_paragraph_numbers(self, fragment_txt):
        filter_paragraph_lead_numbers = re.compile('((^|\n)([0-9]+\.)+[0-9]{0,3}\W?)')
        filter_paragraph_inserted_numbers = re.compile('((?<=\n)\W?([0-9]+\.)+(?![A-Z]))')
        for i, txt in enumerate(fragment_txt):
            txt = txt.strip()
            # remove paragraph numbers, e.g. "23."
            # sometimes wrongly inserted within the text from incorrect layout analysis
            result = re.sub(filter_paragraph_lead_numbers, ' ', txt)
            result = re.sub(filter_paragraph_inserted_numbers, ' ', result)
            if _log_level > 2:
                self.logger.debug(u'[strip_paragraph_numbers] regexp on [{substring}]'.format(substring=txt))
                self.logger.debug(u'[strip_paragraph_numbers] result: [{result}]'.format(result=result))
            fragment_txt[i] = result
        return fragment_txt

    def strip_header(self, fragment_txt):
        ptrn_classif = re.compile('^\W*For Official Use\W*$|'
                                  '^\W*Confidential\W*$|'
                                  '^\W*Unclassified\W*$|'
                                  '^\W*A Usage Officiel\W*$|'
                                  '^\W*Confidentiel\W*$|'
                                  '^\W*Non classifi.{1,2}\W*$|'
                                  '^\W*Diffusion Restreinte\W*$|'
                                  '^\W*Restricted Diffusion\W*$|'
                                  '^\W*Restricted\W*$|'
                                  '^\W*general distribution\W*$', re.IGNORECASE)
        ptrn_cote = re.compile('^\W*([A-Z]+?[\(\)/0-9]+[A-Z]*?)+\W*$')

        classif_idx = None
        for i, txt in enumerate(fragment_txt):
            txt = txt.strip()
            if len(txt) == 0:
                continue
            # if re.search(ptrn_cote, txt) or re.search(ptrn_classif, txt):
            if re.search(ptrn_cote, txt):
                self.logger.debug(u'found header {txt} at index: {i}'.format(txt=txt, i=i))
                self.logger.debug(u'cote pattern match: {m}'.format(m=re.search(ptrn_cote, txt).string))
                continue
            elif re.search(ptrn_classif, txt):
                self.logger.debug(u'found header {txt} at index: {i}'.format(txt=txt, i=i))
                self.logger.debug(u'classif pattern match: {m}'.format(m=re.search(ptrn_classif, txt).string))
                continue
            else:
                classif_idx = i
                break
        if classif_idx:
            fragment_txt = fragment_txt[classif_idx:]
        return fragment_txt

    def strip_classification(self, fragment_txt):
        """
        Remove classification
        :param fragment_txt:
        :return:
        """
        ptrn_classif = re.compile('For Official Use|Confidential|Unclassified|A Usage Officiel|'
                                  'Confidentiel|Non classifié', re.IGNORECASE)
        classif_idx = None
        for i, txt in enumerate(fragment_txt):
            txt = txt.strip()
            if re.search(ptrn_classif, txt):
                self.logger.debug('found classification at index: {i}'.format(i=i))
                classif_idx = i
                break
            if len(txt) > 0:
                break  # only strip out the first occurrence of classification before any actual text
        if classif_idx is not None:
            fragment_txt = fragment_txt[classif_idx+1:]
        return fragment_txt

    def strip_cote(self, fragment_txt):
        """
        Remove cote and any preceding empty strings
        :param fragment_txt:
        :return:
        """
        # ptrn_cote = re.compile('[\w]+/[[\w/]+]?\(\d{2,4}\)\d*.*|[\w]+\(\d{2,4}\)\d*.*')
        ptrn_cote = re.compile('([\w]+?[\(\)/0-9]+[\w]*?)+')
        cote_idx = None
        for i, txt in enumerate(fragment_txt):
            txt = txt.strip()
            if re.search(ptrn_cote, txt):
                self.logger.debug('found cote at index: {i}'.format(i=i))
                cote_idx = i
                break
            if len(txt) > 0:
                break  # only strip out the first occurrence of a cote before any actual text
        if cote_idx is not None:
            fragment_txt = fragment_txt[cote_idx+1:]
            if _log_level > 1:
                self.logger.debug('Fragment without cote is: {frag}'.format(frag=fragment_txt))
        return fragment_txt

    def strip_page_number(self, fragment_txt):
        """
        Remove page number and any trailing empty strings
        :param fragment_txt:
        :return:
        """
        page_number_idx = None
        for i in range(len(fragment_txt)-1, 0, -1):
            txt = fragment_txt[i].strip()
            if re.match('\s*?\d+\s*?', txt):
                self.logger.debug(u'found page number at index: {i} text:{t}'.format(i=i, t=txt))
                page_number_idx = i
                break
            if len(txt) > 0:
                break  # only strip out the first occurrence of a number before any actual text
        fragment_txt = fragment_txt[:page_number_idx]
        return fragment_txt

    def re_order_text(self, txt):
        txt = sorted(txt)
        if _log_level > 1:
            self.logger.debug('-' * 20)
            self.logger.debug('Sorted page text:')
            self.logger.debug('-' * 20)
            for elem in txt:
                self.logger.debug('{elem}'.format(elem=elem))
        return [str_array for _, _, str_array in txt]
        # return (str_array for _, _, str_array in txt)

    def remove_empty_lines(self, fragment_txt):
        result = list()
        for p in fragment_txt:
            p = re.sub(' +', ' ', p)
            p = p.strip()
            if len(p):
                result.append(p)
        return result

    def get_fragment_text(self, page_txt):
        txt = [(round(-coord[1], 0), round(coord[0], 0), str_array)
               for coord, str_array in page_txt.items()]
        return self.re_order_text(txt)

    def get_previous_fragment_text(self, page_txt, split_coord):
        txt = [(round(-coord[1], 0), round(coord[0], 0), str_array)
               for coord, str_array in page_txt.items() if coord[1] > split_coord[1]]
        return self.re_order_text(txt)

    def get_next_fragment_text(self, page_txt, split_coord):
        txt = [(round(-coord[1], 0), round(coord[0], 0), str_array)
               for coord, str_array in page_txt.items() if coord[1] <= split_coord[1]]
        return self.re_order_text(txt)


def to_bytestring(s, enc='utf-8'):
        """Convert the given unicode string to a bytestring, using the standard encoding,
        unless it's already a bytestring"""
        if s:
            if isinstance(s, str):
                return s
            else:
                return s.encode(enc)


if __name__ == '__main__':
    pass
