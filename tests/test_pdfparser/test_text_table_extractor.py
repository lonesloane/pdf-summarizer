import logging
import unittest

from pdfparser.text_table_extractor import Cell, Row, Table


class CellTestCase(unittest.TestCase):

    def test_absorb(self):
        eating_cell = Cell(0, 0, 10, 10)
        print eating_cell

        expected_width = 10
        expected_height = 10
        actual_width = eating_cell.get_width()
        actual_heigth = eating_cell.get_height()
        self.assertEqual(expected_height, actual_heigth)
        self.assertEqual(expected_width, actual_width)

        eaten_cell = Cell(2, 2, 4, 4)
        eating_cell.absorb(eaten_cell)
        print eating_cell
        expected_width = 10
        expected_height = 10
        actual_width = eating_cell.get_width()
        actual_heigth = eating_cell.get_height()
        self.assertEqual(expected_height, actual_heigth)
        self.assertEqual(expected_width, actual_width)

        eaten_cell = Cell(2, 2, 14, 24)
        eating_cell.absorb(eaten_cell)
        print eating_cell
        expected_width = 14
        expected_height = 24
        actual_width = eating_cell.get_width()
        actual_heigth = eating_cell.get_height()
        self.assertEqual(expected_height, actual_heigth)
        self.assertEqual(expected_width, actual_width)

    def test_get_width(self):
        cell = Cell(0, 0, 10, 10)
        self.assertEqual(10, cell.get_width())
        cell = Cell(5, 0, 18, 10)
        self.assertEqual(13, cell.get_width())

    def test_get_height(self):
        cell = Cell(0, 0, 10, 10)
        self.assertEqual(10, cell.get_height())
        cell = Cell(0, 5, 10, 22)
        self.assertEqual(17, cell.get_height())


class RowTestCase(unittest.TestCase):

    def test_add_cell(self):
        row = Row()
        self.assertIsNone(row.max_y)
        self.assertIsNone(row.min_y)
        self.assertEquals(0, len(row.cells))

        cell = Cell(0, 0, 10, 10)
        row.add_cell(cell)
        self.assertEqual(10, row.max_y)
        self.assertEqual(0, row.min_y)
        self.assertEquals(1, len(row.cells))

        cell = Cell(-10, -5.0, 10, 20)
        row.add_cell(cell)
        self.assertEqual(20, row.max_y)
        self.assertEqual(-5.0, row.min_y)
        self.assertEquals(2, len(row.cells))

    def test_update_boundaries(self):
        row = Row()
        row.max_y = 10
        row.min_y = 0

        cell = Cell(-10, -5.0, 10, 20)
        row.update_boundaries(cell)
        self.assertEqual(20, row.max_y)
        self.assertEqual(-5.0, row.min_y)

        cell = Cell(-10, -5.0, 10, 15)
        row.update_boundaries(cell)
        self.assertEqual(20, row.max_y)
        self.assertEqual(-5.0, row.min_y)

        cell = Cell(-10, -15.0, 10, 25)
        row.update_boundaries(cell)
        self.assertEqual(25, row.max_y)
        self.assertEqual(-15.0, row.min_y)

    def test_included(self):
        row = Row()
        row.max_y = 10
        row.min_y = 0

        cell = Cell(-10, 5.0, 10, 8)
        self.assertTrue(row.included(cell))

        cell = Cell(-10, -5.0, 10, 20)
        self.assertFalse(row.included(cell))

    def test_aligned(self):
        row = Row()
        row.max_y = 10
        row.min_y = 0

        cell = Cell(-10, 5.0, 10, 8)
        self.assertTrue(row.aligned(cell))

        cell = Cell(-10, 50, 10, 70)
        self.assertFalse(row.aligned(cell))


class TableTestCase(unittest.TestCase):

    def test_create(self):
        table = Table()
        self.assertIsNotNone(table.cells)
        self.assertIsNotNone(table.rows)
        self.assertEqual(0, len(table.cells))
        self.assertEqual(0, len(table.rows))

    def test_add_row(self):
        table = Table()

        row = Row()
        cell = Cell(-10, 5.0, 10, 8)
        row.add_cell(cell)
        cell = Cell(-10, 5.0, 10, 8)
        row.add_cell(cell)

        table.add_row(row)

        self.assertEqual(1, len(table.rows))
        self.assertEqual(2, len(table.cells))

    def test_add_cells(self):
        table = Table()

        self.assertEqual(0, len(table.cells))
        row = Row()
        cell = Cell(-10, 5.0, 10, 8)
        row.add_cell(cell)
        table.add_cells(row)
        self.assertEqual(1, len(table.cells))
        table.add_cells(row)
        self.assertEqual(2, len(table.cells))

    def test_update_boundaries(self):
        table = Table()
        self.assertIsNone(table.min_y)
        self.assertIsNone(table.max_y)

        cell = Cell(-10, -5.0, 10, 20)
        table.update_boundaries(cell)
        self.assertEqual(20, table.max_y)
        self.assertEqual(-5.0, table.min_y)

        cell = Cell(-10, -5.0, 10, 15)
        table.update_boundaries(cell)
        self.assertEqual(20, table.max_y)
        self.assertEqual(-5.0, table.min_y)

        cell = Cell(-10, -15.0, 10, 25)
        table.update_boundaries(cell)
        self.assertEqual(25, table.max_y)
        self.assertEqual(-15.0, table.min_y)

    def test_included(self):
        table = Table()
        table.min_y = 0
        table.min_y = 50

        cell = Cell(x0=0, y0=0, x1=0, y1=0)
        self.assertFalse(table.included(cell))

        cell = Cell(x0=0, y0=10, x1=0, y1=20)
        self.assertFalse(table.included(cell))

    def test_candidate_cells(self):
        page_width = 100
        table = Table()

        cells = table.candidate_cells(page_width=page_width)
        self.assertIsNotNone(cells)
        self.assertEqual(0, len(cells))

        row = Row()
        row.add_cell(Cell(x0=0, y0=0, x1=10, y1=10))
        row.add_cell(Cell(x0=0, y0=0, x1=10, y1=10))
        row.add_cell(Cell(x0=10, y0=0, x1=80, y1=80))
        table.add_row(row)

        row = Row()
        row.add_cell(Cell(x0=0, y0=0, x1=10, y1=10))
        row.add_cell(Cell(x0=0, y0=0, x1=10, y1=10))
        row.add_cell(Cell(x0=10, y0=0, x1=80, y1=80))
        table.add_row(row)

        row = Row()
        row.add_cell(Cell(x0=0, y0=0, x1=10, y1=10))
        row.add_cell(Cell(x0=0, y0=0, x1=10, y1=10))
        row.add_cell(Cell(x0=10, y0=0, x1=80, y1=80))
        print Cell(x0=10, y0=0, x1=80, y1=80).get_width()
        table.add_row(row)

        cells = table.candidate_cells(page_width=page_width)
        self.assertIsNotNone(cells)
        i = 0
        for cell in cells:
            i += 1
        self.assertEqual(6, i)


class TextTableExtractorTestCase(unittest.TestCase):

    def test_find_table_cells(self):
        self.fail("Not implemented")

    def test_compare_cells(self):
        self.fail("Not implemented")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
