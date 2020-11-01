import random
from typing import Set, Dict, List, TypeVar, Optional
from abc import ABC, abstractmethod

from copy import copy, deepcopy
from queue import Queue
from pprint import pprint

from util import monitor

Value = TypeVar('Value')


class Variable(ABC):
    @property
    @abstractmethod
    def startDomain(self) -> Set[Value]:
        """ Returns the set of initial values of this variable (not taking constraints into account). """
        pass


class CSP(ABC):
    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        """ Return the set of variables in this CSP.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def remainingVariables(self, assignment: Dict[Variable, Value]) -> Set[Variable]:
        """ Returns the variables not yet assigned. """
        return self.variables.difference(assignment.keys())

    @abstractmethod
    def neighbors(self, var: Variable) -> Set[Variable]:
        """ Return all variables related to var by some constraint.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def assignmentToStr(self, assignment: Dict[Variable, Value]) -> str:
        """ Formats the assignment of variables for this CSP into a string. """
        s = ""
        for var, val in assignment.items():
            s += f"{var} = {val}\n"
        return s

    def isComplete(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment covers all variables.
            :param assignment: dict (Variable -> value)
        """
        # TODO: Implement CSP::isComplete (problem 1)
        return len(assignment) == len(self.variables)

    @abstractmethod
    def isValidPairwise(self, var1: Variable, val1: Value, var2: Variable, val2: Value) -> bool:
        """ Return whether this pairwise assignment is valid with the constraints of the csp.
            Abstract method to be implemented for specific instances of CSP problems.
        """
        pass

    def isValid(self, assignment: Dict[Variable, Value]) -> bool:
        """ Return whether the assignment is valid (i.e. is not in conflict with any constraints).
            You only need to take binary constraints into account.
            Hint: use `CSP::neighbors` and `CSP::isValidPairwise` to check that all binary constraints are satisfied.
            Note that constraints are symmetrical, so you don't need to check them in both directions.
        """
        # TODO: Implement CSP::isValid (problem 1)
        skip_pairs = set()
        for variable in assignment:
            for neighbor in self.neighbors(variable):
                if neighbor not in assignment: continue
                if variable == neighbor: continue
                if (variable, neighbor) in skip_pairs: continue
                if not self.isValidPairwise(variable, assignment[variable], neighbor, assignment[neighbor]):
                    # print("Nope")
                    return False
                skip_pairs.add((neighbor, variable))
                skip_pairs.add((variable, neighbor))
        return True

    def solveBruteForce(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with brute force technique.
            Initializes the domains and calls `CSP::_solveBruteForce`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        return self._solveBruteForce(initialAssignment, domains)

    @monitor
    def _solveBruteForce(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm to brute force this CSP.
            Use `CSP::isComplete`, `CSP::isValid`, `CSP::selectVariable` and `CSP::orderDomain`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        # TODO: Implement CSP::_solveBruteForce (problem 1)
        # Code based on function Recursive-Backtracking(assignment, csp) returns solution/failure from notes 2, p. 4

        # if assignment is complete then return assignment
        if self.isComplete(assignment):
            return assignment

        # var <- Select-Unassigned-Variable(Variables[csp], assignment, csp)
        var = self.selectVariable(assignment, domains)

        # for each value in Order-Domain-Values(var, assignment, csp) do
        for value in self.orderDomain(assignment, domains, var):
            # print(var, value)
            # if value is consistent with assignment given Constraints[csp] then
            # add {var = value} to assignment
            new_assignment = copy(assignment)  # fy python
            new_assignment[var] = value
            # TODO: Iedere keer alle variabelen checken??? Te veel overhead, maar isValid heeft maar 1 arg
            if self.isValid(new_assignment):
                # result <- Recursive-Backtracking(assignment, csp)
                result = self._solveBruteForce(new_assignment, domains)
                # if result != failure then return result
                if result is not None:
                    return result
                # remove {var=value} from assignment
                # assignment.pop(var)
        return None

    def solveForwardChecking(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[
        Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking.
            Initializes the domains and calls `CSP::_solveForwardChecking`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains = self.forwardChecking(initialAssignment, domains)
        return self._solveForwardChecking(initialAssignment, domains)

    def domain_copy(self, domain):
        # Arrrrhhh, soms heb ik echt een hekel aan Python
        # Copy -> Wil ni werken, want die dict heeft sets in zich die nog veranderen
        # Deepcopy -> Wil ni werken, want dan zijn cie variabelen in die set niet meer gelijk aan de oorspronkelijke variabele
        # Laat mij gerust iets weten als hier een efficientere oplossing voor is dan deze functie
        cp = dict()
        for key in domain:
            cp[key] = copy(domain[key])
        return cp


    @monitor
    def _solveForwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """ Implement the actual backtracking algorithm with forward checking.
            Use `CSP::forwardChecking` and you should no longer need to check if an assignment is valid.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        # TODO: Implement CSP::_solveForwardChecking (problem 2)

        # code based on _solveBruteForce

        # if assignment is complete then return assignment
        if self.isComplete(assignment):
            return assignment

        # var <- Select-Unassigned-Variable(Variables[csp], assignment, csp)
        var = self.selectVariable(assignment, domains)

        # for each value in Order-Domain-Values(var, assignment, csp) do
        for value in self.orderDomain(assignment, domains, var):
            # print(var, value)
            # if value is consistent with assignment given Constraints[csp] then
            # add {var = value} to assignment
            new_assignment = copy(assignment)  # fy python
            new_assignment[var] = value

            new_domains = copy(domains)
            new_domains[var] = {value}

            new_domains = self.forwardChecking(copy(new_assignment), self.domain_copy(new_domains), var)
            result = self._solveForwardChecking(copy(new_assignment), self.domain_copy(new_domains))

            if result is not None:
                return result
        return None

    def forwardChecking(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]],
                        variable: Optional[Variable] = None) -> Dict[Variable, Set[Value]]:
        """ Implement the forward checking algorithm from the theory lectures.

        :param domains: current domains.
        :param assignment: current assignment.
        :param variable: If not None, the variable that was just assigned (only need to check changes).
        :return: the new domains after enforcing all constraints.
        """
        # TODO: Implement CSP::forwardChecking (problem 2)
        # Code based on function AC-3 (csp) returns the CSP, possibly with reduced domains
        # inputs: csp, a binary CSP with variables {X1, ... Xn}

        # Local variables: queue, a queue of arcs, initially all the arcs in csp
        queue = Queue()
        # Add unassigned variables to queue
        for var1 in self.variables:
            for var2 in self.neighbors(var1):
                # if var2 in assignment: continue
                if variable is not None and variable not in (var1, var2): continue
                if var1 == var2: continue
                queue.put((var1, var2))

        while not queue.empty():
            xi, xj = queue.get()

            # Code based on remove-inconsistent-values(xi, xj) notes p. 7
            removed = False
            for x in copy(domains[xi]):
                satisfied = False
                for y in copy(domains[xj]):
                    if self.isValidPairwise(xi, x, xj, y):
                        satisfied = True
                        break
                if not satisfied:
                    domains[xi].remove(x)
                    removed = True


            if removed:
                for xk in self.neighbors(xi):
                    queue.put((xk, xi))

        return domains

    def selectVariable(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Variable:
        """ Implement a strategy to select the next variable to assign. """
        # return random.choice(list(self.remainingVariables(assignment)))
        # Neem variabele met laagste domain mogelijkheden (want meer variabelen is meer werk om te backtracken)
        var = None
        for variable in self.remainingVariables(assignment):
            if var is None or len(domains[variable]) < len(domains[var]):
                var = variable
        return var
        # TODO: Implement CSP::selectVariable (problem 2)

    def orderDomain(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]], var: Variable) -> \
            List[Value]:
        """ Implement a smart ordering of the domain values. """
        # return list(domains[var])
        # TODO: Implement CSP::orderDomain (problem 2)
        # variabelen die niet veel in andere domains voorkomen eerst
        val_occurrances = dict()
        for var_ in domains:
            for val in domains[var_]:
                if val not in val_occurrances:
                    val_occurrances[val] = 0
                val_occurrances[val] += 1

        result = list(domains[var])
        result.sort(key=lambda x: val_occurrances[x])
        return result


    def solveAC3(self, initialAssignment: Dict[Variable, Value] = dict()) -> Optional[Dict[Variable, Value]]:
        """ Called to solve this CSP with forward checking and AC3.
            Initializes domains and calls `CSP::_solveAC3`. """
        domains = domainsFromAssignment(initialAssignment, self.variables)
        domains = self.forwardChecking(initialAssignment, domains)
        return self._solveAC3(initialAssignment, domains)

    @monitor
    def _solveAC3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Optional[
        Dict[Variable, Value]]:
        """
            Implement the actual backtracking algorithm with AC3 (and FC).
            Use `CSP::ac3`.
            :return: a complete and valid assignment if one exists, None otherwise.
        """
        # TODO: Implement CSP::_solveAC3 (problem 3)

        # code based on _solveBruteForce

        # if assignment is complete then return assignment
        if self.isComplete(assignment):
            return assignment

        # var <- Select-Unassigned-Variable(Variables[csp], assignment, csp)
        var = self.selectVariable(assignment, domains)

        # for each value in Order-Domain-Values(var, assignment, csp) do
        for value in self.orderDomain(assignment, domains, var):
            # print(var, value)
            # if value is consistent with assignment given Constraints[csp] then
            # add {var = value} to assignment
            new_assignment = copy(assignment)  # fy python
            new_assignment[var] = value

            new_domains = copy(domains)
            new_domains[var] = {value}

            new_domains = self.forwardChecking(copy(new_assignment), self.domain_copy(new_domains), var)
            result = self._solveAC3(copy(new_assignment), self.domain_copy(new_domains))

            if result is not None:
                return result
        return None

    def ac3(self, assignment: Dict[Variable, Value], domains: Dict[Variable, Set[Value]]) -> Dict[Variable, Set[Value]]:
        """ Implement the AC3 algorithm from the theory lectures.
        :return: the new domains ensuring arc consistency.
        """
        # TODO: Implement CSP::ac3 (problem 3)

        # Code based on function AC-3 (csp) returns the CSP, possibly with reduced domains
        # inputs: csp, a binary CSP with variables {X1, ... Xn}

        # Local variables: queue, a queue of arcs, initially all the arcs in csp
        queue = Queue()
        # Add unassigned variables to queue
        for var1 in self.variables:
            for var2 in self.neighbors(var1):
                # if var2 in assignment: continue
                # if variable is not None and variable not in (var1, var2): continue
                if var1 == var2: continue
                queue.put((var1, var2))

        while not queue.empty():
            xi, xj = queue.get()

            # Code based on remove-inconsistent-values(xi, xj) notes p. 7
            removed = False
            for x in copy(domains[xi]):
                satisfied = False
                for y in copy(domains[xj]):
                    if self.isValidPairwise(xi, x, xj, y):
                        satisfied = True
                        break
                if not satisfied:
                    domains[xi].remove(x)
                    removed = True

            if removed:
                for xk in self.neighbors(xi):
                    queue.put((xk, xi))

        return domains


def domainsFromAssignment(assignment: Dict[Variable, Value], variables: Set[Variable]) -> Dict[Variable, Set[Value]]:
    """ Fills in the initial domains for each variable.
        Already assigned variables only contain the given value in their domain.
    """
    domains = {v: v.startDomain for v in variables}
    for var, val in assignment.items():
        domains[var] = {val}
    return domains
