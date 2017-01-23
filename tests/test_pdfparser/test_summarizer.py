# -*- coding: utf8 -*-
import logging
import unittest

from pdfparser.summarizer import remove_repetition, PDFSummarizer


class SummarizerTestCase(unittest.TestCase):

    def test_generate_summary(self):
        with open('pdf_sample.txt', mode='rb') as pdf_text:
            text = pdf_text.readlines()
            text = [line.decode('utf-8') for line in text]

        summary = PDFSummarizer().generate_summary(pdf_sentences=text)

        self.assertEqual(15, len(summary))
        s = summary.pop()
        self.assertEqual(s._text, 'Finance Ministers thus have a key role in ensuring financial resilience, a critical component of effective')

    def test_remove_repetition(self):
        text = list()
        text.append('La nature est un temple')
        text.append('Ou de vivants piliers')
        text.append('Laissent parfois sortir')
        text.append('De confuses paroles.')
        text.append('La nature est un temple')
        text.append('Ou de vivants piliers')
        text.append('Laissent parfois sortir')
        text.append('De confuses paroles.')

        self.assertEqual(8, len(text))

        text = remove_repetition(text)

        self.assertEqual(4, len(text))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
