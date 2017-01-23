import logging
import unittest
import pdfparser.table_edges_extractor as extractor


class EdgesExtractorTestCase(unittest.TestCase):

    def test_cell_is_fraction(self):
        cell = extractor.Cell(10.0, 20.0, 30.5, 40.5)
        coord = [1.0, 2.0, 3.0, 4.0]
        self.assertTrue(cell.is_fraction(coord))
        coord = [10.0, 15.0, 30.5, 35.0]
        self.assertFalse(cell.is_fraction(coord))

    def test_cell_contains(self):
        cell = extractor.Cell(1.0, 2.0, 3.5, 4.5)
        coord = [1.0, 2.0, 3.0, 4.0]
        self.assertTrue(cell.contains(coord))
        coord = [1.0, 2.0, 3.5, 5.0]
        self.assertFalse(cell.contains(coord))

    def test_adjacent(self):
        # TODO: fix this! The test depends on the hard coded value of ADJ_DISTANCE!!!
        # extractor.ADJ_DISTANCE
        self.assertTrue(extractor.adjacent(25.0, 24.1))
        self.assertTrue(extractor.adjacent(25.0, 25.9))
        self.assertFalse(extractor.adjacent(25.0, 24.0))
        self.assertFalse(extractor.adjacent(25.0, 26.0))

    def test_same_cell(self):
        cell1 = extractor.Cell(1.0, 2.0, 3.5, 4.5)
        cell2 = extractor.Cell(1.0, 2.0, 3.5, 4.5)
        self.assertTrue(extractor.same_cell(cell1, cell2))
        cell3 = extractor.Cell(1.0, 2.0, 3.5, 4.0)
        self.assertFalse(extractor.same_cell(cell1, cell3))

    def test_collapse_west(self):
        cell1 = extractor.Cell(3.0, 1.0, 6.0, 5.0, rows=1, columns=2)
        cell2 = extractor.Cell(1.0, 3.0, 3.0, 6.0, rows=2, columns=1)
        collapsed = extractor.collapse_west(cell1, cell2)

        self.assertEqual(1.0, collapsed.x0)
        self.assertEqual(1.0, collapsed.y0)
        self.assertEqual(6.0, collapsed.x1)
        self.assertEqual(6.0, collapsed.y1)
        self.assertEqual(2, collapsed.rows)
        self.assertEqual(2, collapsed.columns)

    def test_collapse_east(self):
        cell1 = extractor.Cell(1.0, 3.0, 5.0, 8.0, rows=2, columns=1)
        cell2 = extractor.Cell(5.0, 2.0, 8.0, 3.0, rows=1, columns=2)
        collapsed = extractor.collapse_east(cell1, cell2)

        self.assertEqual(1.0, collapsed.x0)
        self.assertEqual(2.0, collapsed.y0)
        self.assertEqual(8.0, collapsed.x1)
        self.assertEqual(8.0, collapsed.y1)
        self.assertEqual(2, collapsed.rows)
        self.assertEqual(3, collapsed.columns)

    def test_collapse_south(self):
        cell1 = extractor.Cell(3.0, 2.0, 6.0, 5.0, rows=1, columns=2)
        cell2 = extractor.Cell(1.0, 1.0, 5.0, 4.0, rows=2, columns=1)
        collapsed = extractor.collapse_south(cell1, cell2)

        self.assertEqual(1.0, collapsed.x0)
        self.assertEqual(1.0, collapsed.y0)
        self.assertEqual(6.0, collapsed.x1)
        self.assertEqual(5.0, collapsed.y1)
        self.assertEqual(3, collapsed.rows)
        self.assertEqual(2, collapsed.columns)

    def test_collapse_north(self):
        cell1 = extractor.Cell(1.0, 1.0, 5.0, 4.0, rows=2, columns=1)
        cell2 = extractor.Cell(3.0, 2.0, 6.0, 5.0, rows=1, columns=2)
        collapsed = extractor.collapse_north(cell1, cell2)

        self.assertEqual(1.0, collapsed.x0)
        self.assertEqual(1.0, collapsed.y0)
        self.assertEqual(6.0, collapsed.x1)
        self.assertEqual(5.0, collapsed.y1)
        self.assertEqual(3, collapsed.rows)
        self.assertEqual(2, collapsed.columns)

    def test_collapse_overlapping(self):
        cell1 = extractor.Cell(1.0, 1.0, 4.0, 5.0, rows=2, columns=1)
        cell2 = extractor.Cell(2.0, 2.0, 5.0, 5.0, rows=1, columns=2)
        collapsed = extractor.collapse_overlapping(cell1, cell2)

        self.assertEqual(1.0, collapsed.x0)
        self.assertEqual(1.0, collapsed.y0)
        self.assertEqual(5.0, collapsed.x1)
        self.assertEqual(5.0, collapsed.y1)
        self.assertEqual(3, collapsed.rows)
        self.assertEqual(3, collapsed.columns)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
