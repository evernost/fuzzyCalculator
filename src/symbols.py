# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : symbols
# File name       : symbols.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : definition of the symbols accepted by the parser.
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# todo



# =============================================================================
# External libs
# =============================================================================
import utils



# =============================================================================
# Constant pool
# =============================================================================
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

INFIX = [
  {"name": "+",  "priority": 1},
  {"name": "-",  "priority": 1},
  {"name": "*",  "priority": 2},
  {"name": "/",  "priority": 2},
  {"name": "//", "priority": 2},
  {"name": "^",  "priority": 3}
]



# -----------------------------------------------------------------------------
# FUNCTION: nArgsFromFunctionName(string)
# -----------------------------------------------------------------------------
def nArgsFromFunctionName(inputStr) :
  """
  Returns the number of arguments taken by the function whose name is given as 
  argument.

  If no function is found, returns -1.
  """
  
  for f in FUNCTIONS :
    if (inputStr == f["name"]) :
      return f["nArgs"]
  
  print(f"[WARNING] The function {inputStr} could not be found.")
  return -1



class Token :

  # ---------------------------------------------------------------------------
  # METHOD: Token.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, name, value = None) :
    """
    DESCRIPTION
    Takes an expression as argument, returns a Token object.
    
    The Token has a 'type' that is inferred from the value passed as argument.

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
    self.constantsList  = [x["name"] for x in CONSTANTS]
    self.functionsList  = [x["name"] for x in FUNCTIONS]
    self.infixList      = [x["name"] for x in INFIX]
    
    if (name in self.constantsList) :
      self.type     = "CONSTANT"
      self.name     = name
      self.nArgs    = 0
      self.dispStr  = f"CONST:'{name}'"

    elif (name in self.functionsList) :
      self.type     = "FUNCTION"
      self.name     = name
      self.dispStr  = f"FCT:'{name}'"
      
      for f in FUNCTIONS :
        if (name == f["name"]) :
          self.nArgs = f["nArgs"]

    elif (name in self.infixList) :
      self.type     = "INFIX"
      self.name     = name
      self.nArgs    = 2
      self.dispStr  = f"OP:'{name}'"

    elif (utils.isLegalVariableName(name)) :
      self.type     = "VAR"
      self.name     = name
      self.nArgs    = 0
      self.dispStr  = f"VAR:'{name}'"
      self.value    = value

    elif (name == "(") :
      self.type     = "BRKT_OPEN"
      self.name     = name
      self.nArgs    = 0
      self.dispStr  = f"BRKT:'('"

    elif (name == ")") :
      self.type     = "BRKT_CLOSE"
      self.name     = name
      self.nArgs    = 0
      self.dispStr  = f"BRKT:')'"

    elif (name == ",") :
      self.type     = "COMMA"
      self.name     = name
      self.dispStr  = f"SEP:','"

    elif (utils.isNumber(name)) :
      self.type     = "NUMBER"
      self.name     = name
      self.dispStr  = f"NUM:'{name}'"

    elif (utils.isBlank(name)) :
      self.type     = "SPACE"
      self.name     = name
      self.dispStr  = f"BLK:'{name}'"

    else :
      print("[ERROR] Invalid token!")



  # ---------------------------------------------------------------------------
  # METHOD: Token.__str__ (print overloading)
  # ---------------------------------------------------------------------------
  def __str__(self) :
    """
    Defines the behaviour of print(tokenObj).
    """
    return self.dispStr
  
  
  
  def __repr__(self) :
    """
    Defines the behaviour of print([tokenObj1, tokenObj2])
    """
    return self.dispStr



# -----------------------------------------------------------------------------
# Main (unit tests)
# -----------------------------------------------------------------------------
if (__name__ == '__main__') :
  
  print("[INFO] No unit tests available for this library.")
