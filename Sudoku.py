from typing import Set, Dict

from CSP import CSP, Variable, Value


class Sudoku(CSP):
    def __init__(self):
        super().__init__()
        # TODO: Implement Sudoku::__init__ (problem 4)
        # self.n = n always 9x9 = 81 cells
        self._variables = set()
        for row in range(9):
            for col in range(9):
                self._variables.add(Cell(row, col))

    @property
    def variables(self) -> Set['Cell']:
        """ Return the set of variables in this CSP. """
        # TODO: Implement Sudoku::variables (problem 4)
        return self._variables
        pass

    def getCell(self, x: int, y: int) -> 'Cell':
        """ Get the  variable corresponding to the cell on (x, y) """
        # TODO: Implement Sudoku::getCell (problem 4)
        for cell in self._variables:
            if cell.row == x and cell.col == y:
                return cell
        pass

    def neighbors(self, var: 'Cell') -> Set['Cell']:
        """ Return all variables related to var by some constraint. """
        # TODO: Implement Sudoku::neighbors (problem 4)
        neighbors = set()
        for cell in self._variables:
            if cell.isNeighbor(var):
                neighbors.add(cell)
        return neighbors
        pass

    def isValidPairwise(self, var1: 'Cell', val1: Value, var2: 'Cell', val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp. """
        # TODO: Implement Sudoku::isValidPairwise (problem 4)
        return val1 != val2 or not var1.isNeighbor(var2)
        pass

    def assignmentToStr(self, assignment: Dict['Cell', Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for y in range(9):
            if y != 0 and y % 3 == 0:
                s += "---+---+---\n"
            for x in range(9):
                if x != 0 and x % 3 == 0:
                    s += '|'

                cell = self.getCell(x, y)
                s += str(assignment.get(cell, ' '))
            s += "\n"
        return s

    def parseAssignment(self, path: str) -> Dict['Cell', Value]:
        """ Gives an initial assignment for a Sudoku board from file. """
        initialAssignment = dict()

        with open(path, "r") as file:
            for y, line in enumerate(file.readlines()):
                if line.isspace():
                    continue
                assert y < 9, "Too many rows in sudoku"

                for x, char in enumerate(line):
                    if char.isspace():
                        continue

                    assert x < 9, "Too many columns in sudoku"

                    var = self.getCell(x, y)
                    val = int(char)

                    if val == 0:
                        continue

                    assert val > 0 and val < 10, f"Impossible value in grid"
                    initialAssignment[var] = val
        return initialAssignment


class Cell(Variable):
    def __init__(self, row, col):
        super().__init__()
        # TODO: Implement Cell::__init__ (problem 4)
        # You can add parameters as well.
        self.row = row
        self.col = col

    def isNeighbor(self, cell):
        if cell == self: return False
        return cell.row == self.row or \
               cell.col == self.col or \
               (int(cell.row / 3) == int(self.row / 3) and int(cell.col / 3) == int(self.col / 3))

    def __repr__(self):
        return f"({self.row}, {self.col})"
    @property
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        # TODO: Implement Cell::startDomain (problem 4)
        return set(range(1, 10, 1))
