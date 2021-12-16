from random import randint
import unittest
from pathlib import Path
import os
from lang.symb_eval import EvaluationUndefinedHoleError, Evaluator
from lang.ast import *
from lang.paddle import parse
from lark import exceptions
from lang.transformer import TransformerVariableException
from verification.verifier import is_valid


class TestStudent(unittest.TestCase):
    
    #Trivial test to make sure everything's working properly.
    def test_sanity_student(self):
        self.assertTrue(True)

    # Product check with integers. 
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

    # An advanced version of the prod example above. Contains more products of random variables.
    def test_example_prod_complex(self):
        filename = '%s/examples/prod_complex.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestStudent is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        self.assertIsInstance(prog_res, Expression)
        self.assertIsInstance(prog_res, BinaryExpr)
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        self.assertEqual(len(prog_res.uses()), 3)
        model = {"x": IntConst(1), "y": IntConst(
            2), "z": IntConst(3)}
        lhs = empty.evaluate_expr(model, prog_res.left_operand)
        rhs = empty.evaluate_expr(model, prog_res.right_operand)
        self.assertFalse(eval(str(lhs)) == eval(str(rhs)))

    # Simple test to check whether the element is divisible by 3
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

    # Subtraction checking with some manipulation
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

    # Multiplication checking with some manipulation
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

    # Basic bool checking
    def test_example_bazinga(self):
        filename = '%s/examples/bazinga.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog : Program = parse(filename)
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(prog)
        except:
            self.assertFalse(True, "Exception was raised when parsing %s" % filename)
        try:
            self.assertFalse(is_valid(final_constraint_expr))
        except:
            self.assertFalse(True, "Exception was raised when verifying %s" % filename)
    
    # Test to verify the results of multiplication operator
    def test_example_multicheck(self):
        filename = '%s/examples/multicheck.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog : Program = parse(filename)
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(prog)
        except:
            self.assertFalse(True, "Exception was raised when parsing %s" % filename)
        try:
            self.assertTrue(is_valid(final_constraint_expr))
        except:
            self.assertFalse(True, "Exception was raised when verifying %s" % filename)
    
    # Test to verify the least integer
    def test_example_least(self):
        filename = '%s/examples/least.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog : Program = parse(filename)
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(prog)
        except:
            self.assertFalse(True, "Exception was raised when parsing %s" % filename)
        try:
            self.assertTrue(is_valid(final_constraint_expr))
        except:
            self.assertFalse(True, "Exception was raised when verifying %s" % filename)
    
    # Test to check basic bool arithmetic and precedence
    def test_example_arithmetix(self):
        filename = '%s/examples/arithmetix.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog : Program = parse(filename)
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(prog)
        except:
            self.assertFalse(True, "Exception was raised when parsing %s" % filename)
        try:
            self.assertFalse(is_valid(final_constraint_expr))
        except:
            self.assertFalse(True, "Exception was raised when verifying %s" % filename)
    
    def test_example_arithmetix_int(self):
        filename = '%s/examples/arithmetix_int.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception("TestStudent is looking for %s. Make sure file exists." % filename)
        prog : Program = parse(filename)
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(prog)
        except:
            self.assertFalse(True, "Exception was raised when parsing %s" % filename)
        try:
            self.assertTrue(is_valid(final_constraint_expr))
        except:
            self.assertFalse(True, "Exception was raised when verifying %s" % filename)