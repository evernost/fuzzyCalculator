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
from src.commons import Status

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
  {"name": "si",    "nArgs": 1, "dispStr": "FOR TEST PURPOSES - DO NOT USE"},
  {"name": "fct3",  "nArgs": 3, "dispStr": "FOR TEST PURPOSES - DO NOT USE"},
  {"name": "fct4",  "nArgs": 4, "dispStr": "FOR TEST PURPOSES - DO NOT USE"}
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
      self.dispStr  = f"COMMA:','"

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

    # Populated after calling "_read()"
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
    self.statusArgs = self._read(tokens)
    self.statusNest = Status.NOT_RUN



  # ---------------------------------------------------------------------------
  # METHOD: Macro._read()                                             [PRIVATE]
  # ---------------------------------------------------------------------------
  def _read(self, tokens) -> Status :
    """
    Consumes all the tokens, assigns them to the list of argument(s) if the 
    Macro is a function.
    The rest is stored in 'Macro.remainder' for further processing.

    The function returns 'Status.OK' if the Macro creation is successful, 
    'Status.FAIL' otherwise.

    NOTE: the arguments themselves are automatically nested. 
    Therefore, a macro does not have a 'nest' method that needs to be called.
    Creating a Macro occurs during the nesting process anyway.  
    """
    
    nTokens = len(tokens)

    # CASE 1: process an empty input
    if (nTokens == 0) :
      if not(self.QUIET_MODE) : print("[ERROR] Macro._read(): void list of tokens (possible internal error)")
      return Status.FAIL

    # CASE 2: process N > 1 tokens
    elif (nTokens >= 1) :
      
      # CASE 2.1: Function Macro
      if (tokens[0].type == "FUNCTION") :
        self.function     = tokens[0]
        self.nArgs        = nArgsFromFunctionName(self.function.id)
        tokensWithoutFunc = tokens[2:]

        # Parse the arguments
        for i in range(self.nArgs) :
          
          # Consume and append all the tokens for this argument
          (arg, rem) = self._consumeArg(tokensWithoutFunc)
          self.args.append(arg)
          
          # TODO!!
          # At this point, 'rem' might contain a leftover closing parenthesis
          # This case needs to be handled

          # Is there anything left?
          if rem :

            # 1 TOKEN LEFT IN REMAINDER
            # - Case 1: closing parenthesis
            #   The function/bracket is terminated in the most natural way.
            #   Check if this is compatible with the number of arguments the function expects!
            # - Case 2: anything else
            #   That's probably an error considering what lead to exiting the arg consumption
            if (len(rem) == 1) :
              if (rem[0].type != "BRKT_CLOSE") :
                self.remainder = []
              else :
                print("[ERROR] Macro._read(): possible error case")

            # 2 OR MORE TOKENS LEFT IN REMAINDER
            # - Case 1: ')' + ','
            #   The parenthesis closes the current context
            #   (it's the only possibility actually)
            # - Case 2: ')' + '...' (not a comma)
            #   TODO!
            # - Case 3: ',' + ...
            #   TODO!
            else :

              if (rem[0].type == "BRKT_CLOSE") :
                if (rem[1].type == "COMMA") :
                  if ((i+2) <= self.nArgs) :
                    tokensWithoutFunc = rem[1:]
                  else :
                    if not(self.QUIET_MODE) : print(f"[ERROR] Macro._read(): '{self.function.id}' got too many arguments (expected: {self.nArgs})")
                    return Status.FAIL
                else :
                  print("TODO")

              elif (rem[0].type == "COMMA") :
                print("TODO")

              # # Comma: another argument comes next
              # if (rem[0].type == "COMMA") :
                
              #   # Does the function accept more than one argument?
              #   if (self.nArgs >= 2) :
                  
              #     # Trim the leading comma, and start the argument processing again
              #     if (i != (self.nArgs-1)) :
              #       tokensWithoutFunc = rem[1:]
              #     else :
              #       if not(self.QUIET_MODE) : print(f"[ERROR] Macro._read(): '{self.function.id}' got too many arguments (expected: {self.nArgs})")
              #       Status.FAIL
              #   else :
              #     if not(self.QUIET_MODE) : print(f"[ERROR] Macro._read(): '{self.function.id}' only takes 1 argument.")
              #     Status.FAIL

        #self.remainder = rem

      # CASE 2.2: Parenthesis Macro
      elif (tokens[0].type == "BRKT_OPEN") :
        (arg, rem) = parser.nestArg(tokens[1:])
        self.function = Token("id")
        self.nArgs = 1
        self.args.append(arg)
        self.remainder = rem

      # CASE 2.3: Anything else (-> error)
      else :
        if not(self.QUIET_MODE) : print("[ERROR] Macro._read(): the list of tokens must begin with a parenthesis or a function (possible internal error)")
        return Status.FAIL


    # STEP 2: explicit the zeros in the 'opposite' operation
    for arg in self.args :
      arg = parser.explicitZerosWeak(arg)

    # STEP 3: check the nesting
    for arg in self.args :
      ret = parser.nestCheck(arg)
      
      # TODO: set as status the worst status encountered
      if (ret != Status.OK) :
        self.statusNest = Status.FAIL

    return Status.OK



  # -----------------------------------------------------------------------------
  # METHOD: Macro._consumeArg()                                         [PRIVATE]
  # -----------------------------------------------------------------------------
  def _consumeArg(self, tokenList) :
    """
    Weaker version of parser.nest() that processes the content (or arguments) of
    specific elements:
    - function content
    - parenthesis content
    You must get rid of the opening parenthesis (and the function name in case 
    of a function) before calling this function.

    In a nutshell, this function extracts the content of a function/parenthesis.
        
    Like 'nest()', the function returns a nested list of tokens.

    Unlike 'nest()', it halts on ',' and ')' and returns the remainder.
    Therefore, the returned objects is the tuple (T, rem) with:
    - T: the content of the parenthesis/function (as list of tokens)
    - rem: the remainder (as list of tokens)

    'nest()' consumes all the tokens, hence it does not return a remainder.
    'nestArg()' must stop when the argument processing is done.
    """
    
    nTokens = len(tokenList)

    # CASE 1: consume args in an empty list of tokens
    if (nTokens == 0) :
      return ([], [])

    # CASE 2: consume args in a single token
    elif (nTokens == 1) :
      if tokenList[0].type in ("BRKT_OPEN", "BRKT_CLOSE", "FUNCTION") :
        print("[WARNING] Macro._consumeArg(): odd input (single meaningless token)")
        return (tokenList, [])
      else :
        return (tokenList, [])
    
    # CASE 3: consume args in the most general case
    else :
      (tokensFlat, remainder) = utils.consumeFlat(tokenList)

      # The list of token contains no more recursion or arguments: done!
      if not(remainder) :
        return (tokensFlat, [])

      else :
        
        # CASE 3.1: Opening parenthesis/Function in an argument
        # - Encapsulate the nested part in a Macro
        # - Consume the remainder with a call to '_consumeArg' itself
        if (remainder[0].type in ("BRKT_OPEN", "FUNCTION")) :
          M = Macro(remainder)
          rem = M.getRemainder()

          # Consume the remainder as if it were a regular argument
          (arg, rem) = self._consumeArg(rem)
          
          # Concatenate everything, return the outcome.
          return (tokensFlat + [M] + arg, rem)

        # CASE 3.2: Comma in an argument
        # The processing is done for this argument.
        # Another call to _consumeArg will be necessary after the return
        # to process the rest.
        # NOTE: the comma token is included in 'remainder' so that it is
        # easier to detect if there are too many arguments
        elif (remainder[0].type == "COMMA") :  
          if (len(remainder) >= 2) :
            return (tokensFlat, remainder)
          else :
            print("[WARNING] Macro._consumeArg(): possible missing argument")
            return (tokensFlat, [])

        # CASE 3.3: Closing parenthesis in argument
        # End of the processing, go up one level
        # NOTE: the closing parenthesis must be returned in the remainder,
        # otherwise it wouldn't be possible to distinguish 
        # '2x+3),...' and '2x+3),'
        elif (remainder[0].type == "BRKT_CLOSE") :
          return (tokensFlat, remainder)
        
        # CASE 3.4: Anything else
        # Any other token is an error.
        else :
          print("[WARNING] Macro._consumeArg(): possible uncaught syntax error (unexpected token)")
          return (tokensFlat, [])



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
  # def nest(self) -> Status :
  #   """
  #   Nests the list of tokens.

  #   Similar to Expression.nest(), but applied to the specific case of a 
  #   Macro.
  #   """

  #   self.statusNest = Status.OK

  #   for (i, _) in enumerate(self.args) :
  #     (self.args[i], status) = parser.nestProcessor(self.args[i])
  #     #status = parser.nestCheck(self.args[i])

  #     if (status != Status.OK) :
  #       self.statusNest = status

  #   return self.statusNest





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
  Checks all user-customisable declarations (constants, infixes, functions)
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


