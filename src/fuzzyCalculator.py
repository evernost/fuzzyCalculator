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
import src.expression as expression
import src.qParser as qParser
import src.variable as variable

from enum import Enum
import statistics
import matplotlib.pyplot as plt

import numpy as np    # For percentile estimation



# =============================================================================
# Constants pool
# =============================================================================
class CalcStatus(Enum) :
  INIT            = 0
  COMPILE_OK      = 1
  COMPILE_FAILED  = 2
  SIM_OK          = 3



# =============================================================================
# Class definition
# =============================================================================
class Calc :
  
  # ---------------------------------------------------------------------------
  # METHOD: Calc.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self) :
    self.expr   = None
    self.status = CalcStatus.INIT

    self.output = []

    self.binary = None

    self.varNamesDeclared  = []
    self.varNamesDetected  = []
    self.vars = []

    self.exprHasVariables = False

    self.runs = 0

    

  # # ---------------------------------------------------------------------------
  # # METHOD: Calc._setInput(string)
  # # ---------------------------------------------------------------------------
  # def _setInput(self, expr) :
  #   """
  #   Sets the expression to be analysed by the parser.
  #   As it is set, some first basic checks are run on the expression to make 
  #   sure it is valid before proceeding any further.
  #   """

  #   self.expr = expr
    
  #   checkPassed = qParser.sanityCheck(self.expr)
  #   if not(checkPassed) :
  #     print("[ERROR] Parser halted due to an error in the sanity check.")
  #     exit()
      
  #   checkPassed = qParser.bracketBalanceCheck(self.expr)
  #   if not(checkPassed) :
  #     print("[ERROR] Parser halted due to an error in the bracket balance.")
  #     exit()
      
  #   checkPassed = qParser.firstOrderCheck(self.expr)
  #   if not(checkPassed) :
  #     print("[ERROR] Parser halted due to an error in the first order check.")
  #     exit()

  #   # print(f"[INFO] Calculator: input set to '{self.expr}'")



  # ---------------------------------------------------------------------------
  # METHOD: Calc.compile()
  # ---------------------------------------------------------------------------
  def compile(self, input) :
    """
    Compiles the expression in the input string.
    The compilation process consists in the following:
    - STEP 1: basic syntax check
    - STEP 2: rewrite as a list of tokens
    - STEP 3: detect and add the implicit multiplication tokens
    - STEP 4: binarise
    - STEP 5: isolate operators with higher precedence in a macro
    - STEP 6: list the variables detected in the expression
    - STEP 7: compare the detected variable against the declared variables
    - STEP 8: propagate the user-declared variables to the nested binary objects
    """

    # Create expression object
    self.expr = expression.Expression(input)

    # STEP 1: basic syntax check
    self.expr.check()

    # STEP 2: convert to a list of tokens
    self.expr.tokenise()
    
    # STEP 4: binarise
    self.binary = binary.Binary(tokensFull)
    if (self.binary.status == binary.BINARISE_FAILURE) :
      print("[ERROR] Compilation failed: unable to binarise.")
      exit()

    # STEP 5: embed higher priority operations in a Macroleaf (nesting)
    self.binary.nest()
    
    # STEP 6: list detected variables
    self.varNamesDetected += qParser.getVariables(tokensFull)
    self.exprHasVariables = (len(self.varNamesDetected) > 0)
    
    # STEP 7: check if all detected variables are declared
    ret = self._varDeclarationCheck()

    # STEP 8: propagate the user-declared variables to the internal nodes
    self.binary.setVariables(self.vars)

    # If the function made it up to here, compile is OK.
    self.status = CalcStatus.COMPILE_OK
    print("[INFO] Compile OK.")

    if not(self.exprHasVariables) :
      self.status = CalcStatus.SIM_OK
      #print("[DEBUG] Assuming simulation is already done (no variable detected)")



  # ---------------------------------------------------------------------------
  # METHOD: Calc.compileToVar(input, variable name)
  # ---------------------------------------------------------------------------
  def compileToVar(self, input, name) :
    """
    Compiles the expression contained in the input string and pack it 
    in a 'Variable' object so that it can be used in another expression.
    This process is referred to as 'expression composition'.
    
    The function returns a 'Variable' whose name attribute goes by 
    the one given in the 'name' argument.

    Compilation procedure in similar to the one in 'Calc.compile()'.
    """
    
    # STEP 1: first checks
    self._setInput(input)

    # STEP 2: tokenise
    self.tokens = qParser.tokenise(self.expr)
    
    # STEP 3: add implicit tokens (like multiplication)
    tokensFull = qParser.explicitMult(self.tokens)
    
    # STEP 4: binarise
    self.binary = binary.Binary(tokensFull)
    if (self.binary.status == binary.BINARISE_FAILURE) :
      print("[ERROR] compileToVar: compilation failed (cause: unable to binarise)")
      exit()

    # STEP 5: embed higher priority operations in a Macroleaf (nesting)
    self.binary.nest()
    
    # STEP 6: list detected variables
    self.varNamesDetected += qParser.getVariables(tokensFull)
    self.exprHasVariables = (len(self.varNamesDetected) > 0)
    
    # STEP 7: check if all detected variables are declared
    ret = self._varDeclarationCheck(ignoreUnused = True)

    # STEP 8: propagate the user-declared variables to the internal nodes
    self.binary.setVariables(self.vars)

    # If the function made it up to here, compile is OK.
    self.status = CalcStatus.COMPILE_OK
    print("[INFO] Compile OK.")

    if not(self.exprHasVariables) :
      self.status = CalcStatus.SIM_OK
      #print("[DEBUG] Assuming simulation is already done (no variable detected)")

    varObj = variable.CompiledVariable(name, self.binary)

    # Declare the variable
    self.declare(varObj)



  # ---------------------------------------------------------------------------
  # METHOD: Calc.declare('variable' Object / list of 'variable' Object)
  # ---------------------------------------------------------------------------
  def declare(self, vars) :
    """
    Declares a variable to the compiler.
    'var' must be a Variable Object.
    Variable can be either a single variable object, or a list of them.
    """
    
    if isinstance(vars, list) :
      for v in vars :
        if not(v.name in self.varNamesDeclared) :
          self.varNamesDeclared.append(v.name)
          self.vars.append(v)
        else :
          print(f"[INFO] Calc.declare(): skipping declaration of '{v.name}' (already declared)")
      
    else :
      if not(vars.name in self.varNamesDeclared) :
        self.varNamesDeclared.append(vars.name)
        self.vars.append(vars)
      else :
        print(f"[INFO] Calc.declare(): skipping declaration of '{vars.name}' (already declared)")
      
    

  # ---------------------------------------------------------------------------
  # METHOD: Calc._varDeclarationCheck()
  # ---------------------------------------------------------------------------
  def _varDeclarationCheck(self, ignoreUnused = False) :
    """
    Checks that all the variables detected in the expression are declared.
    Returns a warning if variables are declared but not detected.
    """
    
    ret = True
    for varDec in self.varNamesDeclared :
      if not(varDec in self.varNamesDetected) :
        if not(ignoreUnused) :
          print(f"[WARNING] Variable is declared, but not used/detected: '{varDec}'")

    for varDet in self.varNamesDetected :
      if not(varDet in self.varNamesDeclared) :
        print(f"[ERROR] Undeclared variable: '{varDet}'")
        exit()
        ret = False

    return ret



  # ---------------------------------------------------------------------------
  # METHOD: Calc.clearCache()
  # ---------------------------------------------------------------------------
  def clearCache(self) :
    """
    Clears the cache for all variables.
    
    Within one simulation, the call to 'eval()' of a given variable always
    returns the same value. This preserves consistency of the variable value
    accross possible multiple occurences of it in the same expression.
    Example: expr = "a+a", you don't want to draw 2 different values for 'a'.
    So the first call is evaluated, the second is read from cache.
    
    When the expression has been fully evaluated, 'eval()' must return
    a fresh new value i.e. cache must be cleared. 
    """
    
    for v in self.vars :
      v.clearCache()


    
  # ---------------------------------------------------------------------------
  # METHOD: Calc.sim()
  # ---------------------------------------------------------------------------
  def sim(self, runs = 1000, mode = "MIN_MAX", seed = 0) :
    """
    Runs the Monte-Carlo simulation of the compiled expression.
    """
    
    self.output = []
    for n in range(runs) :
      ret = self.binary.eval()
      self.output.append(ret)
      self.clearCache()

      if (n == 0) :
        outMin = ret
        outMax = ret
      
      else :
        if (ret < outMin) :
          outMin = ret

        if (ret > outMax) :
          outMax = ret

    self.status = CalcStatus.SIM_OK
    print(f"[INFO] Simulation done (runs: {runs})")



  # ---------------------------------------------------------------------------
  # METHOD: Calc.print()
  # ---------------------------------------------------------------------------
  def print(self, digits = 5) :
    """
    For a scalar expression (no variables): evaluates the expression, returns
    the result.
    
    For an expression with variables: shows a summary of the output.
    """
    
    if not((self.status == CalcStatus.COMPILE_OK) or (self.status == CalcStatus.SIM_OK)) :
      print("[ERROR] Please compile the expression using 'FuzzyCalculator.compile()' before a 'print()'.")
      exit()
    
    if (self.exprHasVariables) :
      if (self.status != CalcStatus.SIM_OK) :
        print("[WARNING] 'print()' without prior simulation shows only one possible outcome. Consider using 'sim()' for more detailed analysis.")
        out = self.binary.eval()
        print(f"[OUTPUT] {self.expr} = {out}")

      else :
        outMin = min(self.output); outMax = max(self.output)
        center = (outMin + outMax)/2; err = (outMax - outMin) / 2
        print(f"[OUTPUT] {self.expr} = {center:.{digits}} +/- {err:.{digits}} = [{outMin:.{digits}}, {outMax:.{digits}}]")
        print(f"         mean   = {statistics.mean(self.output)}")
        print(f"         std    = {statistics.stdev(self.output)}")
        print(f"         median = {statistics.median(self.output)}")

    else :      
      out = self.binary.eval()
      print(f"[OUTPUT] {self.expr} = {out:.{digits}}")



  # ---------------------------------------------------------------------------
  # METHOD: Calc.plot()
  # ---------------------------------------------------------------------------
  def plot(self, bins = 100, title = "") :
    """
    Plots the statistics of the expression.
    """
    
    if not((self.status == CalcStatus.COMPILE_OK) or (self.status == CalcStatus.SIM_OK)) :
      print("[ERROR] Please compile the expression using 'FuzzyCalculator.compile()' before a 'plot()'.")
      exit()
    
    if (self.exprHasVariables) :
      if (self.status != CalcStatus.SIM_OK) :
        print("[WARNING] A simulation is required before a plot. Consider using 'sim()' before calling this function.")
        
      else :
        plt.hist(self.output, bins = bins, color = 'blue', edgecolor = 'black')

        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title(f"Simulation result for '{self.expr}'")
        # plt.show(block = False)
        plt.show()

    else :
      print("[WARNING] 'plot()' makes sense for expressions containing variables with uncertainties.")



  # ---------------------------------------------------------------------------
  # METHOD: Calc.percentileRange()
  # ---------------------------------------------------------------------------
  def percentileRange(self, p = 0.95) :
    """
    Returns the range that contains p% of the values returned by the simulation.
    The 'p' value defaults to 95%.
    """
    
    lowerBound = np.percentile(self.output, 100*(1-p))
    upperBound = np.percentile(self.output, 100*p)
    print(f"Percentile range ({100*p}%): [{lowerBound:.3f} ... {upperBound:.3f}]")



# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == "__main__") :
  print("[INFO] There are no unit tests available for 'fuzzyCalculator.py'")

