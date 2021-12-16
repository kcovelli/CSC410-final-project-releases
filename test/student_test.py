from random import randint
import unittest
from pathlib import Path
import os
from lang.symb_eval import EvaluationUndefinedHoleError, Evaluator
from lang.ast import *
from lang.paddle import parse
from lark import exceptions
from lang.transformer import TransformerVariableException


class TestStudent(unittest.TestCase):

    def test_sanity_student(self):
        self.assertTrue(True)

    def test_example_prod(self):
        filename = '%s/examples/prod.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestStudent is looking for %s. Make sure file exists." % filename)
        prog: Program = parse(filename)
        ev = Evaluator({})
        x = prog.get_var_of_name("x")
        y = prog.get_var_of_name("y")
        z = prog.get_var_of_name("z")
        self.assertIsInstance(prog, Program, msg="prog must be an instance of Program")
        try:
            self.assertIsInstance(ev, Evaluator, msg="ev must be an instance of Evaluator")
            expr = ev.evaluate(prog)
            self.assertTrue(prog.is_pure_expression(expr), msg="expr must be a pure expression")
            model = {"x": IntConst(randint(-5, 5)), "y": IntConst(randint(-5, 5)), "z": IntConst(randint(-5, 5))}
            e1 = ev.evaluate_expr(model, expr)
            self.assertTrue(prog.is_pure_expression(
                            e1), msg="Evaluation should return pure expressions")
            res = eval(pythonize(str(e1)))
            self.assertFalse(res)
        except:
            self.assertFalse(True, "Exception was raised when evaluating %s" % filename)

    def test_example_prod_complex(self):
        filename = '%s/examples/prod_complex.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "StudentTest is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only 4 variables in prog_res
        self.assertEqual(len(prog_res.uses()), 3)
        # Evaluate the expression
        model = {"x": IntConst(1), "y": IntConst(
            2), "z": IntConst(3)}
        lhs = empty.evaluate_expr(model, prog_res.left_operand)
        rhs = empty.evaluate_expr(model, prog_res.right_operand)
        # These expressions can be evaluated in Python directly
        # They should be different (3 != 4)
        self.assertFalse(eval(str(lhs)) == eval(str(rhs)))

    def test_example_divisible_by_3(self):
        filename = '%s/examples/divisble_by_3.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestStudent is looking for %s. Make sure file exists." % filename)
        prog: Program = parse(filename)
        ev = Evaluator({})
        x = prog.get_var_of_name("x")
        self.assertIsInstance(prog, Program, msg="prog must be an instance of Program")
        try:
            self.assertIsInstance(ev, Evaluator, msg="ev must be an instance of Evaluator")
            expr = ev.evaluate(prog)
            self.assertTrue(prog.is_pure_expression(expr), msg="expr must be a pure expression")
            model = {"x": IntConst(randint(-5, 5))}
            e1 = ev.evaluate_expr(model, expr)
            self.assertTrue(prog.is_pure_expression(
                            e1), msg="Evaluation should return pure expressions")
            res = eval(pythonize(str(e1)))
            self.assertTrue(res)
        except:
            self.assertFalse(True, "Exception was raised when evaluating %s" % filename)

    def test_example_sub_man(self):
        filename = '%s/examples/sub_man.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog: Program = parse(filename)
        ev = Evaluator({})
        x = prog.get_var_of_name("x")
        y = prog.get_var_of_name("y")
        z = prog.get_var_of_name("z")
        self.assertIsInstance(prog, Program, msg="prog must be an instance of Program")
        try:
            self.assertIsInstance(ev, Evaluator, msg="ev must be an instance of Evaluator")
            expr = ev.evaluate(prog)
            self.assertTrue(prog.is_pure_expression(expr), msg="expr must be a pure expression")
            model = {"x": IntConst(randint(-5, 5)), "y": IntConst(randint(-5, 5)), "z": IntConst(randint(-5, 5))}
            e1 = ev.evaluate_expr(model, expr)
            self.assertTrue(prog.is_pure_expression(e1), msg="Evaluation should return pure expressions")
            res = eval(pythonize(str(e1)))
            self.assertTrue(res)
        except:
            self.assertFalse(True, "Exception was raised when evaluating %s" % filename)

    def test_example_multi_man(self):
        filename = '%s/examples/multi_man.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog: Program = parse(filename)
        ev = Evaluator({})
        x = prog.get_var_of_name("x")
        y = prog.get_var_of_name("y")
        z = prog.get_var_of_name("z")
        self.assertIsInstance(prog, Program, msg="prog must be an instance of Program")
        try:
            self.assertIsInstance(ev, Evaluator, msg="ev must be an instance of Evaluator")
            expr = ev.evaluate(prog)
            self.assertTrue(prog.is_pure_expression(expr), msg="expr must be a pure expression")
            model = {"x": IntConst(randint(1, 10)), "y": IntConst(randint(1, 10)), "z": IntConst(randint(1, 10))}
            e1 = ev.evaluate_expr(model, expr)
            self.assertTrue(prog.is_pure_expression(e1), msg="Evaluation should return pure expressions")
            res = eval(pythonize(str(e1)))
            self.assertTrue(res)
        except:
            self.assertFalse(True, "Exception was raised when evaluating %s" % filename)
