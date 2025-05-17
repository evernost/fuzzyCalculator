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
  {"name": "^",  "priority": 3}   # Exponentiation must have the highest priority
]



# =============================================================================
# CLASS DEFINITION - TOKEN
# =============================================================================
class Token :

  """
  TOKEN class definition

  The constructor creates a Token object from a descriptor string.
  
  The string given as argument determines the type of token. 
  Type inference from a string is handy for the integration in the top level
  parser.

  The following list gives the different inference based on the input string:
  - name of a constant ('pi', 'i' etc.)         -> Token.type = 'CONSTANT'
  - name of a function ('sin', 'cos', etc.)     -> Token.type = 'FUNCTION'
  - name of a variable ('abc', 'x', 'R1', etc.) -> Token.type = 'VARIABLE'
  - number ('0.1', '-23', '010.8', etc.)        -> Token.type = 'NUMBER'
  - opening round bracket '('                   -> Token.type = 'BRKT_OPEN'
  - closing round bracket ')'                   -> Token.type = 'BRKT_CLOSE'
  - comma ','                                   -> Token.type = 'COMMA'
  - empty string ''                             -> reserved (used for macros)
  - space ' '                                   -> invalid (deprecated)

  Notes : for a function Token, the opening parenthesis must be omitted.

  EXAMPLES
  - Token("4.5")  -> creates a Token of type "NUMBER"
  - Token("pi")   -> creates a Token of type "CONSTANT"
  - Token("exp")  -> creates a Token of type "FUNCTION"
  """

  def __init__(self, s: str, quiet = False, verbose = False, debug = False) :

    # Constants
    self._initLists()

    # Options
    self.QUIET_MODE   = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE   = debug

    # Determine the type of token based on the input string
    self._readType(s)
    


  # ---------------------------------------------------------------------------
  # METHOD: Token._initLists()
  # ---------------------------------------------------------------------------
  def _initLists(self) -> None :
    """
    Initialises the internal references from the lists of constants.
    """

    self.listConstants  = [x["name"] for x in CONSTANTS]
    self.listFunctions  = [x["name"] for x in FUNCTIONS]
    self.listInfix      = [x["name"] for x in INFIX]



  # ---------------------------------------------------------------------------
  # METHOD: Token._readType()
  # ---------------------------------------------------------------------------
  def _readType(self, s: str) -> None :
    """
    TODO
    """

    if (s in self.listConstants) :
      for c in CONSTANTS :
        if (s == c["name"]) :
          self.type     = "CONSTANT"
          self.id       = s
          self.dispStr  = f"CONST:'{s}'"
          
    elif (s in self.listFunctions) :
      self.type     = "FUNCTION"
      self.id       = s
      self.dispStr  = f"FCT:'{s}'"

    elif (s in self.listInfix) :
      self.type     = "INFIX"
      self.id       = s
      self.dispStr  = f"OP:'{s}'"

    elif (s == "(") :
      self.type     = "BRKT_OPEN"
      self.id       = "("
      self.dispStr  = "'('"

    elif (s == ")") :
      self.type     = "BRKT_CLOSE"
      self.id       = ")"
      self.dispStr  = "')'"

    elif (s == ",") :
      self.type     = "COMMA"
      self.id       = ","
      self.dispStr  = f"SEP:','"

    elif utils.isNumber(s) :
      self.type     = "NUMBER"
      self.id       = s
      self.dispStr  = f"NUM:'{s}'"

    elif utils.isLegalVariableName(s) :
      self.type     = "VARIABLE"
      self.id       = s
      self.dispStr  = f"VAR:'{s}'"

    else :
      self.type     = "UNKNOWN"
      self.id       = s
      self.dispStr  = f"U:'{s}'"
      
      if not(self.QUIET_MODE) :
        print(f"[ERROR] Invalid token input: {s}")



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

  # def getOverviewStr(self) :
  #   """
  #   Returns a string with a pretty print of the content of the Token,
  #   so that it is readable when several of them a shown in a row.
  #   """
  #   return self.name



  # ---------------------------------------------------------------------------
  # METHOD: Token.__setattr__ (generic attribute setter)
  # ---------------------------------------------------------------------------
  # def __setattr__(self, attrName, attrValue):
  #   """
  #   Function is called every time an attribute is set.
  #   For the "number" Token, assigning 'value' automatically changes its name.
  #   """
    
  #   if (attrName == "value") :
  #     if (self.type == "NUMBER") :
  #       super().__setattr__("value", attrValue)
  #       super().__setattr__("name", str(attrValue))
  #       super().__setattr__("dispStr", f"NUM:'{attrValue}'")
  #     else :
  #       super().__setattr__(attrName, attrValue)

  #   else :
  #     super().__setattr__(attrName, attrValue)



# =============================================================================
# CLASS DEFINITION - MACRO
# =============================================================================
class Macro :

  """
  MACRO class definition

  A Macro object is 'super-Token' that abstracts content between round brackets
  or function calls.

  The constructor takes a list of Token objects as input. 
  It consumes all the tokens that fit into the macro expression, the rest is
  left aside in the 'Macro.remainder' attribute for further processing.

  Options: 
  - quiet mode  : turns off all outputs (even errors)
  - verbose mode: prints additional info relative to the parsing
  - debug mode  : prints extra info for investigation
  """

  def __init__(self, tokens, quiet = False, verbose = False, debug = False) :

    # Populated after calling "_consumeArgs()"
    self.function = None
    self.args = []
    self.nArgs = 0

    # Allows Macro object to be treated as a Token
    self.type = "MACRO"

    # Options
    self.QUIET_MODE   = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE   = debug

    self._consumeArgs(tokens)



  # ---------------------------------------------------------------------------
  # METHOD: Macro._consumeArgs()                                      [PRIVATE]
  # ---------------------------------------------------------------------------
  def _consumeArgs(self, tokens) -> None :
    """
    Consumes all the tokens that are part of the arguments of the function.
    The rest is stored in 'Macro.remainder' for futher processing.
    """
    
    nTokens = len(tokens)

    if (nTokens == 0) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Macro._consumeArgs(): void list of tokens (possible internal error)")

    elif (nTokens >= 1) :

      if (tokens[0].type == "FUNCTION") :
        (arg, rem) = utils.nestArg(tokens[2:])
        self.function = tokens[0]
        self.nArgs = nArgsFromFunctionName(self.function.id)
        self.args.append(arg)
        self.remainder = rem

      elif (tokens[0].type == "BRKT_OPEN") :
        (arg, rem) = utils.nestArg(tokens[2:])
        self.function = Token("id")
        self.nArgs = 1
        self.args.append(arg)
        self.remainder = rem

      else :
        if not(self.QUIET_MODE) :
          print("[ERROR] Macro._consumeArgs(): the list of tokens must begin with a parenthesis or a function (possible internal error)")



 




# -----------------------------------------------------------------------------
# FUNCTION: nArgsFromFunctionName(string)
# -----------------------------------------------------------------------------
def nArgsFromFunctionName(s: str) :
  """
  Returns the number of arguments taken by the function whose name is given as 
  argument.

  If no function is found, returns -1.
  """
  
  for f in FUNCTIONS :
    if (s == f["name"]) :
      return f["nArgs"]
  
  print(f"[WARNING] The function {s} could not be found.")
  return -1



# -----------------------------------------------------------------------------
# FUNCTION: _selfCheck()
# -----------------------------------------------------------------------------
def _selfCheck() :
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


  # TODO: detect illegal chars

  print("[INFO] symbols.py: end of auto-test.")



# =============================================================================
# START-UP CODE
# =============================================================================
_selfCheck()



# =============================================================================
# UNIT TESTS
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")
  
  assert(Token("pi"     , quiet=True).type == "CONSTANT")
  assert(Token(".1"     , quiet=True).type == "NUMBER")
  assert(Token("2.0"    , quiet=True).type == "NUMBER")
  assert(Token("0395"   , quiet=True).type == "NUMBER")
  assert(Token("("      , quiet=True).type == "BRKT_OPEN")
  assert(Token(")"      , quiet=True).type == "BRKT_CLOSE")
  assert(Token("x1_3"   , quiet=True).type == "VARIABLE")
  assert(Token(","      , quiet=True).type == "COMMA")
  assert(Token("exp"    , quiet=True).type == "FUNCTION")
  assert(Token("//"     , quiet=True).type == "INFIX")

  assert(Token("-0.9"   , quiet=True).type == "UNKNOWN")
  assert(Token(") "     , quiet=True).type == "UNKNOWN")
  assert(Token("sin("   , quiet=True).type == "UNKNOWN")
  print("- Unit test passed: Token type inference")


