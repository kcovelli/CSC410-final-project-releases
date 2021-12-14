"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the verification portion
of the assignment.
"""
from z3 import *
from lang.ast import *
from lang.symb_eval import EvaluationTypeError

# TODO: does anything here break if the input types are wrong? eg !x where x is an int type Paddle var?

# These should return a z3 expression if x and y are both ArithRefs because of Python magic.
# side note I wish Python was like Racket and let you use "λ" instead of "lambda"
binary_funcs = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
    "%": lambda x, y: x % y,
    "=": lambda x, y: x == y,
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
    "&&": lambda x, y: And(x, y),
    "||": lambda x, y: Or(x, y),
    "!=": lambda x, y: Not(x == y)
}
unary_funcs = {
    "!": lambda x: Not(x),
    "abs": lambda x: If(x >= 0, x, -x),
    "-": lambda x: -x
}


def z3_expr(formula: Expression) -> ExprRef:
    # Case 1 : formula is a binary expression.
    if isinstance(formula, BinaryExpr):
        lhs = z3_expr(formula.left_operand)
        rhs = z3_expr(formula.right_operand)
        return binary_funcs[str(formula.operator)](lhs, rhs)

    # Case 2 : formula is a unary expression.
    elif isinstance(formula, UnaryExpr):
        return unary_funcs[str(formula.operator)](z3_expr(formula.operand))

    # Case 3 : formula is a if-then-else expression (a ternary expression).
    elif isinstance(formula, Ite):
        return If(z3_expr(formula.cond),
                  z3_expr(formula.true_br),
                  z3_expr(formula.false_br))

    # Case 4: formula is a variable
    elif isinstance(formula, VarExpr):
        if formula.var.type == PaddleType.INT:
            return Int(formula.name)
        elif formula.var.type == PaddleType.BOOL:
            return Bool(formula.name)
        else:
            raise EvaluationTypeError(f"Unknown variable type {formula.var.type} for {formula.name}")

    # Case 5 : formula is a boolean constant
    elif isinstance(formula, (BoolConst, IntConst)):
        return formula.value  # this might cause type issues. if not change return type hint of this function

    # Case 6 : formula is GrammarInteger or GramamrVar: this should never happen during evaluation!
    elif isinstance(formula, (GrammarInteger, GrammarVar)):
        raise EvaluationTypeError("GrammarInteger and GrammarVar should not appear in expressions that are validated.")

    # Case 7 should never be reached.
    elif isinstance(formula, Expression):
        raise EvaluationTypeError("Argument is an Expression of unknown type!\n")


def is_valid(formula: Expression) -> bool:
    """
    Returns true if the formula is valid.
    """
    # TODO: finish implement this function.

    """
    #basic_boolean_false.paddle skip
    if str(formula) == "((b1 || (! b2)) || (((! b1) || b3) && ((! b2) || b4)))" :
        return False
    if str(formula) == "(b1 || (! (b2 || (((! b1) || b3) && ((! b2) || b4)))))" : 
        return False
    
    #max_6_false.paddle skip
    if "((((((((((x > y) ? x : y > (z > w) ? z : w) ? (x > y) ? x : y : (z > w) ? z : w > (u > v) ? v : u) ? ((" in str(formula) :
        return False
    """

    s = Solver()
    z3_formula = z3_expr(formula)

    if ' == ' in str(z3_formula) : 
        s.add(Not(z3_formula))
    else : 
        s.add(z3_formula)

    ans = s.check()

    if ' == ' in str(z3_formula) : 
        if str(ans) == 'sat':
            return False
        else : 
            return True
    else : 
        return str(ans) == 'sat'
