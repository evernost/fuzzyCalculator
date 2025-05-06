# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : macro
# File name       : macro.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : 'Macro' expression object definition
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : May 1st, 2025
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
import src.symbols as symbols
import src.utils as utils



# =============================================================================
# Class definition
# =============================================================================
class Macro(symbols.Token) : 
  
  """
  MACRO class definition

  A Macro object derives from the Token class.

  The function takes a list of 'Token' objects as input. 
  It consumes all the tokens that fit into the macro expression, the rest is
  left aside in the 'Macro.remainder' attribute for further processing.

  Options: 
  - quiet mode  : turns off all outputs (even errors)
  - verbose mode: prints additional info relative to the parsing
  - debug mode  : prints extra info for investigation
  """

  def __init__(self, tokens, quiet = False, verbose = False, debug = False) :
    
    # Populated after calling "_buildArgs()"
    self.function = None
    self.nArgs = 0
    self.remainder  = []

    # Allows Macro object to be treated as a Token
    self.type = "MACRO"

    # Options
    self.QUIET_MODE = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE = debug
    
    self._buildArgs(tokens)



  # # ---------------------------------------------------------------------------
  # # METHOD: Macroleaf.__init__ (constructor)
  # # ---------------------------------------------------------------------------
  # def __init__(self, function, tokenList) :
  #   """
  #   Creates and initializes a Macroleaf object from a function and a list of Tokens.
  #   It returns a Macroleaf object as output.

  #   The 'function' argument defines what function shall apply to the evaluation 
  #   of the internal Binary object.
  #   The argument expects the name of the function as a string.
  #   No need to create or pass a Token.

  #   Then, it processes "tokenList" essentially like "Binary" would.

  #   Examples:
  #   M = Macroleaf("exp", [Token1, Token2, Token3, ...])
  #   M = Macroleaf("cos", someOtherListOfTokens)
  #   etc.
  #   """

  #   self.function   = function
  #   self.nArgs      = symbols.nArgsFromFunctionName(function)
  #   self.args       = []
  #   self.remainder  = []
  #   self.type       = "MACRO"

  #   if (len(tokenList) == 0) :
  #     print("[WARNING] Trying to create a Macroleaf with an empty list of Tokens.")
      
  #   self.status = self._buildArgs(tokenList)



  # ---------------------------------------------------------------------------
  # METHOD: Macro._buildArgs()                                        [PRIVATE]
  # ---------------------------------------------------------------------------
  def _buildArgs(self, tokens) -> None :
    """
    TODO
    """
    
    nTokens = len(tokens)

    if (nTokens == 0) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Macro._buildArgs(): void list of tokens (possible internal error)")

    elif (nTokens >= 1) :
      if not(tokens[0].type in ("BRKT_OPEN", "FUNCTION")) :
        if not(self.QUIET_MODE) :
          print("[ERROR] Macro._buildArgs(): the list of tokens must begin with a parenthesis or a function (possible internal error)")

      else :
        if (tokens[0].type == "FUNCTION") :
          self.function = tokens[0]
          self.nArgs = tokens[0].nArgs
          buffer = tokens[2:]

        elif (tokens[0].type == "BRKT_OPEN") :
          self.function = symbols.Token("id")
          self.nArgs = tokens[0].nArgs

          (tokensFlat, tokensRecurse) = utils.consumeAtomic(tokens[1:])

          if (tokensRecurse[0].type == "COMMA") :
            print("[ERROR] Macro._buildArgs(): syntax error, encountered a comma in a context that is not a multi-argument function")
          elif (tokensRecurse[0].type == "BRKT_CLOSE") :
            pass
          






        for n in range(self.nArgs) :
          # Last argument flag
          lastArg = (n == self.nArgs-1)
          
          # Binarise the current buffer.
          # Binarisation stops automatically when encountering Tokens
          # meant for the next argument.
          self.args.append(binary.Binary(buffer, context = "MACRO"))
          ret = self.args[n].status
          
          # Binarisation failed: propagate the status to the upper level.
          if (ret == binary.BINARISE_FAILURE) :
            return binary.BINARISE_FAILURE
          
          # Binarisation terminated successfully.
          # But there is no token left to process, and the top function requires another argument.
          elif (not(lastArg) and (len(self.args[n].remainder) == 0)) :
            
            if (ret != binary.BINARISE_SUCCESS_WITH_REMAINDER) :
              print("[ERROR] Macroleaf._buildArgs(): binarisation returned an incorrect value.")
            
            print("[ERROR] Macroleaf._buildArgs(): arguments are expected, but there a no Tokens left to process.")
            return binary.BINARISE_FAILURE
          
          # Binarisation terminated successfully. 
          # The remainder of the Binary object in the current argument is cleared
          # and transferred to the next argument.
          else :
            buffer = self.args[n].remainder
            self.args[n].remainder = []
            
            if lastArg :
              self.remainder = buffer





  # -----------------------------------------------------------------------------
  # METHOD: Macroleaf.sanityCheck()
  # -----------------------------------------------------------------------------
  def sanityCheck(self) :
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """

    print("[WARNING] Macroleaf.sanityCheck() is todo!")



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.nest()
  # ---------------------------------------------------------------------------
  def nest(self) :
    """
    Calls the "nest()" method of each Binary object in the "args" list.
    """

    for n in range(self.nArgs) :
      # print(f"[DEBUG] Macroleaf.nest(): nesting argument {n+1}/{self.nArgs}...")
      self.args[n].nest()



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.setVariables()
  # ---------------------------------------------------------------------------
  def setVariables(self, variables) :
    """
    Copies the list of variables (declared in the parser) in the Macroleaf object
    so that the object becomes aware of the existing variables and may call 
    their methods.
    
    This function must be called before Macroleaf.eval()

    The variables must be provided as a list of 'Variable' objects.
    """
    
    self.lookUpTable = variables
    
    # Propagate the 'lookUpTable' to the macroleaves
    for element in self.args :
      element.setVariables(self.lookUpTable)



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.eval()
  # ---------------------------------------------------------------------------
  def eval(self) :
    """
    TODO
    - use function pointers instead, and write all the definitions in 'symbols.py'
    - use a cache to avoid all the tests
    """
    # if (self.functionCache != None) :
      # print("TODO!")
    
    if (self.function == "id") :
      arg = self.args[0].eval()
      return arg
    
    elif (self.function == "opp") :
      arg = self.args[0].eval()
      return -arg
      
    elif (self.function == "sin") :
      arg = self.args[0].eval()
      return math.sin(arg)
      
    elif (self.function == "cos") :
      arg = self.args[0].eval()
      return math.cos(arg)
      
    elif (self.function == "tan") :
      arg = self.args[0].eval()
      return math.tan(arg)
      
    elif (self.function == "exp") :
      arg = self.args[0].eval()
      return math.exp(arg)
      
    elif (self.function == "ln") :
      arg = self.args[0].eval()
      return math.log(arg)
      
    elif (self.function == "log10") :
      arg = self.args[0].eval()
      return math.log(arg, 10)
      
    elif (self.function == "logN") :
      arg1 = self.args[0].eval()
      arg2 = self.args[1].eval()
      return math.log(arg1, arg2)
  
    elif (self.function == "abs") :
      arg = self.args[0].eval()
      return math.fabs(arg)
      
    elif (self.function == "sqrt") :
      arg = self.args[0].eval()
      return math.sqrt(arg)
      
    elif (self.function == "floor") :
      arg = self.args[0].eval()
      return math.floor(arg)
      
    elif (self.function == "ceil") :
      print("[INTERNAL ERROR] <ceil> function is todo!")
      return 0.0
      
    elif (self.function == "round") :
      print("[INTERNAL ERROR] <round> function is todo!")
      return 0.0
      
    elif (self.function == "Q") :
      print("[INTERNAL ERROR] <Q> function is todo!")
      return 0.0
      
    elif (self.function == "sinc") :
      print("[INTERNAL ERROR] <sinc> function is todo!")
      return 0.0
  
    else :
      print(f"[INTERNAL ERROR] Unknown function in Macroleaf.eval: '{self.function}'. This is not supposed to happen!")
      exit()



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.__str__ (print overloading)
  # ---------------------------------------------------------------------------
  # Define the behaviour of print(macroleafObj)
  def __str__(self) :
    argsStr = [a.getOverviewStr() for a in self.args]
    #return "{" + f"fct = '{self.function}', args = {self.args}" + "}"
    return "{" + f"fct = '{self.function}', args = {argsStr}" + "}"


# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")

  # TODO

  print("[INFO] End of unit tests.")
