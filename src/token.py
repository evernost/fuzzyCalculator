# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : token
# File name       : token.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : token object
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# =============================================================================

# =============================================================================
# Description
# =============================================================================
#
# -----
# Notes
# -----
#  - pipe chars "|" cannot be used for abs value as they lead to ambiguity.
#    Solution needs to be found for that.
#    Example: |a + b|cos(x)|c + d|
#  - constants cannot contain an underscore (see [R5.9])
#
#
#
# ------------
# TODO / IDEAS
# ------------
# Sorted by increasing relative effort: 
# - add a pretty print for the 'binary tree' to check/debug the parser's interpretation
# - add support for scientific notation
# - add support for thousands delimitation using "_": "3_141_592" vs "3141592"
# - add support for special characters (pi?)
# - add support for infix like '.+'?
# - add support for complex numbers
# - add an interactive mode where: 
#   > a command prompt appears
#   > variables and their statistics can be typed in the CLI
#   > the tree is built as the user types in the expression for immediate feedback
#   > pipes "|" are automatically translated to "abs("
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
# None.



# =============================================================================
# Constant pool
# =============================================================================
# Warning: underscores in the name are not allowed (rule [R5.10] of the parser)
CONSTANTS = [
  {"name": "pi" , "value": 3.14159265358979},
  {"name": "i",   "value": 0.0},
  {"name": "eps", "value": 0.0},
  {"name": "inf", "value": 0.0}
]

FUNCTIONS = [
  {"name": "id",    "nArgs": 1},
  {"name": "opp",   "nArgs": 1},
  {"name": "sin",   "nArgs": 1},
  {"name": "cos",   "nArgs": 1},
  {"name": "tan",   "nArgs": 1},
  {"name": "exp",   "nArgs": 1},
  {"name": "ln",    "nArgs": 1},
  {"name": "log10", "nArgs": 1},
  {"name": "logN",  "nArgs": 2},
  {"name": "abs",   "nArgs": 1},
  {"name": "sqrt",  "nArgs": 1},
  {"name": "floor", "nArgs": 1},
  {"name": "ceil",  "nArgs": 1},
  {"name": "round", "nArgs": 1},
  {"name": "Q",     "nArgs": 2},
  {"name": "sinc",  "nArgs": 1}
]

INFIX_OPS = [
  {"name": "+",  "priority": 1},
  {"name": "-",  "priority": 1},
  {"name": "*",  "priority": 2},
  {"name": "/",  "priority": 2},
  {"name": "//", "priority": 2},
  {"name": "^",  "priority": 3}
]



class Token :

  # ---------------------------------------------------------------------------
  # METHOD: Token.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, name, value = 0) :
    """
    DESCRIPTION
    Takes an expression as argument, returns a Token object whose type matches
    with the expression.

    Tokens can be of type: 
    - CONSTANT
    - FUNCTION
    - TODO

    EXAMPLES
    Token("4.5")  -> creates a Token of type "NUMBER"
    Token("pi")   -> creates a Token of type "CONSTANT"
    Token("exp")  -> creates a Token of type "FUNCTION"
    Etc.
    """
    self.constantsList = [x["name"] for x in Token.CONSTANTS]
    self.functionsList = [x["name"] for x in Token.FUNCTIONS]
    self.infixOpsList  = [x["name"] for x in Token.INFIX_OPS]
    
    if (name in self.constantsList) :
      self.type = "CONSTANT"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"CONST:'{name}'"

    elif (name in self.functionsList) :
      self.type = "FUNCTION"
      self.name = name
      self.dispStr = f"FCT:'{name}'"
      
      for f in Token.FUNCTIONS :
        if (name == f["name"]) :
          self.nArgs = f["nArgs"]

    elif (name in self.infixOpsList) :
      self.type = "INFIX"
      self.name = name
      self.nArgs = 2
      self.dispStr = f"OP:'{name}'"

    elif (checkVariableSyntax(name)) :
      self.type = "VAR"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"VAR:'{name}'"

    elif (name == "(") :
      self.type = "BRKT_OPEN"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"BRKT:'('"

    elif (name == ")") :
      self.type = "BRKT_CLOSE"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"BRKT:')'"

    elif (name == ",") :
      self.type = "COMMA"
      self.name = name
      self.dispStr = f"SEP:','"

    elif (isNumber(name)) :
      self.type = "NUMBER"
      self.name = name
      self.dispStr = f"NUM:'{name}'"

    elif (isBlank(name)) :
      self.type = "SPACE"
      self.name = name
      self.dispStr = f"BLK:'{name}'"

    else :
      print("[ERROR] Invalid token!")



  # ---------------------------------------------------------------------------
  # METHOD: Token.__str__ (print overloading)
  # ---------------------------------------------------------------------------

  # Define the behaviour of print(tokenObj)
  def __str__(self) :
    return self.dispStr
  
  # Define the behaviour of print([tokenObj1, tokenObj2])
  def __repr__(self):
    return self.dispStr

