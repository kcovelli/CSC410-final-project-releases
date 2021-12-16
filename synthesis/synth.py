"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the synthesis portion
of the assignment.
"""

from typing import Mapping, Iterator
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

    # TODO: put all grammars in Chomsky Normal Form, will guarantee we don't duplicate any derivations
    def __init__(self, ast: Program):
        """
        Initialize the Synthesizer.
        The Synthesizer can have a state or other data attributes and
        methods to remember which programs have been synthesized before.
        """
        self.vars_for_hole = {h.var.name: ast.hole_can_use(h.var.name) for h in ast.holes}
        self.generator_states = {}
        # The synthesizer is initialized with the program ast it needs
        # to synthesize hole completions for.
        self.ast = ast

    # TODO: implement something that allows you to remember which
    # programs have already been generated.

    def do_derivation(self, ex: Expression, gram: Grammar, available_vars: set[Variable]) -> Iterator[Expression]:
        """
        A generator function which, given an Expression with some non-terminals and a Grammar, eventually generates
        all possible derivations
        """

        # Handle the Var, Integer, or constant cases
        if isinstance(ex, GrammarVar):
            for v in available_vars:
                yield VarExpr(v)
            return
        elif isinstance(ex, GrammarInteger):
            for i in range(-10, 10):  # TODO: make this not stupid
                yield IntConst(i)
            return
        elif len(ex.uses()) == 0:  # this is a constant expression so can just return ex
            yield ex
            return

        # if none of the above cases apply, then we can likely apply one of the production rules in gram
        # note that just because len(ex.uses()) > 0 doesn't mean there must be some non terminals, could be given
        # an expression like (x1+1). ex.uses() would contain x1 even though it's not a non-terminal
        found_valid_rule = False
        for rule in gram.rules:
            # this rule does not apply to this expression
            if rule.symbol not in ex.uses():
                continue
            found_valid_rule = True

            # if we found a variable we can replace, generate all possible replacements
            if isinstance(ex, VarExpr) and ex.var.name == rule.symbol.name:
                # TODO: need to make sure we put the terminals first
                best_order = sorted(rule.productions,
                                    key=lambda p: len(p.children()))  # TODO: can generate this in __init__
                for product in best_order:
                    for d in self.do_derivation(product, gram, available_vars):
                        yield d
            else:
                # recurse on composite expression types
                if isinstance(ex, Ite):
                    for c in self.do_derivation(ex.cond, gram, available_vars):
                        for t in self.do_derivation(ex.true_br, gram, available_vars):
                            for f in self.do_derivation(ex.false_br, gram, available_vars):
                                yield Ite(c, t, f)

                elif isinstance(ex, BinaryExpr):
                    for l in self.do_derivation(ex.left_operand, gram, available_vars):
                        for r in self.do_derivation(ex.right_operand, gram, available_vars):
                            yield BinaryExpr(ex.operator, l, r)

                elif isinstance(ex, UnaryExpr):
                    for u in self.do_derivation(ex.operand, gram, available_vars):
                        yield UnaryExpr(ex.operator, u)

                # never should have got here since ex.uses() would be empty
                elif isinstance(ex, (IntConst, BoolConst)):
                    raise ASTException("Somehow tried to do derivation on a constant expression")
                else:
                    raise ASTException(f"Unexpected expression type {ex.__class__()} for {ex}")

                return

        # no rules in the given grammar apply to this expression, so just return the expression
        if not found_valid_rule:
            yield ex
            return
            # raise ASTException(f"could not replace all non terminals in {ex} with the grammar {gram}")

    def generate_assignments(self, hole: HoleDeclaration) -> Iterator[Expression]:
        """
        Generator function that generates all possible assignments for the given hole.
        Assignments will be generated breadth first
        """
        # always start from the first production rule
        for product in hole.grammar.rules[0].productions:
            for assignment in self.do_derivation(product, hole.grammar, self.vars_for_hole[hole.var.name]):
                yield assignment

    def synth_method_1(self, ) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).

        **TODO: write a description of your approach in this method.**
        """
        for h in self.ast.holes:
            if h.var.name not in self.generator_states.keys():
                self.generator_states[h.var.name] = self.generate_assignments(h)

        if len(self.ast.holes) == 1:
            h = self.ast.holes[0]
            # will return None if there are no more completions
            next_expr = next(self.generator_states[h.var.name], None)
            return {h.var.name: next_expr}
        else:
            raise NotImplementedError("Haven't implemented support for multiple holes yet")

    def synth_method_2(self, ) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 2).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        return self.synth_method_1()
        # raise Exception("Synth.Synthesizer.synth_method_2 is not implemented.")

    def synth_method_3(self, ) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 3).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        return self.synth_method_1()
        # raise Exception("Synth.synth_method_3 is not implemented.")
