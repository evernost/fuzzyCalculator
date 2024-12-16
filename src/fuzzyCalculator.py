# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : fuzzyCalculator
# File name       : fuzzyCalculator.py
# File type       : Python script (Python 3.10 or higher)
# Purpose         : Fuzzy calculator entry point
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
#
# -----------
# WHAT IS IT?
# -----------
# The Fuzzy Calculator is a regular calculator supporting classical math
# operations on scalars, but enhanced to work also on intervals.
#
# In other words, instead of calculating with numbers, it does the computation
# over the entire range the variables can live.
#
# Behind the scenes, it runs a Monte-Carlo simulation by generating random 
# values according to the statistics declared for each variable at play.
#
# At the end of the day, not only it gives an idea of the min/max range of the
# expression, but it also gives the probability for the output to live in a certain
# range.
#
# ----------------------
# WHAT CAN I DO WITH IT?
# ----------------------
# Non exhaustive list:
# - 
# - signal processing: determine the range of an input to define the most 
#                      appropriate coding.
# - worst case analysis: what are the min/max values an expression can reach?
#
# ----------------
# HOW DO I USE IT?
# ----------------
# The calculator takes as input a string containing the mathematical expression.
# All the parsing machinery is included.
# 
# The integrated parser supports "natural" inputs like good old TI calculators,
# which includes:
# - implicit multiplications: "(a+b)(c+d)"
# - lazy parenthesis: "sin(x+cox(y"
#
# NOTE: the detailed parsing rules can be found in <parser.py>
#
# Declare the variables and their statistic (uniform in range, gaussian, etc.)
# configure the simulation settings and voilà.
#
# --------------------
# WHAT ELSE DO I NEED?
# --------------------
# In order to make it easily portable to any target and/or programming language, 
# it is based on 'native' Python and does not require any specific library.
# In particular:
# - no regex
# - no complex string manipulation
#
# Only numpy/pyplotlib will be used at the end for the actual math and the plot
# but any similar library would do the job.
#
# ---------------------------------
# WHAT OPERATIONS CAN I DO WITH IT?
# ---------------------------------
# The calculator grants the most classical math operators ('+', '-', '*', '/', '^') 
# and more obscure ones ('//' for parallel resistor association in electronics)
# Usual math functions are included (sin, cos, log, log10, exp, abs, ...) 
#
# Structure is quite flexible so it is possible to add custom functions
# and infix operators. 
# Refer to <qParser.py> for more information about the limitations.
#
# ------------------------------
# WHAT FEATURES MIGHT COME NEXT? 
# ------------------------------
# The integrated parser (the "qParser") tries to treat the inputs as 'placeholders' as much as 
# possible which gives flexibility for the manipulated objects.
# Future releases could handle fixed point numbers, integers, matrices, etc.
#
# It is worth mentionning that the built-in parser preserves the order of the input, 
# therefore it does not assume commutativity of infix like '+', '*', ... 
# That implies the possibility to support matrices, quaternions or any other abstract 
# mathematical object in future releases.
#
# --------------
# ANYTHING ELSE?
# --------------
# - pipe chars "|" have been considered at some point as a shortcut for abs(), 
# but it didn't happen as they lead to ambiguity.
#
# Example: |a + b|cos(x)|c + d|
#
# A solution needs to be found for that.
#
# ------------
# TODO / IDEAS
# ------------
# Sorted by increasing effort: 
# - delete the 'match' function to support older versions of Python
# - add a pretty print for the 'binary tree' to check/debug the parser's interpretation
# - add support for scientific notation
# - parser: allow more flexibility to the rule [5.9] considering that variables are 
#           declared before calling the parser.
# - add support for thousands delimitation using "_": "3_141_592" vs "3141592"
# - add support for special characters (pi?)
# - add support for 'dot-prefixed' operators like '.+'?
# - add support for complex numbers
# - add an interactive mode where: 
#   > a command prompt appears
#   > variables and their statistics can be typed in the CLI
#   > the tree is built as the user types in the expression for immediate feedback
#   > pipes "|" are immediately translated to "abs("
#   > implicit multiplications are automatically expanded
#   > possible warnings (ambiguities, ...), errors are shown as the user types
#   > ...
#
#
#



# =============================================================================
# External libs
# =============================================================================
from src.commons import *

import src.binary as binary
import src.qParser as qParser

from enum import Enum



# =============================================================================
# Constants pool
# =============================================================================
class CalcStatus(Enum) :
  INIT = 0
  COMPILE_OK = 1
  COMPILE_FAILED = 2
  SIM_OK = 3



# =============================================================================
# Main code
# =============================================================================
class Calc :
  
  # ---------------------------------------------------------------------------
  # METHOD: Calc.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self) :
    self.expr       = ""
    self.variables  = []
    self.status     = CalcStatus.INIT

    self.binary = None

    self.hasVariables = False


  # ---------------------------------------------------------------------------
  # METHOD: Calc.input(string)
  # ---------------------------------------------------------------------------
  def input(self, expr) :
    """
    Sets the expression to be analysed by the parser.
    As it is set, some first basic checks are run on the expression to make 
    sure it is valid before proceeding any further.
    """

    self.expr = expr
    
    checkPassed = qParser.sanityCheck(self.expr)
    if not(checkPassed) :
      print("[ERROR] Parser halted due to an error in the sanity check.")
      exit()
      
    checkPassed = qParser.bracketBalanceCheck(self.expr)
    if not(checkPassed) :
      print("[ERROR] Parser halted due to an error in the bracket balance.")
      exit()
      
    checkPassed = qParser.firstOrderCheck(self.expr)
    if not(checkPassed) :
      print("[ERROR] Parser halted due to an error in the first order check.")
      exit()

    print(f"[INFO] Input set to '{self.expr}'")



  # ---------------------------------------------------------------------------
  # METHOD: Calc.compile()
  # ---------------------------------------------------------------------------
  def compile(self) :
    """
    Compiles the expression that has been set using 'input()'.
    Compilation process consists in:
    - STEP 1: rewrite the expression as a list of tokens
    - STEP 2: detect and add the implicit multiplication tokens
    - STEP 3: create a binary object from the list of tokens
    - STEP 4: nest away operators with higher precedence so that they are 
    evaluated first.
    The functions does not return anything, it populates the fields 'tokens'
    and 'binary', and updates the status.
    """
    
    # STEP 1: tokenise
    self.tokens = qParser.tokenise(self.expr)
    tokensFull = qParser.explicitMult(self.tokens)
    self.variables = qParser.getVariables(tokensFull)

    # STEP 2: binarise
    self.binary = binary.Binary(tokensFull)
    if (self.binary.status == binary.BINARISE_FAILURE) :
      print("[ERROR] Compilation failed: unable to binarise.")
      exit()
    
    # STEP 3: embed sections of higher precedence in a Macroleaf (nesting)
    self.binary.nest()
    
    self.status = CalcStatus.COMPILE_OK
    print("[INFO] Compile OK.")
    
    

  # ---------------------------------------------------------------------------
  # METHOD: Calc.print()
  # ---------------------------------------------------------------------------
  def print(self) :
    """
    For a scalar expression (no variables): evaluates the expression, returns
    the result.
    
    For an expression with variables: draws one occurence of the variables, 
    evaluates the expression and returns the value.
    
    For a more complete evaluation, please refer to the 'sim' method.
    """
    
    if (len(self.expr) == 0) :
      print("[ERROR] Please set an expression first using 'FuzzyCalculator.input()'")
      exit()

    if (self.status != CalcStatus.COMPILE_OK) :
      print("[ERROR] Please compile the expression using 'FuzzyCalculator.compile()' before evaluating it.")
      exit()
    
    if (self.hasVariables and (self.status != CalcStatus.SIM_OK)) :
      print("[WARNING] Expression has random variables: 'print' returns only the value of one single draw.")

    else :
      if not(self.hasVariables) :
        print("[INFO] Running in scalar mode.")
      out = self.binary.eval()
      print(f"[OUTPUT] {self.expr} = {out}")
    


  # ---------------------------------------------------------------------------
  # METHOD: Calc.print()
  # ---------------------------------------------------------------------------
  # def print(self) :
  #   """
  #   Prints the result of 'eval()' along with some useful information depending 
  #   on the simulation that has been run.
  #   """
    
  #   if (self.status != CalcStatus.COMPILE_OK) :
  #     print("[ERROR] Please compile an expression before evaluating it.")
    
  #   else :
  #     out = B.eval()

    
    
  # ---------------------------------------------------------------------------
  # METHOD: Calc.sim()
  # ---------------------------------------------------------------------------
  def sim(self, nPts = 1000) :
    """
    todo!
    """
    
    print("todo")



# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == "__main__") :
  print("[INFO] There are no unit tests available for 'fuzzyCalculator.py'")

