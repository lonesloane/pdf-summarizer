# -*- coding: utf8 -*-
import logging
import unittest

import pdfparser.pdf_page_filter as filter
from pdfparser.pdf_fragment_type import FragmentType
import pdfparser.table_edges_extractor as table_extractor


class PdfPageFilterTestCase(unittest.TestCase):

    def test_is_cover(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_2 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_3 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_0
        page_txt[2] = txt_0
        page_txt[3] = txt_0

        expected = False
        actual = filter.PDFPageFilter().is_cover(page_txt=page_txt)
        self.assertEqual(expected, actual)

        cote = 'CTPA/CFA/WP10(2011)39/CONF'
        classif = 'For Official Use'
        oecd = u'Organisation for Economic Co-operation and Development'
        ocde = u'Organisation de Coopération et de Développement économiques'

        page_txt[4] = cote
        page_txt[5] = classif

        expected = False
        actual = filter.PDFPageFilter().is_cover(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[4] = cote
        page_txt[5] = classif
        page_txt[6] = oecd

        expected = True
        actual = filter.PDFPageFilter().is_cover(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[4] = cote
        page_txt[5] = classif
        page_txt[6] = ocde

        expected = True
        actual = filter.PDFPageFilter().is_cover(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[4] = cote
        page_txt[5] = classif
        page_txt[6] = ocde
        page_txt[7] = oecd

        expected = True
        actual = filter.PDFPageFilter().is_cover(page_txt=page_txt)
        self.assertEqual(expected, actual)

    def test_match_ocde(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        txt = ''
        expected = 0
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Organisation de Coopération et de Développement économiques'
        expected = 1
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Forum International des Transports'
        expected = 1
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Conférence Européenne des Ministres des Transports'
        expected = 1
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Organisations Coordonnées'
        expected = 1
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'ORGANISATION DE COOPÉRATION'
        expected = 0.5
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'ET DE DÉVELOPPEMENT ÉCONOMIQUES'
        expected = 0.5
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'ORGANISATION DE COOPÉRATION ET DE DÉVELOPPEMENT ÉCONOMIQUES'
        expected = 1
        actual = filter.PDFPageFilter().match_ocde(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

    def test_match_oecd(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        txt = ''
        expected = 0
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Organisation for Economic Co-operation and Development'
        expected = 1
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'International Transport Forum'
        expected = 1
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'European Conference of Ministers of Transport'
        expected = 1
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Co-ordinated Organisations'
        expected = 1
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'ORGANISATION FOR ECONOMIC'
        expected = 0.5
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'COOPERATION AND DEVELOPMENT'
        expected = 0.5
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'ORGANISATION FOR ECONOMIC COOPERATION AND DEVELOPMENT'
        expected = 1
        actual = filter.PDFPageFilter().match_oecd(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

    def test_match_classification(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        txt = ''
        expected = 0
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'For Official Use'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'Confidential'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'Unclassified'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'A Usage Officiel'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'Confidentiel'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Non classifié'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'Diffusion Restreinte'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'Restricted Diffusion'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'Restricted'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'general distribution'
        expected = 1
        actual = filter.PDFPageFilter().match_classification(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'any disclosure of taxpayer information by a competent authority to the members of the arbitration \n' \
              u'panel  would  be  made  pursuant  to  the  authority  of  the  Convention  and  subject  to  ' \
              u'confidentiality \nrequirements  that  are  at  least  as  strong  as  those  applicable  to  the  ' \
              u'competent  authorities.  An \nexpress provision in the text of the Convention itself, with a ' \
              u'cross-reference to Article 26, would \nensure the legal status of the arbitrators. \n'
        expected = 0
        actual = filter.PDFPageFilter().match_classification(txt)
        self.assertEqual(expected, actual, "Shouldn't match classification pattern")

    def test_match_cote(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        txt = ''
        expected = 0
        actual = filter.PDFPageFilter().match_cote(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        cotes = list()
        cotes.append("C(2014)151 \n")
        cotes.append("EXD/INT/D(2001)30 \n")
        cotes.append("NEA/CRPPH(2001)2 \n")
        cotes.append("AGP/HR/VAC(94)5 \n")
        cotes.append("AGR/CA(94)12 \n")
        cotes.append("AGP/GRD/DOC(95)89 \n")
        cotes.append("AGP/HR/VAC(95)8 \n")
        cotes.append("AGP/CONF/D(96)65 \n")
        cotes.append("AGR/FI(97)2 \n")
        cotes.append("CTPA/CFA/WP6/NOE2(2016)3/REV2 \n")
        cotes.append("DCD/DAC/A(2016)5 \n")
        cotes.append("ENV/EPOC(2016)9 \n")
        cotes.append("ENV/WKP(2016)8 \n")
        cotes.append("CTPA/CFA/TFDE/NOE2(2015)10/REV4/CONF \n")
        cotes.append("DAF/COMP/LACF(2015)8 \n")
        cotes.append("DAF/INV/STAT/ACS/A(2015)1 \n")
        cotes.append("NEA/NDC(2015)4 \n")
        cotes.append("DAF/INV/CMF/AS/ATFC(2014)6/FINAL \n")
        cotes.append("CES/PE(2014)4 \n")
        cotes.append("DSTI/EAS/STP/NESTI(2014)11 \n")
        cotes.append("CTPA/CFA/BP/M(2013)1/REV1/CONF \n")
        cotes.append("DAF/COMP/GF/WD(2014)7 \n")
        cotes.append("TAD/PR/II(2012)5/REV \n")
        cotes.append("DELSA/ELSA(2012)9 \n")
        cotes.append("NEA/COM(2012)4 \n")
        cotes.append("GOV/TDPC/URB/A(2012)1 \n")
        cotes.append("EXD/OPS/IMSD/DOC(2012)229 \n")
        cotes.append("ITF/TMB/TR/M(2009)3 \n")
        cotes.append("CTPA/CFA/WP10(2011)39/CONF \n")
        cotes.append("DCD(2000)7 \n")
        cotes.append('DAFFE/CFA/WP1(98)9/REV5/CONF \n')
        cotes.append('DAFFE/CFA/WP1/REV5/CONF \n')

        for cote in cotes:
            expected = 1
            actual = filter.PDFPageFilter().match_cote(txt_0 + cote + txt_1)
            self.assertEqual(expected, actual, 'Cote not correctly identified: [{cote}]'.format(cote=cote))

        cote = 'OLIS : 28-Jan-93\ndist. :'
        expected = 0
        actual = filter.PDFPageFilter().match_cote(cote)
        self.assertEqual(expected, actual, 'Cote not correctly identified: [{cote}]'.format(cote=cote))

    def test_match_summary(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        txt = ''
        expected = 0
        actual = filter.PDFPageFilter().match_summary(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = '\n\t  SUMMARY  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_summary(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  ABSTRACT  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_summary(txt)
        self.assertEqual(expected, actual)

        txt = u'\n\t  RÉSUMÉ  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_summary(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  EXECUTIVE SUMMARY  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_summary(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t SUMMARY / ACTION REQUIRED  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_summary(txt)
        self.assertEqual(expected, actual, txt)

    def test_is_summary(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_3 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_4 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_0
        page_txt[3] = txt_0
        page_txt[4] = txt_0

        summary = '\n\t  SUMMARY  \n'
        abstract = '\n\t  ABSTRACT \n'
        resume = u'\n\t  RÉSUMÉ \n'
        executive = '\n\t EXECUTIVE SUMMARY  \n'

        expected = False
        actual = filter.PDFPageFilter().is_summary(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = summary
        expected = True
        actual = filter.PDFPageFilter().is_summary(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = abstract
        expected = True
        actual = filter.PDFPageFilter().is_summary(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = resume
        expected = True
        actual = filter.PDFPageFilter().is_summary(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = executive
        expected = True
        actual = filter.PDFPageFilter().is_summary(page_txt=page_txt)
        self.assertEqual(expected, actual)

    def test_is_toc(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_3 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_4 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        toc = '\n\t  TABLE OF CONTENTS  \n'
        exact = u'Table des matières'
        random = 'This piece of code is really getting complicated....'
        continued_1 = u'Some random text'
        continued_2 = u'Chapter bla    ................ 23'
        continued_3 = u'Chapter blabla    ................ 23'
        continued_4 = u'Chapter blablabla    ................ 23'
        continued_5 = u'Chapter another thing altogether    ................ 23'

        expected = False
        actual = filter.PDFPageFilter().is_toc(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = toc
        expected = True
        actual = filter.PDFPageFilter().is_toc(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = exact
        expected = True
        actual = filter.PDFPageFilter().is_toc(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = random
        expected = False
        actual = filter.PDFPageFilter().is_toc(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        page_txt[5] = continued_1
        page_txt[6] = continued_2
        page_txt[7] = continued_3
        page_txt[8] = continued_4
        page_txt[9] = continued_5

        expected = True
        actual = filter.PDFPageFilter().is_toc(page_txt=page_txt, current_fragment_type=FragmentType.TABLE_OF_CONTENTS)
        self.assertEqual(expected, actual)

    def test_match_toc_title(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = filter.PDFPageFilter().match_toc_title(txt_0 + txt_1)
        self.assertEqual(expected, actual)

        txt = 'TABLE OF CONTENTS'
        expected = 1
        actual = filter.PDFPageFilter().match_toc_title(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'TABLE DES MATIERES'
        expected = 1
        actual = filter.PDFPageFilter().match_toc_title(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = 'SOMMAIRE'
        expected = 1
        actual = filter.PDFPageFilter().match_toc_title(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

    def test_match_toc_exact(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = filter.PDFPageFilter().match_toc_exact(txt_0 + txt_1)
        self.assertEqual(expected, actual)

        txt = u'table des matières'
        expected = 0
        actual = filter.PDFPageFilter().match_toc_exact(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt = u'Table des matières'
        expected = 1
        actual = filter.PDFPageFilter().match_toc_exact(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

    def test_match_toc_continued(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt += '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = len(filter.PDFPageFilter().match_toc_continued(txt))
        self.assertEqual(expected, actual)

        txt += u'table des matières'
        expected = 0
        actual = len(filter.PDFPageFilter().match_toc_continued(txt))
        self.assertEqual(expected, actual)

        txt += u'table des matières    ................ 23'
        expected = 1
        actual = len(filter.PDFPageFilter().match_toc_continued(txt))
        self.assertEqual(expected, actual)

        txt += u'table des matières    ................ 45'
        expected = 2
        actual = len(filter.PDFPageFilter().match_toc_continued(txt))
        self.assertEqual(expected, actual)

        txt += u'table des matières    ................ 54'
        expected = 3
        actual = len(filter.PDFPageFilter().match_toc_continued(txt))
        self.assertEqual(expected, actual)

    def test_is_glossary(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_3 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_4 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        loa = '\n\t  LIST OF ABBREVIATIONS  \n'
        glossary = '\n\t  GLOSSARY  \n'
        acronyms = '\n\t  LIST OF ACRONYMS  \n'
        abrev = 'Abbreviations'
        random = 'This piece of code is really getting complicated....'
        continued_1 = 'Some random text'
        continued_2 = 'ATM – Agriculture Trade and Markets division of TAD'
        continued_3 = 'COAG – Committee for Agriculture of the OECD'
        continued_4 = 'Chapter blablabla    ................ 23'
        continued_5 = 'Chapter another thing altogether    ................ 23'
        continued_6 = 'ATM – Agriculture Trade and Markets division of TAD'
        continued_7 = 'COAG – Committee for Agriculture of the OECD'
        continued_8 = 'Chapter blablabla    ................ 23'
        continued_9 = 'Chapter another thing altogether    ................ 23'
        continued_10 = 'ATM – Agriculture Trade and Markets division of TAD'
        continued_11 = 'COAG – Committee for Agriculture of the OECD'

        expected = False
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = loa
        expected = True
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = glossary
        expected = True
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = acronyms
        expected = True
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = abrev
        expected = True
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt[2] = random
        expected = False
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        page_txt[5] = continued_1
        page_txt[6] = continued_2
        page_txt[7] = continued_3
        page_txt[8] = continued_4
        page_txt[9] = continued_5
        page_txt[10] = continued_6
        page_txt[11] = continued_7
        page_txt[12] = continued_8
        page_txt[13] = continued_9
        page_txt[14] = continued_10
        page_txt[15] = continued_11

        expected = True
        actual = filter.PDFPageFilter().is_glossary(page_txt=page_txt, current_fragment_type=FragmentType.GLOSSARY)
        self.assertEqual(expected, actual)

    def test_match_glossary_title(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = filter.PDFPageFilter().match_glossary_title(txt_0 + txt_1)
        self.assertEqual(expected, actual)

        txt = '\n\t  LIST OF ABBREVIATIONS  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_glossary_title(txt + txt_1)
        self.assertEqual(expected, actual)

        txt = '\n\t  GLOSSARY  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_glossary_title(txt + txt_1)
        self.assertEqual(expected, actual)

        txt = '\n\t  Glossary  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_glossary_title(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  LIST OF ACRONYMS  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_glossary_title(txt + txt_1)
        self.assertEqual(expected, actual)

        txt = '\n\t  Abbreviations  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_glossary_title(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  SIGLES ET ACRONYMES  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_glossary_title(txt)
        self.assertEqual(expected, actual)

    def test_match_glossary_structure(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt += '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = len(filter.PDFPageFilter().match_glossary_structure(txt))
        self.assertEqual(expected, actual)

        txt += 'table of contents'
        expected = 0
        actual = len(filter.PDFPageFilter().match_glossary_structure(txt))
        self.assertEqual(expected, actual)

        txt = '\nSome random text\n'
        txt += '\nATM – Agriculture Trade and Markets division of TAD\n'
        expected = 1
        actual = len(filter.PDFPageFilter().match_glossary_structure(txt))
        self.assertEqual(expected, actual)

        # TODO: need to fix this! Looks like we will never be able to identify glossary continuation!
        txt = '\nSome random text\n'
        txt += '\nCOAG – Committee for Agriculture of the OECD\n'
        expected = 1
        actual = len(filter.PDFPageFilter().match_glossary_structure(txt))
        self.assertEqual(expected, actual)

    def test_is_bibliography(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_3 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_4 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        biblio = '\n\t  bibliography  \n'
        random = 'This piece of code is really getting complicated....'
        continued_1 = 'Some random text'
        continued_2 = 'Baumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis'
        continued_3 = 'OECD (2010c), The OECD Innovation Strategy: Getting a Head Start on Tomorrow, Paris: OECD.'
        continued_4 = 'Chapter blablabla    ................ 23'
        continued_5 = 'Chapter another thing altogether    ................ 23'
        continued_6 = 'Baumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis'
        continued_7 = 'OECD (2010c), The OECD Innovation Strategy: Getting a Head Start on Tomorrow, Paris: OECD.'
        continued_8 = 'Chapter blablabla    ................ 23'
        continued_9 = 'Chapter another thing altogether    ................ 23'
        continued_10 = 'Baumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis'
        continued_11 = 'OECD (2010c), The OECD Innovation Strategy: Getting a Head Start on Tomorrow, Paris: OECD.'

        expected = False
        actual, coord = filter.PDFPageFilter().is_bibliography(page_txt=page_txt,
                                                               current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

        page_txt[2] = biblio
        expected = True
        actual, coord = filter.PDFPageFilter().is_bibliography(page_txt=page_txt,
                                                               current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)
        self.assertEqual(2, coord)

        page_txt[2] = random
        expected = False
        actual, coord = filter.PDFPageFilter().is_bibliography(page_txt=page_txt,
                                                               current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        page_txt[5] = continued_1
        page_txt[6] = continued_2
        page_txt[7] = continued_3
        page_txt[8] = continued_4
        page_txt[9] = continued_5
        page_txt[10] = continued_6
        page_txt[11] = continued_7
        page_txt[12] = continued_8
        page_txt[13] = continued_9
        page_txt[14] = continued_10
        page_txt[15] = continued_11

        expected = True
        actual, coord = filter.PDFPageFilter().is_bibliography(page_txt=page_txt,
                                                        current_fragment_type=FragmentType.BIBLIOGRAPHY)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

    def test_match_bibliography_title(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = filter.PDFPageFilter().match_bibliography_title(txt_0 + txt_1)
        self.assertEqual(expected, actual)

        txt = '\n\t  bibliography  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_bibliography_title(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  bibliographie  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_bibliography_title(txt)
        self.assertEqual(expected, actual)

        txt = u'\n\t  référence  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_bibliography_title(txt)
        self.assertEqual(expected, actual)

        txt = u'\n\t  références  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_bibliography_title(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  litterature  \n'
        expected = 1
        actual = filter.PDFPageFilter().match_bibliography_title(txt)
        self.assertEqual(expected, actual)

    def test_match_bibliography_structure(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt += '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = len(filter.PDFPageFilter().match_bibliography_structure(txt))
        self.assertEqual(expected, actual)

        txt += 'bibliography continued'
        expected = 0
        actual = len(filter.PDFPageFilter().match_bibliography_structure(txt))
        self.assertEqual(expected, actual)

        txt = '\nSome random text\n'
        txt += '\nBaumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis\n'
        expected = 1
        actual = len(filter.PDFPageFilter().match_bibliography_structure(txt))
        self.assertEqual(expected, actual)

    def test_is_participants_list(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_3 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_4 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        presents = '\n\t  PRESENT  \n'
        random = 'This piece of code is really getting complicated....'

        expected = False
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                               current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

        page_txt[2] = presents
        expected = True
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                               current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)
        self.assertEqual(2, coord)

        page_txt[2] = random
        expected = False
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                               current_fragment_type=FragmentType.UNKNOWN)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        page_txt[5] = 'Some random text'
        page_txt[6] = 'Ms. Agustina VIERHELLER \nAssistante \nSection OCDE \nEmbassy of Argentina \n'
        page_txt[7] = '\nM. Christophe LAI \nAttach\xc3\xa9 commercial \n'
        page_txt[8] = 'Chapter blablabla    ................ 23'

        expected = False
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                        current_fragment_type=FragmentType.PARTICIPANTS_LIST)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

        page_txt[9] = 'Chapter another thing altogether    ................ 23'
        page_txt[10] = 'Dr. Tom GEERINCKX \nPolicy Advisor \nAgriculture and Fisheries Policy Division \n'
        page_txt[11] = 'Mme Carmen RODRIGUEZ MU\xc3\x91OZ \nHead of Area for Fisheries Economics \n'

        expected = True
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                        current_fragment_type=FragmentType.PARTICIPANTS_LIST)
        self.assertEqual(expected, actual)
        self.assertEqual(10, coord)

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        page_txt[5] = 'Some random text'
        page_txt[6] = '\nE-mail: Wolfgang.Zornbach@bml.bund.de'
        page_txt[7] = '\nE-mail: stephane.varin@gmail.com \n'
        page_txt[8] = 'Chapter blablabla    ................ 23'

        expected = False
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                                    current_fragment_type=FragmentType.PARTICIPANTS_LIST)
        self.assertEqual(expected, actual)
        self.assertEqual(None, coord)

        page_txt[9] = 'Chapter another thing altogether    ................ 23'
        page_txt[10] = 'mumu_varin@hotmail.fr'
        page_txt[11] = 'nicolas.vahleas@oecd.org \n'

        expected = True
        actual, coord = filter.PDFPageFilter().is_participants_list(page_txt=page_txt,
                                                                    current_fragment_type=FragmentType.PARTICIPANTS_LIST)
        self.assertEqual(expected, actual)
        self.assertEqual(10, coord)

    def test_match_participants_title(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        expected = False
        actual = filter.PDFPageFilter().match_participants_title(txt)
        self.assertEqual(expected, actual)

        txt = '\nPRESENTS\n'
        expected = True
        actual = filter.PDFPageFilter().match_participants_title(txt)
        self.assertEqual(expected, actual)

        txt = '\nLIST OF PARTICIPANTS\n'
        expected = True
        actual = filter.PDFPageFilter().match_participants_title(txt)
        self.assertEqual(expected, actual)

        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\nLorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt = 'LIST OF PARTICIPANTS'
        expected = True
        actual = filter.PDFPageFilter().match_participants_title(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\nLorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt = 'Liste des Participants / List of Participants'
        expected = True
        actual = filter.PDFPageFilter().match_participants_title(txt_0 + txt + txt_1)
        self.assertEqual(expected, actual)

        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\nLorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt = 'Liste des participants'
        expected = True
        actual = filter.PDFPageFilter().match_participants_title(txt + txt_1)
        self.assertEqual(expected, actual)

        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\nLorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt = 'Participants list'
        expected = True
        actual = filter.PDFPageFilter().match_participants_title(txt + txt_1)
        self.assertEqual(expected, actual)

    def test_match_participants_names(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt += '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += '\nMr. Christian HEDERER, Counsellor for Energy, Trade, Industry and Science\n'
        expected = 1
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += "Ms. Agustina VIERHELLER \nAssistante \nSection OCDE \nEmbassy of Argentina \n6, rue Cimarosa \n75116 Paris " \
              "\nFrance \n \nTel: +33 1 44 05 27 10 \nEmail: Vih@mrecic.gov.ar \n"
        expected = 2
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += "\nM. Christophe LAI \nAttach\xc3\xa9 commercial \nD\xc3\xa9l\xc3\xa9gation Economique de Taiwan - CAPEC " \
               "\n75 bis Avenue Marceau \n75116 Paris \nFrance \n \nTel: +33 1 56 89 81 09 \nFax: +1 56 89 81 01 \nEmail: " \
               "clai@noos.fr \n \n"
        expected = 3
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += "Miss Antonia MEI \nAttach\xc3\xa9e Commerciale \nService Economique et Commercial, Bureau de " \
               "Representation de Taipei \nen France \nCentre Asiatique de Promotion Economique et Commerciale \n(" \
               "C.A.P.E.C.) \n75bis, Avenue Marceau \n75116 Paris \nFrance \n \nTel: +33 1 56 89 81 03 \nFax: +33 1 56 89 " \
               "81 01 \nEmail: bcmei@orange.fr \n"
        expected = 4
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += "Dr. Tom GEERINCKX \nPolicy Advisor \nAgriculture and Fisheries Policy Division \nFlemish Ministry of " \
               "Agriculture \nKoning Albert II Laan 35 \n1030 Brussels \nBelgium \n \nTel: +3225527947 \nFax: +3225527921 " \
               "\nEmail: tom.geerinckx@lv.vlaanderen.be \n"
        expected = 5
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += "Mrs. Luz Maria ACEVEDO \ncollaboratrice \nD\xc3\xa9l\xc3\xa9gation Permanente de l'Espagne aupr\xc3\xa8s " \
               "de l'OCDE \n22, avenue Marceau \n75008 Paris \nFrance \n \nM. Sebastian FRAILE \nConseiller de " \
               "l'Agriculture, la P\xc3\xaache et l'Alimentation \nD\xc3\xa9l\xc3\xa9gation Permanente de l'Espagne " \
               "aupr\xc3\xa8s de l'OCDE \n22, avenue Marceau \n75008 Paris \nFrance \n \nTel: +33 1 44 43 30 19 \nFax: " \
               "+33 1 44 43 30 18 \nEmail: sfrailea@magrama.es \n"
        expected = 7
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

        txt += "Mme Carmen RODRIGUEZ MU\xc3\x91OZ \nHead of Area for Fisheries Economics \nMinistry of Agriculture, " \
               "Food and Environment \nVelazguez 147 \n28002 Madrid \nSpain \n \nTel: +34 91 347 36 94 \nFax: +34 91 347 " \
               "84 45 \nEmail: carmenr@mapya.es \n"
        expected = 8
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        self.assertEqual(expected, actual)

#        txt += '\nMr. Christian HEDERER, Counsellor for Energy, Trade, Industry and Science\n'
        txt += '\nMs. Maria-Antoinetta SIMONS, Permanent Delegation of Belgium to the OECD\n'
        expected = 9
        actual = len(filter.PDFPageFilter().match_participants_names(txt))
        print filter.PDFPageFilter().match_participants_names(txt)
        self.assertEqual(expected, actual)

    def test_match_participants_emails(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt += '\n Consulares nobilitarunt et praefecturae.'

        expected = 0
        actual = len(filter.PDFPageFilter().match_participants_emails(txt))
        self.assertEqual(expected, actual)

        txt += '\nj.a.f.vandewijnboom@minez.nl\n'
        expected = 1
        actual = len(filter.PDFPageFilter().match_participants_emails(txt))
        self.assertEqual(expected, actual)

        txt += '\nskowalczyk@ijhars.gov.pl \n\n'
        expected = 2
        actual = len(filter.PDFPageFilter().match_participants_emails(txt))
        self.assertEqual(expected, actual)

    def test_is_annex(self):
        txt_0 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        txt_1 = '\n Consulares nobilitarunt et praefecturae.'
        txt_3 = '\nEusebius vero obiecta fidentius negans, suspensus in eodem gradu constantiae stetit latrocinium.'
        txt_4 = '\nIllud esse, non iudicium clamans.'

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        annexe = '\n\t  ANNEXE  \n'
        appendix = '\n\t  APPENDIX  \n'
        random = 'This piece of code is really getting complicated....'

        expected = False
        actual = filter.PDFPageFilter().is_annex(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = annexe
        expected = True
        actual = filter.PDFPageFilter().is_annex(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = appendix
        expected = True
        actual = filter.PDFPageFilter().is_annex(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt[2] = random
        expected = False
        actual = filter.PDFPageFilter().is_annex(page_txt=page_txt)
        self.assertEqual(expected, actual)

        page_txt = dict()
        page_txt[0] = txt_0
        page_txt[1] = txt_1
        page_txt[3] = txt_3
        page_txt[4] = txt_4

        page_txt[5] = 'Some random text'
        page_txt[6] = 'FIGURE AND TABLE ANNEX'
        page_txt[8] = 'Chapter blablabla    ................ 23'

        expected = True
        actual = filter.PDFPageFilter().is_annex(page_txt=page_txt)
        self.assertEqual(expected, actual)

    def test_match_annex_title(self):
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n '
        expected = False
        actual = filter.PDFPageFilter().match_annex_title(txt)
        self.assertEqual(expected, actual)

        txt = '\n\t  ANNEXES  \n'
        expected = True
        actual = filter.PDFPageFilter().match_annex_title(txt)
        self.assertEqual(expected, actual)
        txt = '\n\t  ANNEXE 1 \n'
        expected = True
        actual = filter.PDFPageFilter().match_annex_title(txt)
        self.assertEqual(expected, actual)
        txt = '\n\t  Annexe 9a  \n'
        expected = True
        actual = filter.PDFPageFilter().match_annex_title(txt)
        self.assertEqual(expected, actual)
        txt = '\n\t  APPENDIX  \n'
        expected = True
        actual = filter.PDFPageFilter().match_annex_title(txt)
        self.assertEqual(expected, actual)

    @unittest.skip('Not yet implemented')
    def test_filter_text_tables(self):
        self.assertTrue(False, 'Not yet implemented')

    @unittest.skip('Not yet implemented')
    def test_filter_tables(self):
        self.assertTrue(False, 'Not yet implemented')

    @unittest.skip('Not yet implemented')
    def test_filter_repetition(self):
        self.assertTrue(False, 'Not yet implemented')

    @unittest.skip('Not yet implemented')
    def test_filter_number(self):
        self.assertTrue(False, 'Not yet implemented')

    def test_text_is_within_table(self):
        outer_edges = list()
        outer_edges.append(table_extractor.Cell(0.0, 0.0, 20.5, 40.5))
        outer_edges.append(table_extractor.Cell(30.0, 50.0, 60.5, 100.5))

        coord = [1.0, 2.0, 3.0, 4.0]
        expected = True
        actual = filter.PDFPageFilter().text_is_within_table(coord, outer_edges)
        self.assertEquals(expected, actual)

        coord = [1.0, 2.0, 30.0, 4.0]
        expected = False
        actual = filter.PDFPageFilter().text_is_within_table(coord, outer_edges)
        self.assertEquals(expected, actual)

        coord = [31.0, 52.0, 40.0, 70.0]
        expected = True
        actual = filter.PDFPageFilter().text_is_within_table(coord, outer_edges)
        self.assertEquals(expected, actual)

        coord = [31.0, 52.0, 55.0, 80.0]
        expected = False
        actual = filter.PDFPageFilter().text_is_within_table(coord, outer_edges)
        self.assertEquals(expected, actual)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
