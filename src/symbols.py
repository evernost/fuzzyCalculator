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
# EXTERNALS
# =============================================================================
# Project libraries
import src.utils as utils
import src.parser as parser

# Standard libraries
import math



# =============================================================================
# CONSTANTS
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
    self._initRefs()

    # Options
    self.QUIET_MODE   = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE   = debug

    # Determine the type of token based on the input string
    self._readInputType(s)
    


  # ---------------------------------------------------------------------------
  # METHOD: Token._initRefs()                                         [PRIVATE]
  # ---------------------------------------------------------------------------
  def _initRefs(self) -> None :
    """
    Initialises the internal references from the lists of constants / functions
    and infix operators.
    """

    self.listConstants  = [x["name"] for x in CONSTANTS]
    self.listFunctions  = [x["name"] for x in FUNCTIONS]
    self.listInfix      = [x["name"] for x in INFIX]



  # ---------------------------------------------------------------------------
  # METHOD: Token._readInputType()                                    [PRIVATE]
  # ---------------------------------------------------------------------------
  def _readInputType(self, s: str) -> None :
    """
    Guesses the type of token from the string input.
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




# =============================================================================
# CLASS DEFINITION - MACRO
# =============================================================================
class Macro :

  """
  MACRO class definition

  A Macro object is 'super-Token' that abstracts content between round brackets
  (for precedence enforcement or as part of a function call).

  The constructor takes as input the list of Tokens where the Macro has to 
  start:
  - the function token + the opening parenthesis token for a function 
  - the opening parenthesis token for an expression between round brackets.

  The list of tokens must contain the entire the macro has to encapsulate. 
  All the tokens that fit into the macro expression will be consumed, the rest 
  is left aside in 'Macro.remainder' attribute for further processing (e.g. when 
  the parenthesis closes)

  For functions, all the arguments will be extracted and stored in a list
  of arguments.

  Macro generation is recursive: nested functions within the macro will create 
  their own macro etc. 

  Options: 
  - quiet mode  : turns off all outputs (even errors)
  - verbose mode: prints additional info relative to the parsing
  - debug mode  : prints extra info for investigation
  """

  def __init__(self, tokens, quiet = False, verbose = False, debug = False) :

    # Populated after calling "_consumeArgs()"
    self.function   = None    # Top-level function of the macro
    self.args       = []      # List of arguments
    self.nArgs      = 0       # Number of arguments
    self.remainder  = []      # Trailing tokens outside the scope of the function

    # Allows Macro object to be treated as a Token
    # TODO: make the Macro class inherit from the Token class?
    self.type = "MACRO"

    # Options
    self.QUIET_MODE   = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE   = debug

    # Populate the attributes
    self.statusArgs = self._consumeArgs(tokens)
    self.statusNest = False



  # ---------------------------------------------------------------------------
  # METHOD: Macro._consumeArgs()                                      [PRIVATE]
  # ---------------------------------------------------------------------------
  def _consumeArgs(self, tokens) -> bool :
    """
    Consumes all the tokens that are part of the argument(s) of the function.
    The rest is stored in 'Macro.remainder' for further processing.

    The function returns True if the Macro creation is successful, False
    otherwise.
    """
    
    nTokens = len(tokens)

    # CASE 1: empty input
    if (nTokens == 0) :
      if not(self.QUIET_MODE) : print("[ERROR] Macro._consumeArgs(): void list of tokens (possible internal error)")
      return False

    # CASE 2: general case
    elif (nTokens >= 1) :
      if (tokens[0].type == "FUNCTION") :
        self.function = tokens[0]
        self.nArgs = nArgsFromFunctionName(self.function.id)
        buff = tokens[2:]

        # Parse the arguments
        for i in range(self.nArgs) :
          (arg, rem) = parser.nestArg(buff)
          self.args.append(arg)
          
          # Is there a new argument?
          if rem :
            if (rem[0].type == "COMMA") :
              if (self.nArgs >= 2) :
                if (i != (self.nArgs-1)) :
                  buff = rem[1:]
                else :
                  if not(self.QUIET_MODE) : print(f"[ERROR] Macro._consumeArgs(): '{self.function.id}' got too many arguments (expected: {self.nArgs})")
                  return False
              else :
                if not(self.QUIET_MODE) : print(f"[ERROR] Macro._consumeArgs(): '{self.function.id}' only takes 1 argument.")
                return False

        self.remainder = rem

      elif (tokens[0].type == "BRKT_OPEN") :
        (arg, rem) = parser.nestArg(tokens[1:])
        self.function = Token("id")
        self.nArgs = 1
        self.args.append(arg)
        self.remainder = rem

      else :
        if not(self.QUIET_MODE) : print("[ERROR] Macro._consumeArgs(): the list of tokens must begin with a parenthesis or a function (possible internal error)")
        return False


      # STEP 2: explicit the zeros in the 'opposite' operation
      for arg in self.args :
        arg = parser.explicitZerosWeak(arg)

      return True



  # ---------------------------------------------------------------------------
  # METHOD: Macro.getRemainder()
  # ---------------------------------------------------------------------------
  def getRemainder(self) :
    """
    Returns the remainder i.e. all tokens that are not part of the macro.
    'Macro.remainder' is cleared after the call (remainder is used only once)
    """
    
    rem = self.remainder
    self.remainder = []
    
    return rem
    


  # ---------------------------------------------------------------------------
  # METHOD: Macro.nest()
  # ---------------------------------------------------------------------------
  def nest(self) -> bool :
    """
    Nests the list of tokens.

    Similar to Expression.nest(), but applied to the specific case of a 
    Macro.
    """

    # Note: nest() and nestCheck() are externalised because they are shared
    # with the Macro object.
    #self.tokens     = utils.nest(self.tokens)
    for arg in self.args :
      self.tokens = parser.nestProcessor(self.tokens)
      self.statusNest = parser.nestCheck(self.tokens)

    return self.statusNest



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
  
  print(f"[WARNING] Impossible to get 'nArgs': the function {s} could not be found.")
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
  assert(Token("0"      , quiet=True).type == "NUMBER")
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


