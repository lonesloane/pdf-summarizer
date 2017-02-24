# -*- coding: utf8 -*-
import re

from pdfparser import _log_level, _config
import pdfparser.table_edges_extractor as table_extractor
import pdfparser.text_table_extractor as text_table_extractor
from pdfparser.pdf_fragment_type import FragmentType
from pdfparser.report import Report
from pdfparser.text_table_extractor import Cell, compare_cells

X0, Y0, X1, Y1 = 0, 1, 2, 3


class PDFPageFilter:
    """

    """

    def __init__(self, report=None, logger=None):
        """

        :param report:
        """
        if not logger:
            from pdfparser import logger
        self.logger = logger
        self.__TEXT_MIN_FRACTION_SIZE = _config.getfloat('MAIN', 'TEXT_MIN_FRACTION_SIZE')
        self.__MIN_NUMBER_ROWS = _config.getfloat('MAIN', 'MIN_NUMBER_ROWS')
        self.__MIN_NUMBER_COLS = _config.getfloat('MAIN', 'MIN_NUMBER_COLS')
        self.__PAGE_Y_MIN = _config.getfloat('MAIN', 'PAGE_Y_MIN')
        self.__PAGE_Y_MAX = _config.getfloat('MAIN', 'PAGE_Y_MAX')

        self.report = report if report else Report()
        self.tables_text = list()

    def is_cover(self, page_txt):
        """

        :param page_txt:
        :return:
        """
        nb_match = 0
        for _, fragment in page_txt.items():
            txt = fragment.strip()
            # Cote
            nb_match += self.match_cote(txt)
            # Classification
            nb_match += self.match_classification(txt)
            # OECD
            nb_match += self.match_oecd(txt)
            # OCDE
            nb_match += self.match_ocde(txt)

            if nb_match > 2:
                self.report.cover_page = 1
                return True
        return False

    def match_ocde(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_ocde = re.compile('Organisation de Coop.{1,2}ration et de D.{1,2}veloppement .{1,2}conomiques'
                               '|Forum International des Transports|'
                               'Conf.{1,2}rence Europ.{1,2}enne des Ministres des Transports|'
                               'Organisations Coordonn.{1,2}es')
        ptrn_ocde_telex = re.compile(('.*ORGANISATION DE COOP.{1,2}RATION.*\s?.*'
                                  'ET DE D.{1,2}VELOPPEMENT .{1,2}CONOMIQUES.*'),
                                 re.MULTILINE)
        ptrn_ocde_telex_start = re.compile('.*ORGANISATION DE COOP.{1,2}RATION.*\s?.*')
        ptrn_ocde_telex_end = re.compile('.*ET DE D.{1,2}VELOPPEMENT .{1,2}CONOMIQUES.*')
        if re.search(ptrn_ocde, txt) or re.search(ptrn_ocde_telex, txt):
            self.logger.debug(u'OCDE found: {frag}'.format(frag=txt))
            return 1
        elif re.search(ptrn_ocde_telex_start, txt) or re.search(ptrn_ocde_telex_end, txt):
            self.logger.debug(u'OCDE part found: {frag}'.format(frag=txt))
            return 0.5
        else:
            return 0

    def match_oecd(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_oecd = re.compile('Organisation for Economic Co-operation and Development'
                               '|International Transport Forum|'
                               'European Conference of Ministers of Transport|'
                               'Co-ordinated Organisations')
        ptrn_oecd_telex = re.compile('.*ORGANISATION FOR ECONOMIC.*\s?.*CO.*?OPERATION AND DEVELOPMENT.*',
                                     re.MULTILINE)
        ptrn_oecd_telex_start = re.compile('.*ORGANISATION FOR ECONOMIC.*\s?.*')
        ptrn_oecd_telex_end = re.compile('.*CO.*?OPERATION AND DEVELOPMENT.*')
        if re.search(ptrn_oecd, txt) or re.search(ptrn_oecd_telex, txt):
            self.logger.debug(u'OECD found: {frag}'.format(frag=txt))
            return 1
        elif re.search(ptrn_oecd_telex_start, txt) or re.search(ptrn_oecd_telex_end, txt):
            self.logger.debug(u'OECD part found: {frag}'.format(frag=txt))
            return 0.5
        else:
            return 0

    def match_classification(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_classif = re.compile('[^a-zA-Z0-9_]?For Official Use[^a-zA-Z0-9_]?'
                                  '|[^a-zA-Z0-9_]?Confidential[^a-zA-Z0-9_]?|'
                                  '[^a-zA-Z0-9_]?Unclassified[^a-zA-Z0-9_]?|'
                                  '[^a-zA-Z0-9_]?A Usage Officiel[^a-zA-Z0-9_]?'
                                  '[^a-zA-Z0-9_]?|Confidentiel[^a-zA-Z0-9_]?|'
                                  '[^a-zA-Z0-9_]?Non classifi.{1,2}[^a-zA-Z0-9_]?|'
                                  '[^a-zA-Z0-9_]?Diffusion Restreinte[^a-zA-Z0-9_]?|'
                                  '[^a-zA-Z0-9_]?Restricted Diffusion[^a-zA-Z0-9_]?'
                                  '|[^a-zA-Z0-9_]?Restricted[^a-zA-Z0-9_]?'
                                  '|[^a-zA-Z0-9_]?general distribution[^a-zA-Z0-9_]?')
        if re.search(ptrn_classif, txt):
            self.logger.debug(u'Classification found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    def match_cote(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_cote = re.compile('([A-Z]+?[\(\)/0-9]+[A-Z]*?)+  # e.g. AGP/HR/VAC(94)5', re.VERBOSE)

        if re.search(ptrn_cote, txt):
            self.logger.debug(u'Cote found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    def is_summary(self, page_txt):
        """

        Sample documents:
            - '2014/11/03/JT03365426.pdf'
        :param page_txt:
        :return:
        """
        for _, fragment in page_txt.items():
            txt = fragment.strip()
            if self.match_summary(txt):
                self.report.summary = 1
                return True
        else:
            return False

    def match_summary(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_summary = re.compile('^\s*?SUMMARY\s*?$|'
                                  '^\s*?ABSTRACT\s*?$|'
                                  '^\s*?R.{1,2}SUM.{1,2}\s*?$|'
                                  '\s*?ABSTRACT/R.{1,2}SUM.{1,2}\s*?$|'
                                  '^\s*?EXECUTIVE SUMMARY\s*?$|'
                                  '^\s*?SUMMARY\s{0,2}/\s{0,2}ACTION REQUIRED\s*?$', re.IGNORECASE)

        if re.search(ptrn_summary, txt):
            self.logger.debug(u'Summary "Title" found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    def is_toc(self, page_txt, current_fragment_type):
        """

        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        # TODO: improve to handle situation where text follows toc on same page (see IMP19901498FRE)
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()

            if self.match_toc_title(fragment) or self.match_toc_exact(fragment):
                self.report.toc = 1
                return True

            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                continue

            # if regexp matches and previous page was already 'Table of Content'
            # then assume this is the continuation of 'Table of Content'
            nb += len(self.match_toc_continued(fragment))
            if nb > 2 and current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                self.logger.debug(u'T.O.C. continuation found')
                self.report.toc = 1  # TODO: useful? Maybe toc += 1 to keep track of the number of pages in the t.o.c.?
                return True

        else:
            return False

    def match_toc_title(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_toc_title = re.compile('TABLE OF CONTENTS|TABLE DES MATI.{1,2}RES|SOMMAIRE')  # Expected text in uppercase
        if re.search(ptrn_toc_title, txt):
            self.logger.debug(u'T.O.C. "Title" found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    def match_toc_exact(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_toc_exact = re.compile('Table des mati.{1,2}res')  # Expected text in lowercase
        if re.search(ptrn_toc_exact, txt):
            self.logger.debug(u'T.O.C. "Title" found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    def match_toc_continued(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_toc_cont = re.compile('([\.]{10,}?\s[0-9]{1,4})')
        return re.findall(ptrn_toc_cont, txt)

    def is_glossary(self, page_txt, current_fragment_type):
        """

        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()

            if self.match_glossary_title(fragment):
                self.report.glossary = 1
                return True

            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.GLOSSARY:
                continue

            nb += len(self.match_glossary_structure(fragment))
            if nb > 5:
                self.logger.debug(u'Glossary continuation found.')
                self.report.glossary = 1
                return True

        else:
            return False

    def match_glossary_title(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_glossary_title = re.compile('^\W*?LIST OF ABBREVIATIONS|'
                                         '^\W*?GLOSSARY|'
                                         '^\W*?Glossary\W*?$|'
                                         '^\W*?LIST OF ACRONYMS|'
                                         '^\W*?Abbreviations\s*?$|'
                                         '^[\W\w]*?ACRONYMES\s*?$')
        if re.search(ptrn_glossary_title, txt):
            self.logger.debug(u'Glossary "Title" found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    @classmethod
    def match_glossary_structure(cls, txt):
        """

        :param txt:
        :return:
        """
        # Some examples of patterns usually found in glossaries:
        # "ATM – Agriculture Trade and Markets division of TAD"
        # "COAG – Committee for Agriculture of the OECD"
        ptrn_glossary_struct = re.compile('(?:[A-Z]{3,10}\s+?–\s+?[A-Z])')
        return re.findall(ptrn_glossary_struct, txt)

    def is_bibliography(self, page_txt, current_fragment_type):
        """

        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        # TODO: either improve regexp (case sensitive?)
        # or detect that text initially came from a table (see JT03366941 page 49)
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if self.match_bibliography_title(fragment):
                self.report.bibliography = 1
                return True, coord
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.BIBLIOGRAPHY:
                continue
            # if regexp matches and previous page was already 'Bibliography'
            # then assume this is the continuation of 'Bibliography'.
            nb += len(self.match_bibliography_structure(fragment))
            if nb > 2:
                self.logger.debug(u'Bibliography "pattern" found.')
                self.report.bibliography = 1
                return True, None
        else:
            return False, None

    def match_bibliography_title(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_biblio = re.compile('^\s*?bibliograph(y|ie)\s*?$|'
                                 '^\s*?r.{1,2}f.{1,2}rence(?:s)?\s*?$|'
                                 '^\s*?lit(?:t)?erature\s*?$', re.IGNORECASE)
        if re.search(ptrn_biblio, txt):
            self.logger.debug(u'Bibliography "Title" found: {frag}'.format(frag=txt))
            return 1
        else:
            return 0

    def match_bibliography_structure(self, txt):
        """

        :param txt:
        :return:
        """
        # Some examples of patterns usually found in bibliographies:
        # "Baumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis”, American"
        # "OECD (2010c), The OECD Innovation Strategy: Getting a Head Start on Tomorrow, Paris: OECD."
        ptrn_biblio_cont = re.compile('((?:[A-Z].*[A-Z])?(?:OECD)?.*\([0-9]{4}.*\).*)')
        return re.findall(ptrn_biblio_cont, txt)

    def is_participants_list(self, page_txt, current_fragment_type):
        """

        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        nb_names, nb_emails = 0, 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()

            if self.match_participants_title(fragment):
                self.logger.debug(u'participants title found. {frag}'.format(frag=fragment))
                return True, coord

            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                continue

            # if regexp matches and previous page was already 'Participants List'
            # then assume this is the continuation of 'Participants List'.
            nb_names += len(self.match_participants_names(fragment))
            if nb_names > 2 and current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                self.logger.debug(u'continued participants found. nb: {nb}'.format(nb=nb_names))
                self.report.participants_list = 1
                return True, coord

            nb_emails += len(self.match_participants_emails(fragment))
            if nb_emails > 2 and current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                self.logger.debug(u'continued participants found. nb: {nb}'.format(nb=nb_emails))
                self.report.participants_list = 1
                return True, coord
        else:
            return False, None

    def match_participants_title(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_part_exact_1 = re.compile('Participants list|LIST OF PARTICIPANTS|Liste des participants',
                                       re.IGNORECASE)
        ptrn_part_exact_2 = re.compile('^\W*?PRESENT(S)?\W*?$')
        ptrn_part_find_1 = re.compile('(List of Participants|Liste des Participants) ?/ ?(Liste des Participants'
                                      '|List of Participants|List of Presence)', re.IGNORECASE)
        ptrn_part_find_2 = re.compile('LIST OF PARTICIPANTS')
        if re.match(ptrn_part_exact_1, txt):
            self.logger.debug(u'participants section title found. Match:{match}'.format(match='ptrn_part_exact_1'))
            return True
        elif re.match(ptrn_part_exact_2, txt):
            self.logger.debug(u'participants section title found. Match:{match}'.format(match='ptrn_part_exact_2'))
            return True
        elif re.search(ptrn_part_find_1, txt):
            self.logger.debug(u'participants section title found. Match:{match}'.format(match='ptrn_part_find_1'))
            return True
        elif re.search(ptrn_part_find_2, txt):
            self.logger.debug(u'participants section title found. Match:{match}'.format(match='ptrn_part_find_2'))
            return True
        else:
            return False

    def match_participants_names(self, txt):
        """

        :param txt:
        :return:
        """
        # "Mr. Christian HEDERER, Counsellor for Energy, Trade, Industry and Science"
        # "Ms. Maria-Antoinetta SIMONS, Permanent Delegation of Belgium to the OECD"
#        ptrn_participants_names = re.compile('(?:M[r]?|Mme|M[i|r]?s[s]?|Dr)\.?(?: [[A-Z][a-z\s]*?]*? [A-Z ]+)')
        ptrn_participants_names = re.compile('(?:M[r]?|Mme|M[i|r]?s[s]?|Dr)'
                                             '\.?'
                                             '(?: [A-Z][a-z\s]*?[- ]?[[A-Z][a-z\s]*?]? ?[A-Z ]+)')
        return re.findall(ptrn_participants_names, txt)

    def match_participants_emails(self, txt):
        """

        :param txt:
        :return:
        """
        # "j.a.f.vandewijnboom@minez.nl\n"
        # "skowalczyk@ijhars.gov.pl \n"
        # "dkrzyzanowska@ijhars.gov.pl \n"
        # "dbalinska@ijhars.gov.pl\n"
        # "aszymanska@ijhars.gov.pl\n"
        # 'Marta.Dziubiak@minrol.gov.pl\n'
        ptrn_participants_emails = re.compile('\w*?\.?\w*@\w*\.\w*')
        return re.findall(ptrn_participants_emails, txt)

    def is_annex(self, page_txt):
        """

        :param page_txt:
        :return:
        """
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if self.match_annex_title(fragment):
                self.report.annex = 1
                return True
        else:
            return False

    def match_annex_title(self, txt):
        """

        :param txt:
        :return:
        """
        ptrn_annex = re.compile('^\W*ANNEX(E)?\s*[0-9]?[A-Z]?\.?\s*$|'
                                '^\W*ANNEX(E)?\s*[0-9]?[A-Z]?\.?\s*?-?\s*?:?[\W\w]*?$|'
                                '^\W*Annex(e)?\s{1,2}[0-9]?[a-z]?\s*$|'
                                '^\W*APPENDI(X|CE)\s*[0-9]?[A-Z]?\s*$|'
                                '^\s*TECHNICAL ANNEX\s*$|'
                                '^\s*FIGURE AND TABLE ANNEX\s*$')
        if re.search(ptrn_annex, txt):
            return True
        else:
            return False

    def filter_text_tables(self, page_txt):
        """

        :param page_txt:
        :return:
        """
        if _log_level > 1:
            self.logger.debug('[Enter filter_text_tables]')

        text_cells = [Cell(x0, y0, x1, y1) for x0, y0, x1, y1 in page_txt.keys()]
        text_cells.sort(key=compare_cells, reverse=True)

        if _log_level > 1:
            self.logger.debug('text cells\n{tc}'.format(tc=text_cells))

        outer_edges = text_table_extractor.find_table_cells(text_cells) if len(text_cells) > 1 else []

        '''
        if _log_level > 1:
            self.logger.debug('outer edges\n{oe}'.format(oe=outer_edges))
            self.logger.debug(u'nb candidate cells found: {nb}'.format(nb=len(outer_edges)))
            self.logger.debug(u'Before table filtering, length of page text:{len}'.format(len=len(page_txt)))
        '''

        #if len(outer_edges):
        for cell in outer_edges:
            if _log_level > 1:
                self.logger.debug((u'removing cell: {cell.x0} {cell.y0} {cell.x1} {cell.y1} - {c}')
                             .format(cell=cell, c=page_txt[(cell.x0, cell.y0, cell.x1, cell.y1)]))
            page_txt.pop((cell.x0, cell.y0, cell.x1, cell.y1))

        if _log_level > 1:
            self.logger.debug(u'After table filtering, length of page text:{len}'.format(len=len(page_txt)))

        if _log_level > 1:
            self.logger.debug('[Exit filter_text_tables]')

    def filter_tables(self, page_txt, page_cells):
        """

        :param page_txt:
        :param page_cells:
        :return:
        """
        if _log_level > 1:
            self.logger.debug('[Enter filter_tables]')
            self.logger.debug(u'nb cells: {nb}'.format(nb=len(page_cells)))

        outer_edges = table_extractor.find_outer_edges(page_cells) if len(page_cells) > 1 else []

        if _log_level > 1:
            self.logger.debug(u'nb candidate tables found: {nb}'.format(nb=len(outer_edges)))

        if len(outer_edges) > 0:
            # Consider only tables with at least MIN_NUMBER_ROWS and MIN_NUMBER_COLS
            outer_edges = [table for table in outer_edges if table.rows > self.__MIN_NUMBER_ROWS and
                           table.columns > self.__MIN_NUMBER_COLS]

        if len(outer_edges) > 0:
            self.report.tables = 1

            if _log_level > 1:
                self.logger.info('\nMATCH - {Table} found.')
                self.logger.debug(u'Found {ntables} actual tables on page'.format(ntables=len(outer_edges)))

                for table in outer_edges:
                    self.logger.debug(table)
                    self.logger.debug(u'{nrows} inner rows and {ncolumns} inner columns'.format(nrows=table.rows,
                                                                                           ncolumns=table.columns))
                self.logger.debug(u'Before table filtering, length of page text:{len}'.format(len=len(page_txt)))

            for coord, _ in page_txt.items():
                # cell_content = page_txt[coord].strip()
                if self.text_is_within_table(coord, outer_edges):
                    page_txt.pop(coord)
                    # cell_content = self.filter_number(cell_content)
                    # cell_content = self.filter_repetition(cell_content)
                    # page_txt[coord] = cell_content
            if _log_level > 1:
                self.logger.debug(u'After table filtering, length of page text:{len}'.format(len=len(page_txt)))
        if _log_level > 1:
            self.logger.debug('[Exit filter_tables]')

    def filter_notes(self, page_txt, cells, min_text_x0, max_text_x1):
        """
        Filter out the text found "below" the notes separator
        :param page_txt:
        :param cells:
        :param min_text_x0:
        :param max_text_x1:
        :return:
        """
        if _log_level > 1:
            self.logger.debug('[Enter filter_notes]')
            self.logger.debug(u'nb cells: {nb}'.format(nb=len(cells)))

        # Figure out if one of the cells is the "notes separator"
        separator = None
        text_width = abs(max_text_x1 - min_text_x0)
        leftmost_cell_found = False
        for cell in sorted(cells, cmp=lambda c1,c2: int(c1.y0 - c2.y0), reverse=False):
            self.logger.debug('[Searching separator] '
                         'cell: {c} - '
                         'minx0: {min} - '
                         'cell width: {w} - '
                         'text_width: {tw} - '
                         'width percentage: {p}'.format(c=cell, w=cell.width, min=min_text_x0, tw=text_width,
                                                        p=cell.width/text_width))
            if cell.x0 <= min_text_x0:
                leftmost_cell_found = True
                if text_width * 0.10 < cell.width < text_width * 0.33 \
                        and cell.y1 < (self.__PAGE_Y_MAX - self.__PAGE_Y_MIN) * .33:
                        # TODO: extract separator "minimum" and maximum width to config file
                    # TODO: include a "maximum" position in the page for the separator
                    # TODO: TEST!!! Make sure to avoid false positives
                    self.logger.debug(u'Notes separator found: {c}'.format(c=cell))
                    separator = cell
                    break
            if leftmost_cell_found :
                break

        if separator:
            for coord, _ in page_txt.items():
                if self.text_below_notes_separator(coord, separator):
                    self.logger.debug(u'Stripping out note: {n}'.format(n=page_txt[coord]))
                    page_txt.pop(coord)

    def filter_repetition(self, cell_content):
        """

        :param cell_content:
        :return:
        """
        cell_content = cell_content.strip()
        # remove inner line breaks
        cell_content = cell_content.replace('\n', ' ')

        if cell_content in self.tables_text:
            if _log_level > 1:
                self.logger.debug(u'[Table inner text] - repetition found: {txt}'.format(txt=cell_content))
            return ''
        else:
            if _log_level > 2:
                self.logger.debug(u'{txt} not found yet'.format(txt=cell_content, tt=self.tables_text))
            self.tables_text.append(cell_content)
            return cell_content

    def filter_number(self, cell_content):
        """

        :param cell_content:
        :return:
        """
        cell_content = cell_content.strip()
        if _log_level > 2:
            self.logger.debug(u'Looking if {txt} is a number'.format(txt=cell_content))

        if re.match('^\s*?[0-9\.,]+\s*?$', cell_content):
            if _log_level > 1:
                self.logger.debug(u'[Table inner text] - number found: {nb}'.format(nb=cell_content))
            return ''
        else:
            if _log_level > 1:
                self.logger.debug(u'[Table inner text] - not a number.')
            return cell_content

    def text_is_within_table(self, coord, outer_edges):
        """

        :param coord:
        :param outer_edges:
        :return:
        """
        for cell in outer_edges:
            if cell.contains(coord) and cell.is_fraction(coord):
                if _log_level > 1:
                    self.logger.debug(u'Text cell {text_cell} inside table.'.format(text_cell=coord))
                return True
        else:
            self.logger.debug(u'Text cell not contained in table, or not a fraction of table')
            return False

    def text_below_notes_separator(self, coord, separator):
        """

        :param coord:
        :param separator:
        :return:
        """
        if coord[Y0] < separator.y0:
            self.logger.debug('cell below sepratator - [{x0}|{y0}|{x1}|{y1}]'.format(x0=coord[X0],
                                                                                y0=coord[Y0],
                                                                                x1=coord[X1],
                                                                                y1=coord[Y1]))
            return True
        return False

if __name__ == '__main__':
    pass