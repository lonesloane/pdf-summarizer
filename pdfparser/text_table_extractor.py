
class Cell:

    def __init__(self, x0, y0, x1, y1, rows=1, columns=1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.rows = rows
        self.columns = columns
        self.width = self.get_width()
        self.height = self.get_height()

    def __repr__(self):
        return ('[x0: {self.x0}, y0: {self.y0}, x1: {self.x1}, y1: {self.y1}, '
                'rows: {self.rows}, columns: {self.columns}, '
                'width: {self.width}, height: {self.height}]'.format(self=self))

    def absorb(self, cell):
        if cell.x0 < self.x0:
            self.x0 = cell.x0
        if cell.x1 > self.x1:
            self.x1 = cell.x1
        if cell.y0 < self.y0:
            self.y0 = cell.y0
        if cell.y1 > self.y1:
            self.y1 = cell.y1

        # TODO: replace this with @property !!!
        self.width = self.get_width()
        self.height = self.get_height()

    def get_width(self):
        return abs(self.x0 - self.x1)

    def get_height(self):
        return abs(self.y0 - self.y1)


class Row:

    def __init__(self):
        self.max_y = None
        self.min_y = None
        self.cells = list()

    def add_cell(self, cell):
        self.cells.append(cell)
        self.update_boundaries(cell)

    def update_boundaries(self, cell):
        if not self.min_y or cell.y0 < self.min_y:
            self.min_y = cell.y0
        if not self.max_y or cell.y1 > self.max_y:
            self.max_y = cell.y1

    def included(self, cell):
        if cell.y0 >= self.min_y and cell.y1 <= self.max_y:
            return True
        return False

    def aligned(self, cell):
        # TODO: review this logic, seems "funky"
        if self.min_y > cell.y0 and self.min_y > cell.y1:
            return False
        if self.max_y <= cell.y0 and self.max_y <= cell.y1:  # TODO: <= or < ?
            return False
        return True


class Table:

    def __init__(self):
        self.max_y = None
        self.min_y = None
        self.cells = list()
        self.rows = list()

    def add_row(self, row):
        self.rows.append(row)
        self.add_cells(row)

    def add_cells(self, row):
        for cell in row.cells:
            self.cells.append(cell)
            self.update_boundaries(cell)

    def update_boundaries(self, cell):
        if not self.min_y or cell.y0 < self.min_y:
            self.min_y = cell.y0
        if not self.max_y or cell.y1 > self.max_y:
            self.max_y = cell.y1

    def included(self, cell):
        if cell.y0 >= self.min_y and cell.y1 <= self.max_y:
            return True
        return False

    def candidate_cells(self, page_width):
        if len(self.rows) > 2:  # TODO: extract to config file
            cells = (cell for cell in self.cells if cell.get_width() < page_width/2.5)
        else:
            cells = ()

        return cells


def find_table_cells(cells):
    # TODO: ensure cells are sorted correctly, do not assume caller has done it already !
    # TODO: implement logic based on columns in addition to rows !!!
    global_cell = None
    tables = list()
    table = Table()
    candidate_row = Row()
    for cell in cells:
        # keep track of page global dimensions
        if not global_cell:
            global_cell = Cell(cell.x0, cell.y0, cell.x1, cell.y1)
        else:
            global_cell.absorb(cell)

        # store cells into rows and rows into tables
        if len(candidate_row.cells) == 0:
            candidate_row.add_cell(cell)
        else:
            if candidate_row.aligned(cell) or candidate_row.included(cell) or table.included(cell):  # append
                candidate_row.add_cell(cell)
            else:
                if len(candidate_row.cells) > 2:    # save previous row
                    table.add_row(candidate_row)
                else:
                    tables.append(table)
                    table = Table()

                candidate_row = Row()
                candidate_row.add_cell(cell)

    # deal with leftovers, if any...
    if len(candidate_row.cells) > 2:
        table.add_row(candidate_row)

    cells = [cell for table in tables for cell in table.candidate_cells(global_cell.get_width())]
    return cells


def compare_cells(cell):
    """
    Filter function used to compare cells
    :param cell:
    :return:
    """
    return cell.y0, cell.x0, cell.x1, cell.y1


if __name__ == '__main__':
    pass
