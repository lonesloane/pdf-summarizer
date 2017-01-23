import logging
import unittest
import test_pdfparser.test_table_edges_extractor as table_extractor
import test_pdfparser.test_text_extractor as text_extractor
import test_pdfparser.test_pdf_page_filter as pdf_page_filter
import test_pdfparser.test_summarizer as summarizer
import test_pdfparser.test_text_table_extractor as text_table_extractor

suite_table_extractor = unittest.TestLoader().loadTestsFromModule(table_extractor)
suite_text_extractor = unittest.TestLoader().loadTestsFromModule(text_extractor)

suite_pdf_page_filter = unittest.TestLoader().loadTestsFromModule(pdf_page_filter)
suite_summarizer = unittest.TestLoader().loadTestsFromModule(summarizer)
suite_text_table_extractor = unittest.TestLoader().loadTestsFromModule(text_table_extractor)

all_tests = unittest.TestSuite([suite_table_extractor,suite_text_extractor, suite_pdf_page_filter, suite_summarizer,
                                suite_text_table_extractor])

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.TextTestRunner().run(all_tests)
