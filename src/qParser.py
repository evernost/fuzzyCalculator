# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : qParser
# File name       : qParser.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : built-in parser for the Fuzzy Calculator
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : Saturday, 1 June 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Parser/evaluator for math expression.
#  
# It supports "natural" inputs (e.g. implicit multiplications) and lazy 
# parenthesis.
# Expressions like "(a+b)(c-d)" or "sin(x+cos(y" are valid.
#
# It is based on native Python and does not require any specific library:
# - no regex
# - no complex string manipulation
# 
# However, if transcription to another programming language is needed, 
# the following features would be nice to have:
# - OOP 
# - string to float conversion
# - the math functions you want to support (sin, cos, exp, etc.)
# - random number generation for the Monte-Carlo analysis
# - some plotting features
#
# The calculator provides the most common math operators ('+', '-', '*', '/', '^') 
# and some obscure ones ('//' for parallel resistor association)
# Usual math functions are included (sin, cos, log, exp, abs, ...) 
#
# The parser preserves the order of the input while evaluating, therefore 
# it does not assume commutativity of infix like '+', '*' etc. 
# This could allow to extend the parser to other types, like matrices.
#
# When called as a 'main', the library runs unit tests on the built-in
# parsing functions.
#
#
#
# The following gives the parsing strategy and lists all rules that apply 
# when evaluating an expression.
# 
# -------------
# PARSING RULES
# -------------
# [R1] CASE SENSITIVE
# Parser is case sensitive.
#
# [R2] CONSTANT/VARIABLE/FUNCTION NAME PREFIXING
# The name of a function/variable/constant cannot start with a number.
# It would be impossible to tell if it's a variable or an implicit
# product between a number and a variable.
#
# [R3] FUNCTION CALL SYNTAX
# No space is accepted between the function name and the parenthesis.
# It makes the parsing trickier, and there is no added value.
# "exp(-2t)" -> OK
# "cos (3x)" -> rejected
#
# [R4] VOID ARGUMENTS
# Function cannot be called with empty arguments.
#
# [R5] IMPLICIT MULTIPLICATION RULES
# The following priorities have been defined based on what feels 
# the most "natural" interpretation. 
# In case of ambiguity, a warning is raised.
# [R5.1] "pixel"      -> var("pixel")             The variable as a whole is more likely than a product of smaller variables/const.
#                                                 Why not even "p*i*x*e*l", "pi*x*e*l", "p*ixel", etc.
#
# Rules for prefixing digit/number:
# [R5.2]  "1X"        -> 1*var("X")               A variable cannot start with a digit (rule R2)
# [R5.3]  "1_X"       -> 1*var("_X")              Same as R5.2
# [R5.4]  "1.0X"      -> 1.0*var("X")             Same as R5.2
# [R5.5]  "1.0_X"     -> 1.0*var("_X")            Same as R5.2
#
# Rules for suffixing digit/number:
# [R5.6]  "X2"        -> var("X2")                Typical case of variable suffixing.
# [R5.7]  "X_2"       -> var("X_2")               Same as R5.6
# [R5.8]  "X2.0       -> var("X")*2.0             | A decimal number interrupts the variable parsing.
#                                                 | A bit odd, but it is probably the most plausible meaning.
#                                                 | Raises a warning.
# [R5.9]  "X_2.0      -> var("X_")*2.0            Same as R5.8
#
# Rules for suffixing digit/number (continued):
# [R5.10] "X3Y"       -> var("X3")*var("Y")       | If a variable contains a number, its name can only end with a digit.
#         "R10C2"     -> var("R10")*var("C2")     |
#         "C1cos("    -> var("C1")*cos(...        |
#         "X2cos+3"   -> syntax error!            "cos" is not called according to the rules for functions (R3)
# [R5.11] "X_3Y"      -> var("X_3")*var("Y")      | Same principle as [R5.10]
#         "v_21cos("  -> var("v_21")*cos(...      |
#         "X_2cos("   -> var("X_2")*cos(...       |
# [R5.12] "X2.0cos("  -> var("X")*2.0*cos(...     Consistent with R5.8
# [R5.13] "X_2.0cos(" -> var("X_")*2.0*cos(...    Consistent with R5.9
# [R5.14] "R1_Y*pi"   -> var("R1_Y")*pi           | An underscore allows more complex variable names, even after a digit.
#         "x_1_2_Y*4" -> var("x_1_2_Y")*4         | 
# [R5.15] "X_3.0_Y"    -> var("X_")*3.0*var("_Y") Raises a warning


# Consequences:
# "X_3.1Y" -> var("X_")*3.1"*var("Y")           Consequence of rule R5.9

# Behaviour not decided yet:
# [R5.__] "pi4X"   -> const("pi")*4*var("X")     ??
# [R5.__] "pi4.0X" -> const("pi")*4.0*var("X")   ??
# [R5.__] "pi_5"   -> var("pi_5")                Underscore serves as disembiguation/indexing and overrides the constant

# [R5.__] "pipi"   -> var("pipi")                If "pi*pi" was meant, maybe the user should make an effort here.
# [R5.__] "inf"    -> const("inf")               Parser tries to see as a whole in priority (so not "i*nf", "i" being a constant too)
#                                                See also [R5.10]
# [R5.__] "ipi"    -> var("ipi")                 Same as [R5.13]
#
# [R6] INFIX OPERATOR NAME
# The super common ones (+, -, /, *, ...) along with exotic ones ('//') are already included.
#
# Users are free to customise with their favorite infix if they really want to, 
# but some restrictions apply:
# - infix ops cannot be made of letters, digits, commas, dots: this would mess with the rest of the parsing.
#   Special characters are recommended: @, !, \, $, #, ...
#   Special characters can even be combined: '@*', '+!', ...
# - the special character(s) for your custom infix need to be added to the 'white list' in <sanityCheck>
# - the expected behaviour for this new infix operator needs to be defined.
#
# Infix operators that are not based on special characters will not be supported.
# There are no plans to accept inputs like 'x DONG y' or 'a SUPER+ b'.
# Reasons for that:
# - ruins the readability
# - special characters already give enough flexibility
# - exotic infix operators are not that common. It is not worth the engineering.
# - infix operators are 2 variables functions in disguise.
#   Multiargs functions are already supported and should be the reasonable choice here.
#
# Also, be careful when defining the priority of your new operator (see rules [R7.X] and [R11])
#
# [R7] OMITTED TOKEN RULES
# The infix operator "-" (minus sign) is the only operator that allows an implicit left operand.
# In other words, expressions like "(-3x+..." are accepted.
#
# There are not many cases where the implicit left operand is common and/or makes sense.
# It is mostly used:
# - to negate a number/constant/variable (rule [R7.1]) 
# - for negative exponents               (rule [R7.2])
#
# Based on that, the parser's strategy is the following:
# - "(-3*..."  -> add a leading 0: "(0-3*..."
# - "10^-4..." -> create a macroleaf with the 'opp' function: "10^M..."
#   with M : {f = opp, M = [Num:'4']}.
#   This should not have side effect with the rest of the expression
#   since '^' has the highest priority.
#   Keep that in mind when you define custom infix.
#
# When the '-' appears at the beginning of an expression or subexpression
# (like in a macroleaf) then rule [R7.1] applies.
#
# Otherwise, rule [R7.2] is applied.
# 
# [R7.2] is derived as rule [R7.3] when the infix is not '^' anymore. 
# Behaviour is the same but a warning is raised because the priority between 
# operations becomes ambiguous and the expression does not look 'natural'.
# Use of parenthesis is strongly recommended for both clarity and correctness.
#
# Examples: 
# - "(-5..." is valid                     (rule [7.1])
# - "...^-5" is valid (e.g. for '10^-4')  (rule [7.2])
# - "a^-3u" is be treated as "(a^(-3))*u" (rule [7.2])
#
# The following will raise a warning:
# - "...--4..." becomes "...-M..." with M = {f = opp, M = [Num:'4']}   (rule [7.3])
# - "...*-pi..." becomes "...*M..." with M = {f = opp, M = [Cst:'pi']} (rule [7.3])
#
# [R7.4] "(+4" is not accepted (implicit left operand is for minus sign only)
# [R7.5] "-*4" is not accepted
#
# Note: rule [7.1] only adds a zero and does not add parenthesis.
# This prevents "-x^2" to be turned into "(-x)^2", which is probably
# never what is really meant.
#
# [R8] VARIABLE NAMING
# Variable cannot start with a number.
#
# [R9] WHITE SPACES
# White spaces are not part of the syntax and are simply ignored.
#
# [R10] OPERATORS ASSOCIATIVITY
# Consecutive operators with identical priority are all treated 
# with increasing nesting level (i.e. the 'rightest the deepest'):
# - a+b+c+d -> a+(b+(c+d))
# - a/b/c   -> a/(b/c)
# - a//b//c -> a//(b//c)      (note: '//' is associative, parenthesis do not matter)
# - a^b^c^d -> a^(b^(c^d))    (people will complain anyway, no matter what convention is chosen)
# In doubt: check the output interpretation, add parenthesis.
#
# [R11] OPERATORS PRECEDENCE
# It is not recommended to change the relative priorities of the basic infix
# operators: '+', '-', '*' , '/', '^'.
# - as far as I know, there is no real need for that
# - side effect will emerge due to the parsing strategy 
#   (e.g. rule [R7.2]: '^' is assumed to have the highest precedence for proper operation)
#
# Also, be careful when defining priority of custom infix: think twice about 
# how it interacts with other infix.
# Again, in doubt: use parenthesis and don't blindly rely on precedence. Parenthesis are free!
#
# Priority level is limited to 100 (arbitrary limit)
#



# =============================================================================
# External libs
# =============================================================================
from src.commons import *

import src.binary as binary
import src.symbols as symbols
import src.utils as utils


import numpy as np



# =============================================================================
# Constants pool
# =============================================================================
VERBOSE_MODE = True
DEBUG_MODE = False



# =============================================================================
# Main code
# =============================================================================


# -----------------------------------------------------------------------------
# FUNCTION: reservedWordsCheck(string)
# -----------------------------------------------------------------------------
def reservedWordsCheck(inputStr) :
  """
  Checks if reserved words (like function names, constants) are used incorrectly.
  
  EXAMPLES
  (See unit tests in "main")
  """
  
  # Input guard
  assert isinstance(inputStr, str), "'reservedWordsCheck' expects a string as an input."

  print("TODO")
  return True




# -----------------------------------------------------------------------------
# FUNCTION: getVariables(tokenList)
# -----------------------------------------------------------------------------
def getVariables(tokenList) :
  """
  Inspects the list of Tokens given as input and returns the list of variables
  that were found.
  """

  varList = []

  for t in tokenList :
    if (t.type == "VAR") :
      #print(f"[DEBUG] Variable found by the parser: '{t.name}'")
      if not(t.name in varList) :
        varList.append(t.name)

  return varList



# -----------------------------------------------------------------------------
# FUNCTION: secondOrderCheck(tokenList)
# -----------------------------------------------------------------------------
def secondOrderCheck(tokenList) :
  """
  DESCRIPTION
  Takes the tokens 2 by 2 from the list of Tokens and detects any invalid combination.
  Detailed list can be found in "resources/secondOrderCheck.xslx"
  
  It is a complement to "firstOrderCheck".
  Some checks are easier to do on the list of tokens rather than the raw input expression.
  
  EXAMPLES
  todo
  """

  nTokens = len(tokenList)

  for i in range(nTokens-1) :
    
    T1 = tokenList[i]; T2 = tokenList[i+1]

    if (T1.type == "FUNCTION") :
      if not(T2.type == "BRKT_OPEN") :
        print(f"[ERROR] A function must be followed with a parenthesis (Rule R3).")
        return CHECK_FAILED      
      else :
        pass
    
    
    # 
    # TODO: this section needs to be completed.
    # 


  T = tokenList[nTokens-1]
  if (T.type == "FUNCTION") :
    print(f"[ERROR] An expression cannot end with a function.")
    return CHECK_FAILED

  elif (T.type == "BRKT_OPEN") :
    print(f"[ERROR] An expression cannot end with an opening parenthesis.")
    return CHECK_FAILED
  
  elif (T.type == "INFIX") :
    print(f"[ERROR] An expression cannot end with an infix operator.")
    return CHECK_FAILED



  return CHECK_SUCCESS




# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")
  print()

  # Disable the babbling mode while doing the unit tests
  VERBOSE_MODE = False


  
  # TODO: check some tokenisations
  tokenList = [
    "1X",
    "3.14X",
    "1_x",
    "1.0_x",
    "R1",
    "R_1",
    "R1.0",
    "R_1.0",
    "1+2*pi*R1C1cos(x/7.1)"
  ]
  print("- TODO: <tokenise>")
  
  # TODO: trigger all the error cases in "secondOrderCheck"
  # secondOrderCheck([Token("sin")])
  print("- TODO: 'secondOrderCheck'")
  
  print()
  
  # Restore the babbling mode
  VERBOSE_MODE = True

  testVect = [
    ("1-2+3-4",           1-2+3-4),
    ("-1-2-3",            -1-2-3),
    ("-1+4(2-1",          -1+4*(2-1)),
    ("-1-6(-2-1",         -1-6*(-2-1)),
    ("-(4+1)*2-3*7",      (-(4+1)*2)-(3*7)),
    ("2^3^4",             (2**3)**4),
    ("2^-1+2",            (2**(-1))+2),
    ("1*2-3*4",           1*2-3*4),
    ("-1*2-3*4",          -1*2-3*4),
    ("(1+2)(3+4)",        (1+2)*(3+4)),
    ("(1+2)(3+4)(5-6",    (1+2)*(3+4)*(5-6)),
    ("-(1+2)(3+4)",       -(1+2)*(3+4)),
    ("-(1/16)^-1/2",      -(16/2)),
    ("-(1/16)^(-1/2)",    -4),
    ("12//100",           12*100/(12+100)),
    ("4.7 + 10//100",     4.7+(10*100/(10+100))),
    ("-(-3+9)/(1+2)",     -(-3+9)/(1+2)),
    ("-2cos(1.5pi)",      -2*np.cos(1.5*np.pi)),
    ("3cos(2*pi/10)",     3*np.cos(2*np.pi/10)),
    ("-abs(-15*7)/5",     -105/5),
    ("sin(2*pi*0.1",      np.sin(2*np.pi*0.1)),
    ("1.0//2.5",          1.0*2.5/(1.0+2.5)),
    ("10//100+1",         ((10*100)/(10+100)) + 1),
    ("1+cos(exp(pi*3))",  1 + np.cos(np.exp(3*np.pi))),
    ("1+cos(exp(pi*3))/tan(0.1/2)", 1 + np.cos(np.exp(3*np.pi))/np.tan(0.1/2))
  ]

  for (n, vect) in enumerate(testVect) :
    
    (expr, val) = vect

    print(f"----- Test vector {n}: '{expr}' -----")

    # STEP 1: rewrite the expression as a list of tokens
    tokenList = tokenise(expr)
    
    # STEP 2: detect and add the implicit multiplication tokens
    tokenListFull = explicitMult(tokenList)
    
    # STEP 3: create a binary object from the list of tokens
    B = binary.Binary(tokenListFull)
  
    # STEP 4: group and nest operators with higher precedence
    B.nest()
    
    # STEP 6: evaluate!
    out = B.eval()

    print(f"Tokens          : {tokenList}")
    print(f"Tokens with mult: {tokenListFull}")
    print(f"Binary          : {B}")
    print(f"output          : {out}")
    print(f"expected        : {val}")
    print()


