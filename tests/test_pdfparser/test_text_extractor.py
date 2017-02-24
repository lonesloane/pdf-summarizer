# -*- coding: utf8 -*-
import logging
import unittest

import pdfparser.text_extractor as extractor
from pdfparser.pdf_fragment_type import FragmentType


class TextExtractorTestCase(unittest.TestCase):

    def test_clean_fragment(self):
        fragment_text = list()
        fragment_text.append("Pays membres du Centre de développement et membres de l’OCDE : Allemagne, Autriche, Belgique, Chili, \nCorée,  Danemark,  Espagne,  Finlande,  France,  Irlande,  Islande,  Israël,  Italie,  Luxembourg,  Mexique, \nNorvège,  Pays-Bas,  Pologne,  Portugal,  République  slovaque,  République  tchèque,  Royaume-Uni,  Suède, \nSuisse et Turquie.   \n")
        fragment_text.append("3  \n")
        fragment_text.append("Pays  membres  du  Centre  de  développement  non  membres  de  l’OCDE :  Brésil  (mars  1994) ;  Inde (février \n2001) ;  Panama  (juillet  2013) ;  Roumanie  (octobre  2004) ;  Thaïlande  (mars  2005) ;  Afrique  du  Sud \n(mai 2006) ;  Égypte  et  Vietnam  (mars  2008) ;  Colombie  (juillet  2008) ;  Indonésie  (février 2009) ;  Costa \nRica,  Maurice,  Maroc  et  Pérou  (mars  2009) ;  République  dominicaine  (novembre  2009),  Sénégal  (février \n2011) ; et Argentine et Cap-Vert (mars 2011).   \n")
        fragment_text.append("L’Union européenne participe également au Comité directeur du Centre. \n")
        fragment_text.append(" \n")
        fragment_text.append("3 \n")
        fragment_text.append(" \n")
        self.assertEquals(len(fragment_text), 7)

        fragment_text = extractor.PDFTextExtractor().strip_page_number(fragment_text)

        self.assertEquals(len(fragment_text), 5)
        self.assertEquals(" \n", fragment_text[4])
        self.assertEquals("L’Union européenne participe également au Comité directeur du Centre. \n", fragment_text[3])

    def test_strip_cote(self):
        fragment_text = list()
        fragment_text.append(" \n")
        fragment_text.append("C(2014)151 \n")
        fragment_text.append(" \n")
        fragment_text.append(" \n")
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné le « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")

        self.assertEquals(len(fragment_text), 5)

        fragment_text = extractor.PDFTextExtractor().strip_cote(fragment_text)

        self.assertEquals(len(fragment_text), 3)
        self.assertEquals(" \n", fragment_text[1])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné le « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
                          fragment_text[2])

    @unittest.skip('deprecated method')
    def test_is_cote(self):
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
        for cote in cotes:
            self.assertTrue(extractor.is_cote(cote), 'Cote not correctly identified: [{cote}]'.format(cote=cote))

        self.assertFalse(extractor.is_cote("This is not a cote"))

    def test_strip_classification(self):
        fragment_text = list()
        fragment_text.append(" \n")
        fragment_text.append("CONFIDENTIAL \n")
        fragment_text.append(" \n")
        fragment_text.append(" \n")
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")

        self.assertEquals(len(fragment_text), 5)

        fragment_text = extractor.PDFTextExtractor().strip_classification(fragment_text)

        self.assertEquals(len(fragment_text), 3)
        self.assertEquals(" \n", fragment_text[1])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
                          fragment_text[2])

        fragment_text = list()
        fragment_text.append(" \n")
        fragment_text.append("CONFIDENTIAL \n")
        fragment_text.append(" \n")
        fragment_text.append(" \n")
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")
        fragment_text.append("CONFIDENTIAL \n")
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")

        self.assertEquals(len(fragment_text), 7)

        fragment_text = extractor.PDFTextExtractor().strip_classification(fragment_text)

        self.assertEquals(len(fragment_text), 5)
        self.assertEquals(" \n", fragment_text[1])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
        fragment_text[2])
        self.assertEquals("CONFIDENTIAL \n", fragment_text[3])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
        fragment_text[4])


    def test_re_order_text(self):
        txt = list()
        txt.append((0, 1, "0:1"))
        txt.append((1, 0, "1:0"))
        txt.append((1, 1, "1:1"))
        txt.append((2, 0, "2:0"))
        txt.append((2, 1, "2:1"))
        txt.append((-2, 2, "-2:2"))
        txt.append((0, 0, "0:0"))
        txt.append((0, 2, "0:2"))
        txt.append((1, -2, "1:-2"))
        actual = extractor.PDFTextExtractor().re_order_text(txt)
        expected = ['-2:2', '0:0', '0:1', '0:2', '1:-2', '1:0', '1:1', '2:0', '2:1']
        self.assertListEqual(actual, expected)

    def test_get_fragment_text(self):
        page_txt = dict()
        page_txt[(0, 1)] = "0:1"
        page_txt[(1, 0)] = "1:0"
        page_txt[(1, 1)] = "1:1"
        page_txt[(2, 0)] = "2:0"
        page_txt[(2, 1)] = "2:1"
        page_txt[(2, 2)] = "2:2"
        page_txt[(0, 0)] = "0:0"
        page_txt[(0, 2)] = "0:2"
        page_txt[(1, 2)] = "1:2"
        actual = extractor.PDFTextExtractor().get_fragment_text(page_txt)
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)

    def test_get_previous_fragment_text(self):
        page_txt = dict()
        page_txt[(0, 1)] = "0:1"
        page_txt[(1, 0)] = "1:0"
        page_txt[(1, 1)] = "1:1"
        page_txt[(2, 0)] = "2:0"
        page_txt[(2, 1)] = "2:1"
        page_txt[(2, 2)] = "2:2"
        page_txt[(0, 0)] = "0:0"
        page_txt[(0, 2)] = "0:2"
        page_txt[(1, 2)] = "1:2"
        actual = extractor.PDFTextExtractor().get_previous_fragment_text(page_txt, (2, 0))
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1']
        self.assertListEqual(expected, actual)
        actual = extractor.PDFTextExtractor().get_previous_fragment_text(page_txt, (2, 1))
        expected = ['0:2', '1:2', '2:2']
        self.assertListEqual(expected, actual)
        actual = extractor.PDFTextExtractor().get_previous_fragment_text(page_txt, (2, 2))
        expected = []
        self.assertListEqual(expected, actual)
        actual = extractor.PDFTextExtractor().get_previous_fragment_text(page_txt, (2, -1))
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)

    def test_get_next_fragment_text(self):
        page_txt = dict()
        page_txt[(0, 1)] = "0:1"
        page_txt[(1, 0)] = "1:0"
        page_txt[(1, 1)] = "1:1"
        page_txt[(2, 0)] = "2:0"
        page_txt[(2, 1)] = "2:1"
        page_txt[(2, 2)] = "2:2"
        page_txt[(0, 0)] = "0:0"
        page_txt[(0, 2)] = "0:2"
        page_txt[(1, 2)] = "1:2"
        actual = extractor.PDFTextExtractor().get_next_fragment_text(page_txt, (2, 0))
        expected = ['0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)
        actual = extractor.PDFTextExtractor().get_next_fragment_text(page_txt, (2, 1))
        expected = ['0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)
        actual = extractor.PDFTextExtractor().get_next_fragment_text(page_txt, (2, 2))
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)
        actual = extractor.PDFTextExtractor().get_next_fragment_text(page_txt, (2, -1))
        expected = []
        self.assertListEqual(expected, actual)

    @unittest.skip('Not yet implemented')
    def test_extract_object_text_hash(self):
        self.assertTrue(False)

    def test_add_fragment_debug(self):
        fragment_text = list()
        fragment_text.append("Representatives of other international organisations, including UNCTAD, UNESCO and IUCN,")
        fragment_text.append("were invited to intervene and report about their activities as appropriate during the meeting.")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        print 'text: {t}'.format(t=text)
        self.assertEquals(1, len(text))
        self.assertEquals('Representatives of other international organisations, including UNCTAD, UNESCO and IUCN, '
                          'were invited to intervene and report about their activities as appropriate during the meeting.', text[0])

    def test_add_fragment(self):
        fragment_text = list()
        fragment_text.append("A complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        fragment_text.append("Another incomplete sentence")
        fragment_text.append("also continued. And followed by another complete sentence.")
        fragment_text.append("And the final sentence.")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        print 'text: {t}'.format(t=text)
        self.assertEquals(4, len(text))
        self.assertEquals('An incomplete sentence continued in the next fragment.', text[1])
        self.assertEquals('Another incomplete sentence also continued. And followed by another complete sentence.', text[2])
        self.assertEquals('And the final sentence.', text[3])

        fragment_text.append("Should also work if the final punctuation is not a dot!!!")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(5, len(text))
        self.assertEquals('Should also work if the final punctuation is not a dot!!!', text[4])

        fragment_text.append("Should also work if the final punctuation is not a dot...")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(6, len(text))
        self.assertEquals('Should also work if the final punctuation is not a dot...', text[5])

        fragment_text.append("Should also work if the final punctuation is not a dot?")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(7, len(text))
        self.assertEquals('Should also work if the final punctuation is not a dot?', text[6])
        '''
        fragment_text.append("Should also work if the final fragment is incomplete")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(8, len(text))
        self.assertEquals('Should also work if the final fragment is incomplete', text[7])
        '''

    def test_add_fragment_over_pages(self):
        fragment_text = list()
        fragment_text.append("A complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        fragment_text.append("Another incomplete sentence")
        fragment_text.append("also continued. And followed by another complete sentence.")
        fragment_text.append("And the last sentence")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        print 'text: {t}'.format(t=text)
        self.assertEquals(3, len(text))
        self.assertEquals('Another incomplete sentence also continued. And followed by another complete sentence.', text[2])

        fragment_text = list()
        fragment_text.append("is now a complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(5, len(text))
        self.assertEquals('And the last sentence is now a complete sentence.', text[3])

    def test_validate_page(self):
        self.assertTrue(False, 'not yet implemented')

    def test_add_text_content(self):
        self.assertTrue(False, 'not yet implemented')

    def test_remove_empty_lines(self):
        self.assertTrue(False, 'not yet implemented')

    def test_strip_paragraph_numbers(self):
        fragment_text = list()
        fragment_text.append(u'La nature est un temple')
        fragment_text.append(u'Où de vivants piliers')
        fragment_text.append(u'Laissent parfois sortir')
        fragment_text.append(u'De confuses paroles')
        txt = extractor.PDFTextExtractor().strip_paragraph_numbers(fragment_txt=fragment_text)

        self.assertEqual(4, len(txt))
        self.assertEqual(u'La nature est un temple', txt[0])
        self.assertEqual(u'Où de vivants piliers', txt[1])
        self.assertEqual(u'Laissent parfois sortir', txt[2])
        self.assertEqual(u'De confuses paroles', txt[3])

        fragment_text = list()
        fragment_text.append(u'1. La nature est un temple')
        fragment_text.append(u'2. Où de vivants piliers')
        fragment_text.append(u'3. Laissent parfois sortir')
        fragment_text.append(u'4. De confuses paroles')
        txt = extractor.PDFTextExtractor().strip_paragraph_numbers(fragment_txt=fragment_text)

        self.assertEqual(4, len(txt))
        self.assertEqual(u' La nature est un temple', txt[0])
        self.assertEqual(u' Où de vivants piliers', txt[1])
        self.assertEqual(u' Laissent parfois sortir', txt[2])
        self.assertEqual(u' De confuses paroles', txt[3])

    def test_strip_header(self):
        fragment_text = list()
        fragment_text.append(u'CONFIDENTIAL \n')
        fragment_text.append(u'CTPA/CFA/WP1/NOE2(2014)36/CONF \n')
        fragment_text.append(u'any disclosure of taxpayer information by a competent authority to the members of the arbitration \npanel  would  be  made  pursuant  to  the  authority  of  the  Convention  and  subject  to  confidentiality \nrequirements  that  are  at  least  as  strong  as  those  applicable  to  the  competent  authorities.  An \nexpress provision in the text of the Convention itself, with a cross-reference to Article 26, would \nensure the legal status of the arbitrators. \n')
        fragment_text.append(u'\uf02d  The Commentary on Article 25 could provide additional relevant guidance, noting the practice of \nsome  competent  authorities  (i)  to  request  that  taxpayers  authorise  the  disclosure  of  relevant \ninformation to the arbitrators and (ii) to require that the arbitrators and their staffs agree in writing \nto  maintain  the  confidentiality  of  the  information  they  receive  in  the  course  of  the  arbitration \nprocess  (subject  only  to  further  disclosure  in  accordance  with  the  requirements  and  further \nauthorisation of the competent authorities and the affected taxpayers). \n')
        fragment_text.append(u'\uf02d  The Commentary on Article 25 could also note the practice of some countries to oblige taxpayers \nand their representatives to maintain confidentiality regarding arbitration in a MAP case,  subject \nto  any  necessary  disclosures  such  as  for  financial  reporting  purposes,  with  a  view  to  avoiding \npotential taxpayer manipulation of the MAP arbitration process. \n')
        fragment_text.append(u'\uf0b7  Form  of  process  for  decision.  There  are  two  principal  approaches  to  decision-making  in  the \narbitration process. The format most commonly used in commercial matters is the \u201cconventional\u201d \nor  \u201cindependent  opinion\u201d  approach,  in  which  the  arbitrators  are  presented  with  the  facts  and \narguments of the parties based on applicable law and then reach an independent decision, typically \nin the form of a written, reasoned analysis. This approach strongly resembles a judicial proceeding \nand is the model for the EU Arbitration Convention as well as the default approach reflected in the \nSample Mutual Agreement on Arbitration (the Sample Agreement) included in the Commentary on \nArticle  25  of  the  OECD  Model.  The  other  main  format  is  the  \u201clast  best  offer\u201d  or  \u201cFinal  Offer\u201d \napproach  (often  informally  referred  to  as  \u201cbaseball  arbitration\u201d).  This  approach  is  reflected  in  a \nnumber  of  bilateral  tax  treaties  signed  by  OECD  member  countries.  Under  this  approach,  in \ngeneral,  each  of  the  competent  authorities  submits  to  the  arbitration  panel  a  proposed  resolution \n(i.e. its proposed disposition of the specific amounts of income, expense or taxation at issue in the \nMAP case), together with a position paper that explains the rationale for the proposed resolution. \nThe  arbitration  panel  is  required  to  adopt  as  its  determination  one  of  the  proposed  resolutions \nsubmitted by the competent authorities. The determination by the arbitration panel does not state a \nrationale and has no precedential value. Based on experience with both approaches to arbitration, it \nappears  that  the  time  and  resources  required  to  set  up,  organise  and  use  Final  Offer  MAP \narbitration  may  be  significantly  less  than  with  the  independent  opinion  MAP  arbitration.  In \naddition, it is also not apparent that the reasoned opinions developed in the MAP cases dealt with \nusing the independent opinion approach would have any particular utility (e.g. as precedent for the \nresolution of future MAP cases). \n')
        txt = extractor.PDFTextExtractor().strip_header(fragment_txt=fragment_text)
        self.assertEqual(4, len(txt))

        fragment_text = list()
        fragment_text.append(u'Le  projet  utilisera  aussi  largement  des  données  quantitatives  issues  de  sources  internationales (Regards sur l’éducation, NESLI, PIAAC, PISA, TALIS ou d’autres sources provenant de pays non membres de l’OCDE), de sources nationales tirées des rapports de base, et de données issues du projet ITEL.')
        txt = extractor.PDFTextExtractor().strip_header(fragment_txt=fragment_text)
        self.assertEqual(1, len(txt))

    def test_strip_page_number(self):
        fragment_text = list()
        fragment_text.append(u'La nature est un temple')
        fragment_text.append(u'Où de vivants piliers')
        fragment_text.append(u'Laissent parfois sortir')
        fragment_text.append(u'De confuses paroles')
        fragment_text.append(u'1')
        self.assertEqual(5, len(fragment_text))

        txt = extractor.PDFTextExtractor().strip_page_number(fragment_txt=fragment_text)

        self.assertEqual(4, len(txt))
        self.assertEqual(u'La nature est un temple', txt[0])
        self.assertEqual(u'Où de vivants piliers', txt[1])
        self.assertEqual(u'Laissent parfois sortir', txt[2])
        self.assertEqual(u'De confuses paroles', txt[3])

        fragment_text = list()
        fragment_text.append(u'La nature est un temple')
        fragment_text.append(u'Où de vivants piliers')
        fragment_text.append(u'Laissent parfois sortir')
        fragment_text.append(u'De confuses paroles')
        fragment_text.append(u'1')
        fragment_text.append(u'L homme y passe au travers')
        fragment_text.append(u'Des forêts de symoles')
        fragment_text.append(u'Qui parlent à son ame')
        fragment_text.append(u'En termes familiers')
        fragment_text.append(u'2')
        self.assertEqual(10, len(fragment_text))

        txt = extractor.PDFTextExtractor().strip_page_number(fragment_txt=fragment_text)

        self.assertEqual(9, len(txt))

        self.assertEqual(u'La nature est un temple', txt[0])
        self.assertEqual(u'En termes familiers', txt[8])

    def test_should_force_raw_extraction(self):

        pdf_extractor = extractor.PDFTextExtractor()
        expected = True
        actual = pdf_extractor.should_force_raw_extraction()
        self.assertEqual(expected, actual)

        pdf_extractor = extractor.PDFTextExtractor(single_page=1)
        expected = False
        actual = pdf_extractor.should_force_raw_extraction()
        self.assertEqual(expected, actual)

        pdf_extractor = extractor.PDFTextExtractor()
        contents = dict()
        contents[FragmentType.TEXT] = "This is the text..."
        pdf_extractor.contents = contents
        expected = False
        actual = pdf_extractor.should_force_raw_extraction()
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
