# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : symbols
# File name       : symbols.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : definition of the symbols accepted by the parser.
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# TODO



# =============================================================================
# External libs
# =============================================================================
import src.utils as utils

import math



# =============================================================================
# Constant pool
# =============================================================================
CONSTANTS = [
  {"name": "pi" , "value": math.pi},
  {"name": "i",   "value": 0.0},
  {"name": "eps", "value": 0.0},
  {"name": "inf", "value": 0.0}
]

FUNCTIONS = [
  {"name": "id",    "nArgs": 1, "dispStr": "Identity"},
  {"name": "opp",   "nArgs": 1, "dispStr": "Opposite"},
  {"name": "sin",   "nArgs": 1, "dispStr": "Sine"},
  {"name": "cos",   "nArgs": 1, "dispStr": "Cosine"},
  {"name": "tan",   "nArgs": 1, "dispStr": "Tangent"},
  {"name": "exp",   "nArgs": 1, "dispStr": "Exponential"},
  {"name": "ln",    "nArgs": 1, "dispStr": "Natural log"},
  {"name": "log10", "nArgs": 1, "dispStr": "Log base 10"},
  {"name": "logN",  "nArgs": 2, "dispStr": "Log base N"},
  {"name": "abs",   "nArgs": 1, "dispStr": "Abs value"},
  {"name": "sqrt",  "nArgs": 1, "dispStr": "Square root"},
  {"name": "floor", "nArgs": 1, "dispStr": "Floor"},
  {"name": "ceil",  "nArgs": 1, "dispStr": "Ceil"},
  {"name": "round", "nArgs": 1, "dispStr": "Round"},
  {"name": "Q",     "nArgs": 2, "dispStr": "Quantise"},
  {"name": "sinc",  "nArgs": 1, "dispStr": "Sinc"},
  {"name": "si",    "nArgs": 1, "dispStr": "FOR TEST PURPOSES - DO NOT USE"}
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




# -----------------------------------------------------------------------------
# FUNCTION: _autoTest()
# -----------------------------------------------------------------------------
def _autoTest() :
  """
  Checks all user-customisable declarations
  """
  
  # Look for duplicate definitions in 'CONSTANTS'
  constList = [c["name"] for c in CONSTANTS]
  if (len(constList) != len(set(constList))) :
    print("[WARNING] Symbols auto-test: found duplicate in the list of constants.")

  # Look for duplicate definitions in 'FUNCTIONS'
  funcList = [f["name"] for f in FUNCTIONS]
  if (len(funcList) != len(set(funcList))) :
    print("[WARNING] Symbols auto-test: found duplicate in the list of functions.")

  # Look for duplicate definitions in 'INFIX'
  infixList = [i["name"] for i in INFIX]
  if (len(infixList) != len(set(infixList))) :
    print("[WARNING] Symbols auto-test: found duplicate in the list of infix.")

  print("[INFO] symbols.py: end of auto-test.")



# -----------------------------------------------------------------------------
# TOKEN CLASS DEFINITION
# -----------------------------------------------------------------------------
class Token :


  def __init__(self, name, value = None) :
    """
    DESCRIPTION
    Creates a Token object from an atomic expression.
    
    EXAMPLES
    Token("4.5")  -> creates a Token of type "NUMBER"
    Token("pi")   -> creates a Token of type "CONSTANT"
    Token("exp")  -> creates a Token of type "FUNCTION"

    The Token has a 'type' that is inferred from the value passed as argument.

    Tokens can be of type: 
    - CONSTANT
    - FUNCTION
    - TODO    
    """

    self.constantsList  = [x["name"] for x in CONSTANTS]
    self.functionsList  = [x["name"] for x in FUNCTIONS]
    self.infixList      = [x["name"] for x in INFIX]
    
    if (name in self.constantsList) :
      self.type     = "CONSTANT"
      self.name     = name
      self.nArgs    = 0
      self.dispStr  = f"CONST:'{name}'"
      
      for c in CONSTANTS :
        if (name == c["name"]) :
          self.value = c["value"]
          if not(value is None) :
            print("[WARNING] Non-empty field for 'value' is ignored when creating a constant.")
          
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

      for i in INFIX :
        if (name == i["name"]) :
          self.priority = i["priority"]

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
      self.dispStr  = f"'('"

    elif (name == ")") :
      self.type     = "BRKT_CLOSE"
      self.name     = name
      self.nArgs    = 0
      self.dispStr  = f"')'"

    elif (name == ",") :
      self.type     = "COMMA"
      self.name     = name
      self.dispStr  = f"SEP:','"

    elif (utils.isNumber(name)) :
      self.type     = "NUMBER"
      self.name     = name
      self.dispStr  = f"NUM:'{name}'"
      self.value    = float(name)

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

  def getOverviewStr(self) :
    """
    Returns a string with a pretty print of the content of the Token,
    so that it is readable when several of them a shown in a row.
    """
    return self.name



  # ---------------------------------------------------------------------------
  # METHOD: Token.__setattr__ (generic attribute setter)
  # ---------------------------------------------------------------------------
  def __setattr__(self, attrName, attrValue):
    """
    Function is called every time an attribute is set.
    For the "number" Token, assigning 'value' automatically changes its name.
    """
    
    if (attrName == "value") :
      if (self.type == "NUMBER") :
        super().__setattr__("value", attrValue)
        super().__setattr__("name", str(attrValue))
        super().__setattr__("dispStr", f"NUM:'{attrValue}'")
      else :
        super().__setattr__(attrName, attrValue)

    else :
      super().__setattr__(attrName, attrValue)



# =============================================================================
# START-UP CODE
# =============================================================================
_autoTest()



# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  print("[INFO] Library called as main: running unit tests...")
  
  T1 = Token("x", -1.0)
  assert(T1.name == "x")
  assert(T1.value == -1.0)
  print("- Self-test passed: number token")

  T2 = Token("pi")
  assert(T2.value == math.pi)   # Comparing two floats like that is not very clean...
  T3 = Token("pi", -1.0)
  print("- Self-test passed: constant token")
  


