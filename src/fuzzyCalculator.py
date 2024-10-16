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
from commons import *
from enum import Enum

import qParser
import variable



class calcStatus(Enum) :
  INIT = 0
  COMPILE_OK = 1
  COMPILE_FAILED = 2




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
    self.status     = calcStatus.INIT



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
    
    # Run some basic checks
    ret = qParser.sanityCheck(self.expr)
    if (ret != CHECK_SUCCESS) :
      print("[ERROR] Parser failed due to an error in the sanity check.")
      exit()
      
    ret = qParser.bracketBalanceCheck(self.expr)
    if (ret != CHECK_SUCCESS) :
      print("[ERROR] Parser failed due to an error in the bracket balance.")
      exit()
      
    ret = qParser.firstOrderCheck(self.expr)
    if (ret != CHECK_SUCCESS) :
      print("[ERROR] Parser failed due to an error in the first order check.")
      exit()



  # ---------------------------------------------------------------------------
  # METHOD: Calc.compile()
  # ---------------------------------------------------------------------------
  def compile(self) :
  
    
    # STEP 1: rewrite the expression as a list of tokens
    tokenList = qParser.tokenise(self.expr)
    
    # STEP 2: detect and add the implicit multiplication tokens
    tokenListFull = qParser.explicitMult(tokenList)
    
    # STEP 3: create a binary object from the list of tokens
    B = binary.Binary(tokenListFull)
  
    # STEP 4: nest away operators with higher precedence
    B.nest()
    
    # STEP 6: evaluate!
    #out = B.eval()

    # TODO: update the internal status
    #self.status = ...
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Calc.eval()
  # ---------------------------------------------------------------------------
  def eval(self) :
    """
    For a scalar expression (no variables): evaluates the expression, returns
    the value.
    
    For an expression with variables: draws one occurence of the variables, 
    evaluates the expression and returns the value.
    
    For a more complete evaluation, please refer to the 'sim' method.
    """
    
    if (self.status != calcStatus.COMPILE_OK) :
      print("[ERROR] Please compile an expression before evaluating it.")
    
    else :
      print("todo")
    
    
    
  # ---------------------------------------------------------------------------
  # METHOD: Calc.sim()
  # ---------------------------------------------------------------------------
  def sim(self, nPts = 1000) :
    """
    todo!
    """
    print("todo")
    
    
    
