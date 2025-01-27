"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the synthesis portion
of the assignment.
"""

from typing import Mapping, Iterator, Set, Dict
from z3 import *
from lang.ast import *


class Synthesizer():
    """
    This class is has three methods `synth_method_1`, `synth_method_2` or
    `synth_method_3` for generating expression for a program's holes.

    You may also choose to add data attributes and methods to this class
    to enable instances of `Synthesizer` to remember information about
    previous runs.

    Calling `synth_method_1`, `synth_method_2` or `synth_method_3` should
    produce a new set of hole completions at each call for a given
    `Synthesizer` instance.
    For example, suppose the program p contains one hole `h1` with the
    grammar `[ G : int -> G + G | 0 | 1 ]`. Then, the following sequence
    is a possible execution:
    ```
    > s = Synthesizer(p)
    > s.synth_method_1()
    { "h1" : 0 }
    > s.synth_method_1()
    { "h1" : 1 }
    > s.synth_method_1()
    { "h1" : 0 + 1 }
    ...
    ```
    Each call produces a hole completion. The returned object should
    be a mapping from the hole id (its name) to the expression of the
    hole.
    Each `synth_method_..` should implement a different enumeration
    strategy (e.g. depth first, breadth first, constants-first,
    variables-first...).

    **Don't forget that we expect your third method to be the best on
    average!**

    *Hint*: the method `hole_can_use` in the `Program` class returns the
    set of variables that a given hole can use in its completions.
    e.g. `prog.hole_can_use("h1")` returns the variables that "h1" can use.
    """

    def __init__(self, ast: Program):
        """
        Initialize the Synthesizer.
        The Synthesizer can have a state or other data attributes and
        methods to remember which programs have been synthesized before.
        """
        self.vars_for_hole = {h.var.name: ast.hole_can_use(h.var.name) for h in ast.holes}
        self.generator_states = {}
        self.ordered_rules = {
            h.var.name: {r.symbol: sorted(r.productions, key=lambda p: len(p.children())) for r in h.grammar.rules} for
            h in ast.holes}
        # The synthesizer is initialized with the program ast it needs
        # to synthesize hole completions for.
        self.ast = ast
        self.max_depth = 5

    def do_derivation_1(self, ex: Expression,
                        sorted_rules: Dict[Variable, List[Expression]],
                        available_vars: Set[Variable],
                        depth: int = 5) -> Iterator[Expression]:
        """
        A generator function which, given an Expression with some non-terminals and a Grammar, eventually generates
        all possible derivations
        """
        if depth < 0:
            return
        # Handle the Var, Integer, or constant cases
        if isinstance(ex, GrammarVar):
            for v in available_vars:
                yield VarExpr(v)
            return
        elif isinstance(ex, GrammarInteger):
            for i in range(-10, 10):  # this is very stupid
                yield IntConst(i)
            return
        elif len(ex.uses()) == 0:  # this is a constant expression so can just return ex
            yield ex
            return

        # if none of the above cases apply, then we can likely apply one of the production rules in gram
        # note that just because len(ex.uses()) > 0 doesn't mean there must be some non terminals, could be given
        # an expression like (x1+1). ex.uses() would contain x1 even though it's not a non-terminal
        found_valid_rule = False
        for symbol, productions in sorted_rules.items():
            # this rule does not apply to this expression
            if symbol not in ex.uses():
                continue
            found_valid_rule = True

            # if we found a variable we can replace, generate all possible replacements
            if isinstance(ex, VarExpr) and ex.var.name == symbol.name:
                for product in productions:
                    for d in self.do_derivation_1(product, sorted_rules, available_vars, depth - 1):
                        if depth > 0 or len(d.children()) == 0:
                            yield d

            else:
                # recurse on composite expression types
                if isinstance(ex, Ite):
                    for c in self.do_derivation_1(ex.cond, sorted_rules, available_vars, depth - 1):
                        for t in self.do_derivation_1(ex.true_br, sorted_rules, available_vars, depth - 1):
                            for f in self.do_derivation_1(ex.false_br, sorted_rules, available_vars, depth - 1):
                                yield Ite(c, t, f)

                elif isinstance(ex, BinaryExpr):
                    for left in self.do_derivation_1(ex.left_operand, sorted_rules, available_vars, depth - 1):
                        for right in self.do_derivation_1(ex.right_operand, sorted_rules, available_vars, depth - 1):
                            yield BinaryExpr(ex.operator, left, right)

                elif isinstance(ex, UnaryExpr):
                    for u in self.do_derivation_1(ex.operand, sorted_rules, available_vars, depth - 1):
                        yield UnaryExpr(ex.operator, u)

                # never should have gotten
                elif isinstance(ex, (IntConst, BoolConst)):
                    raise ASTException("Somehow tried to do derivation on a constant expression")
                else:
                    raise ASTException(f"Unexpected expression type {ex.__class__()} for {ex}")

                return

        # no rules in the given grammar apply to this expression, so just return
        if not found_valid_rule:
            yield ex
            return
            # raise ASTException(f"could not replace all non terminals in {ex} with the grammar {gram}")

    def do_derivation_2(self, ex: Expression,
                        sorted_rules: Dict[Variable, List[Expression]],
                        available_vars: Set[Variable],
                        depth: int = 5) -> Iterator[Expression]:
        """
        A generator function which, given an Expression with some non-terminals and a Grammar, eventually generates
        all possible derivations
        """
        if depth < 0:
            return
        # Handle the Var, Integer, or constant cases
        if isinstance(ex, GrammarVar):
            for v in available_vars:
                yield VarExpr(v)
            return
        elif isinstance(ex, GrammarInteger):
            for i in range(-10, 10):  # this is very stupid
                yield IntConst(i)
            return
        elif len(ex.uses()) == 0:  # this is a constant expression so can just return ex
            yield ex
            return

        # if none of the above cases apply, then we can likely apply one of the production rules in gram
        # note that just because len(ex.uses()) > 0 doesn't mean there must be some non terminals, could be given
        # an expression like (x1+1). ex.uses() would contain x1 even though it's not a non-terminal
        found_valid_rule = False
        for symbol, productions in sorted_rules.items():
            # this rule does not apply to this expression
            if symbol not in ex.uses():
                continue
            found_valid_rule = True

            # if we found a variable we can replace, generate all possible replacements
            if isinstance(ex, VarExpr) and ex.var.name == symbol.name:
                for product in productions:
                    for d in self.do_derivation_1(product, sorted_rules, available_vars, depth - 1):
                        if depth > 0 or len(d.children()) == 0:
                            yield d

            else:
                # recurse on composite expression types
                if isinstance(ex, Ite):
                    for f in self.do_derivation_1(ex.false_br, sorted_rules, available_vars, depth - 1):
                        for t in self.do_derivation_1(ex.true_br, sorted_rules, available_vars, depth - 1):
                            for c in self.do_derivation_1(ex.cond, sorted_rules, available_vars, depth - 1):
                                yield Ite(c, t, f)

                elif isinstance(ex, BinaryExpr):
                    for right in self.do_derivation_1(ex.right_operand, sorted_rules, available_vars, depth - 1):
                        for left in self.do_derivation_1(ex.left_operand, sorted_rules, available_vars, depth - 1):
                            yield BinaryExpr(ex.operator, left, right)

                elif isinstance(ex, UnaryExpr):
                    for u in self.do_derivation_1(ex.operand, sorted_rules, available_vars, depth - 1):
                        yield UnaryExpr(ex.operator, u)

                # never should have gotten
                elif isinstance(ex, (IntConst, BoolConst)):
                    raise ASTException("Somehow tried to do derivation on a constant expression")
                else:
                    raise ASTException(f"Unexpected expression type {ex.__class__()} for {ex}")

                return

        # no rules in the given grammar apply to this expression, so just return
        if not found_valid_rule:
            yield ex
            return

    def generate_assignments(self, hole: HoleDeclaration, derivation_func) -> Iterator[Expression]:
        """
        Generator function that generates all possible assignments for the given hole.
        Assignments will be generated breadth first
        """
        # always start from the first production rule
        for product in hole.grammar.rules[0].productions:
            h = hole.var.name
            for assignment in derivation_func(product, self.ordered_rules[h], self.vars_for_hole[h], self.max_depth):
                yield assignment

    def get_next_assignment(self, h: HoleDeclaration, derivation_func):
        # will return None if there are no more completions
        next_expr = next(self.generator_states[h.var.name], None)
        if next_expr is None:
            self.max_depth *= 2
            self.generator_states[h.var.name] = self.generate_assignments(h, derivation_func)
            next_expr = next(self.generator_states[h.var.name], None)
        # print(next_expr)
        return {h.var.name: next_expr}

    def synth_method_1(self, ) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).

        Performs DFS search of all expressions, up to a depth of 5. When depth is reached, doubles depth and tries again
        This is not very efficient as it ends up generating the same expressions at low depths many times.
        """
        ans = {}
        for h in self.ast.holes:
            if h.var.name not in self.generator_states.keys():
                self.generator_states[h.var.name] = self.generate_assignments(h, self.do_derivation_1)
            ans = dict(ans, **self.get_next_assignment(self.ast.holes[0], self.do_derivation_1))

        return ans

    def synth_method_2(self, ) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 2).

        Reversed the order of expression expansion compared to synth_method_1. May perform differently in some cases
        """
        ans = {}
        for h in self.ast.holes:
            if h.var.name not in self.generator_states.keys():
                self.generator_states[h.var.name] = self.generate_assignments(h, self.do_derivation_2)
            ans = dict(ans, **self.get_next_assignment(self.ast.holes[0], self.do_derivation_2))

        return ans

    def synth_method_3(self, ) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 3).

        Ran out of time unfortunately, but would have liked to try putting all grammars in Chomsky Normal Form
        to guarantee we dont generate the same expression multiple times, and to to implement a BFS instead of DFS.
        This should have generated smaller, simpler expressions first, which would probably be more likely to be correct
        """
        return self.synth_method_2()
