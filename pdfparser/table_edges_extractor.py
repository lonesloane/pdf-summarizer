from pdfparser import _log_level, _config

MAX_RECURSION = _config.getint('MAIN', 'MAX_RECURSION')
ADJ_DISTANCE = _config.getfloat('MAIN', 'ADJ_DISTANCE')
X0, Y0, X1, Y1 = 0, 1, 2, 3


class Cell:

    _MIN_HEIGHT = _config.getfloat('MAIN', 'CELL_MIN_HEIGHT')
    _MIN_WIDTH = _config.getfloat('MAIN', 'CELL_MIN_WIDTH')
    _TEXT_MIN_FRACTION_SIZE = _config.getfloat('MAIN', 'TEXT_MIN_FRACTION_SIZE')

    def __init__(self, x0, y0, x1, y1, rows=1, columns=1, logger=None):
        self.logger = logger
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.height = abs(self.y0 - self.y1)
        self.rows = rows if self.height > Cell._MIN_HEIGHT else 0
        self.width = abs(self.x0 - self.x1)
        self.columns = columns if self.width > Cell._MIN_WIDTH else 0

    def __repr__(self):
        return ('[' + 'x0: ' + str(self.x0) + ', y0: ' + str(self.y0) +
                ', x1: ' + str(self.x1) + ', y1: ' + str(self.y1) +
                ', rows: ' + str(self.rows) + ', columns: ' + str(self.columns) + ']')

    def contains(self, coord):
        if self.x0 <= coord[X0] and self.y0 <= coord[Y0] and self.x1 >= coord[X1] and self.y1 >= coord[Y1]:
            return True
        return False

    def is_fraction(self, coord):
        text_width = abs(coord[X0] - coord[X1])
        fraction = text_width / self.width

        if _log_level > 2:
            self.logger.debug('table x0: {table.x0} - table x1: {table.x1}'.format(table=self))
            self.logger.debug('table width: {cw}'.format(cw=self.width))
            self.logger.debug('text x0: {x0} - text x1: {x1}'.format(x0=coord[X0], x1=coord[X1]))
            self.logger.debug('text width: {tw}'.format(tw=text_width))
            self.logger.debug('Fraction: {fraction}'.format(fraction=fraction))

        if fraction < Cell._TEXT_MIN_FRACTION_SIZE:
            return True
        return False


def adjacent(pt1, pt2):
    if abs(pt1 - pt2) < ADJ_DISTANCE:
        return True
    return False


def same_cell(cell, neighbor_cell):
    if cell.x0 != neighbor_cell.x0:
        return False
    if cell.x1 != neighbor_cell.x1:
        return False
    if cell.y0 != neighbor_cell.y0:
        return False
    if cell.y1 != neighbor_cell.y1:
        return False
    return True


def find_outer_edges(cells, nth_recursion=0):
    nth_recursion += 1
    log('{n}th recursion step'.format(n=nth_recursion))
    if nth_recursion > MAX_RECURSION:
        return cells
    log('Initial nb cells found: {ntables}'.format(ntables=len(cells)))

    converged = True
    neighbor_cells = cells[:]  # deep copy to ensure no side effects (really useful?)
    collapsed_cells = list()
    ignored_cells = list()

    for cell in cells:
        log('Trying to collapse cell: {cell}'.format(cell=cell))
        # collapsed = False
        if cell in ignored_cells:
            continue
        collapsed_cell = cell

        for neighbor_cell in neighbor_cells:
            collapsed = False
            if neighbor_cell in ignored_cells or same_cell(cell, neighbor_cell):
                log('neighbor cell ignored')
                continue

            log('neighbor cell {neighbor_cell}'.format(neighbor_cell=neighbor_cell))

            # Collapse adjacent cell on West side
            if ((adjacent(collapsed_cell.x0, neighbor_cell.x1)) and
                    (adjacent(neighbor_cell.y0, collapsed_cell.y0) or adjacent(neighbor_cell.y1, collapsed_cell.y1))):
                log('[W] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                             neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_west(collapsed_cell, neighbor_cell)
                log('[W] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed = True

            # Collapse adjacent cell on East side
            if ((adjacent(neighbor_cell.x0, collapsed_cell.x1)) and
                    (adjacent(neighbor_cell.y0, collapsed_cell.y0) or adjacent(neighbor_cell.y1, collapsed_cell.y1))):
                log('[E] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                             neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_east(collapsed_cell, neighbor_cell)
                log('[E] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed = True

            # Collapse adjacent cell on South side
            if ((adjacent(collapsed_cell.y0, neighbor_cell.y1)) and
                    (adjacent(neighbor_cell.x0, collapsed_cell.x0) or adjacent(neighbor_cell.x1, collapsed_cell.x1))):
                log('[S] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                             neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_south(collapsed_cell, neighbor_cell)
                log('[S] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed = True

            # Collapse adjacent cell on North side
            if ((adjacent(neighbor_cell.y0, collapsed_cell.y1)) and
                    (adjacent(neighbor_cell.x0, collapsed_cell.x0) or
                     adjacent(neighbor_cell.x1, collapsed_cell.x1))):
                log('[N] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                             neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_north(collapsed_cell, neighbor_cell)
                log('[N] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed = True

            # Collapse inner cell
            if ((collapsed_cell.x0 <= neighbor_cell.x0 <= neighbor_cell.x1 <= collapsed_cell.x1) and
                    (collapsed_cell.y0 <= neighbor_cell.y0 <= neighbor_cell.y1 <= collapsed_cell.y1)):
                log('[INNER] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                                 neighbor_cell=neighbor_cell))
                log('[INNER] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cell.columns += neighbor_cell.columns
                collapsed_cell.rows += neighbor_cell.rows
                collapsed = True

            # Collapse outer cell
            if ((neighbor_cell.x0 <= collapsed_cell.x0 <= collapsed_cell.x1 <= neighbor_cell.x1) and
                    (neighbor_cell.y0 <= collapsed_cell.y0 <= collapsed_cell.y1 <= neighbor_cell.y1)):
                log('[OUTER] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                                 neighbor_cell=neighbor_cell))
                log('[OUTER] resulting cell {cell}'.format(cell=neighbor_cell))
                neighbor_cell.columns += collapsed_cell.columns
                neighbor_cell.rows += collapsed_cell.rows
                collapsed_cell = neighbor_cell
                collapsed = True

            # Collapse overlapping cell on the right
            if (neighbor_cell.x0 <= collapsed_cell.x1 and
                    (collapsed_cell.y0 <= neighbor_cell.y0 <= collapsed_cell.y1 or
                     collapsed_cell.y0 <= neighbor_cell.y1 <= collapsed_cell.y1)):
                log('[OE] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                              neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_overlapping(collapsed_cell, neighbor_cell)
                log('[OE] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed = True

            # Collapse overlapping cell on the left
            if (neighbor_cell.x1 >= collapsed_cell.x0 and
                    (collapsed_cell.y0 <= neighbor_cell.y0 <= collapsed_cell.y1 or
                     collapsed_cell.y0 <= neighbor_cell.y1 <= collapsed_cell.y1)):
                log('[OW] collapsing cells {cell} and {neighbor_cell}'.format(cell=collapsed_cell,
                                                                              neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_overlapping(collapsed_cell, neighbor_cell)
                log('[OW] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed = True

            if collapsed:
                ignored_cells.append(cell)
                ignored_cells.append(neighbor_cell)
                converged = False
            else:
                log('No match found for neighbor cell {cell}'.format(cell=neighbor_cell))

        collapsed_cells.append(collapsed_cell)

    if converged:
        log('Converged. All cells collapsed....')
        return collapsed_cells
    else:
        log('Final nb cells found: {ntables}'.format(ntables=len(collapsed_cells)))
        for cell in collapsed_cells:
            log(cell)
        # Not converged yet, make a recursive call to ourselves with cells collapsed so far.
        return find_outer_edges(collapsed_cells, nth_recursion=nth_recursion)


def collapse_overlapping(cell, neighbor_cell):
    left = min(cell.x0, neighbor_cell.x0)
    right = max(cell.x1, neighbor_cell.x1)
    top = max(cell.y1, neighbor_cell.y1)
    bottom = min(cell.y0, neighbor_cell.y0)
    rows = cell.rows + neighbor_cell.rows
    columns = cell.columns + neighbor_cell.columns
    collapsed_cell = Cell(left, bottom, right, top, rows=rows, columns=columns)
    return collapsed_cell


def collapse_north(cell, neighbor_cell):
    left = min(cell.x0, neighbor_cell.x0)
    right = max(cell.x1, neighbor_cell.x1)
    rows = cell.rows + neighbor_cell.rows
    columns = max(cell.columns, neighbor_cell.columns)
    collapsed_cell = Cell(left, cell.y0, right, neighbor_cell.y1, rows=rows, columns=columns)
    return collapsed_cell


def collapse_south(cell, neighbor_cell):
    left = min(cell.x0, neighbor_cell.x0)
    right = max(cell.x1, neighbor_cell.x1)
    rows = cell.rows + neighbor_cell.rows
    columns = max(cell.columns, neighbor_cell.columns)
    collapsed_cell = Cell(left, neighbor_cell.y0, right, cell.y1, rows=rows, columns=columns)
    return collapsed_cell


def collapse_east(cell, neighbor_cell):
    bottom = min(cell.y0, neighbor_cell.y0)
    top = max(cell.y1, neighbor_cell.y1)
    rows = max(cell.rows, neighbor_cell.rows)
    columns = cell.columns + neighbor_cell.columns
    collapsed_cell = Cell(cell.x0, bottom, neighbor_cell.x1, top, rows=rows, columns=columns)
    return collapsed_cell


def collapse_west(cell, neighbor_cell):
    bottom = min(cell.y0, neighbor_cell.y0)
    top = max(cell.y1, neighbor_cell.y1)
    rows = max(cell.rows, neighbor_cell.rows)
    columns = cell.columns + neighbor_cell.columns
    collapsed_cell = Cell(neighbor_cell.x0, bottom, cell.x1, top, rows=rows, columns=columns)
    return collapsed_cell


def log(log_text):
    if _log_level > 2:
        pass
        #logger.debug(log_text)

if __name__ == '__main__':
    pass
