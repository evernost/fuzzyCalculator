# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : fuzzyCalculator
# File name       : fuzzyCalculator.py
# File type       : Python script (Python 3.10 or higher)
# Purpose         : a regular calculator, for scalars and intervals.
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
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
# In other words, instead of calculating with numbers, it runs the calculation
# over the entire range the variables can live.
#
# Behind the scenes, it runs a Monte-Carlo simulation by generating random 
# values according to the declared statistics of each variable at play.
#
# At the end of the day, not only it gives an idea of the min/max range of the
# expression, but also gives the probability for the output to live in a certain
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
# - implicit multiplications
# - lazy parenthesis
# So expressions like "(a+b)(c-d)" or "sin(x+cox(y" are perfectly legal.
#
# NOTE: the detailed parsing rules can be found in <parser.py>
#
# Declare the variables and their statistic (uniform in range, gaussian, etc.)
# configure the simulation settings and voilà.
#
# --------------------
# WHAT ELSE DO I NEED?
# --------------------
# In order to keep it easily portable for any target and/or programming language, 
# it is based on 'native' Python and does not require any specific library.
# In particular:
# - no regex
# - no complex string manipulation
#
# Only numpy/pyplotlib will be used at the end for the actual math and the plot.
#
# ---------------------------------
# WHAT OPERATIONS CAN I DO WITH IT?
# ---------------------------------
# The calculator grants the most classical math operators ('+', '-', '*', '/', '^') 
# and more obscure ones ('//' for parallel resistor association)
# Usual math functions are included (sin, cos, log, log10, exp, abs, ...) 
#
# Structure is quite flexible so it is possible to add custom functions
# and infix operators. 
# Refer to <parser.py> for more information about the limitations.
#
# ------------------------------
# WHAT FEATURES MIGHT COME NEXT? 
# ------------------------------
# The integrated parser tries to treat the inputs as 'placeholders' as much as 
# possible which gives flexibility for the manipulated objects.
# Future releases could handle fixed point numbers, integers, matrices, etc.
#
# It is worth mentionning that the built-in parser preserves the order of the input, 
# therefore it does not assume commutativity of infix like '+', '*', ... 
# which makes it possible to extend it to matrices, quaternions, etc.
#
# --------------
# ANYTHING ELSE?
# --------------
# - pipe chars "|" have been considered at some point as a shortcut for abs(), 
#   but it didn't happen as they lead to ambiguity.
#
#   Example: |a + b|cos(x)|c + d|
#
#   A solution needs to be found for that.
#
# ------------
# TODO / IDEAS
# ------------
# Sorted by increasing effort: 
# - delete the 'match' function to support even lower versions of Python
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
# ----
# Misc
# ---- 
# Python 3.10 is required for the pattern matching features.
# Pattern matching is used for cleaner code, but does not participate to 
# the actual parsing process.
#



# =============================================================================
# External libs
# =============================================================================
import parser
import variable




# I wrap the calls to the parser.
# I keep track of the variables declared
# I run the Monte-Carlo simulations






class Calc :
  
  # ---------------------------------------------------------------------------
  # METHOD: Calc.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self) :
    self.expr       = ""
    self.variables  = []


  # ---------------------------------------------------------------------------
  # METHOD: Calc.compile(string)
  # ---------------------------------------------------------------------------
  def compile(self, expr) :
  
    self.expr = expr
  
    ret = parser.sanityCheck(expr)
    ret = parser.bracketBalanceCheck(expr)
    ret = parser.firstOrderCheck(expr)
    
  
  
  