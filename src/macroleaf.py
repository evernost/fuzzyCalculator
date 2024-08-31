# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : macroleaf
# File name       : macroleaf.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : Macroleaf object definition
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# todo



# =============================================================================
# External libs
# =============================================================================
import binary
import symbols
import math


class Macroleaf :
  """
  Description
  A Macroleaf <M> is a recursive structure represented as follows:
  
  M = {F, [B1, B2, ..., Bn]]}
  
  where:
  - <F> is a function token
  - <B1>, ..., <Bn> are Binary objects.

  There are as many Binary objects <Bi> as there are arguments taken by the function.
  
  A 'Macroleaf' is essentially a function <F> applied to objects (Binary objects)
  that reduces to a leaf.
  
  The structure being recursive, it needs a terminal case.
  The terminal case is usually:

  M = {Id, [L]}
  
  where <Id> is the Identity function and <L> is a 'leaf': a constant, a variable or a number.

  
  Claim: any valid expression can be associated to a Macroleaf representation.


  Advantage: once the representation is built, the evaluation is straighforward.
  - Evaluate (recursively) each binary object
  - Apply the top function to the result.

  Priority between operators is decided when the list of Tokens is evaluated.
  Token list evaluation is beyond the scope of this class.

  Examples:
  - cos(2x) -> {F:cos, [NUM:2, OP:*, VAR:x]}
  """



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, function, tokenList) :
    """
    DESCRIPTION
    Creates and initializes a Macroleaf object from a function and a list of Tokens.
    Takes a list of Tokens as input, returns a Macroleaf object as output.

    The <function> argument only requires the name of the function as a string.
    No need to create or pass a Token.

    EXAMPLE
    M = Macroleaf("exp", someListOfTokens)
    M = Macroleaf("cos", someOtherListOfTokens)
    etc.
    """    
    self.function   = function
    self.nArgs      = symbols.nArgsFromFunctionName(function)
    self.args       = [binary.Binary() for _ in range(self.nArgs)]
    self.remainder  = []
    self.type       = "MACRO"

    if (len(tokenList) >= 1) :
      self._buildArgs(tokenList)
      
      for n in range(self.nArgs) :
        self._balanceMinus()

    else :
      print("[WARNING] Trying to create a Macroleaf with an empty list of Tokens.")



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf._buildArgs(tokenList)
  # ---------------------------------------------------------------------------
  def _buildArgs(self, tokenList) :
    """
    DESCRIPTION
    Takes a list of tokens as input, assigns them to each argument of the function 
    and binarises them.
    
    Returns: None.
    Only the internal attributes are updated.
    
    NOTE 
    The parenthesis token must be removed before calling this function.
    """
    
    if (len(tokenList) >= 1) :
      buffer = tokenList
      
      for n in range(self.nArgs) :
        
        # Build the stack with the current buffer.
        # "_buildStack" will automatically stop when encountering the Tokens
        # meant for the next argument.
        ret = self.args[n]._buildStack(buffer)
        buffer = self.args[n].remainder
        
        if (ret == binary.BINARISE_FAILURE) :
          return binary.BINARISE_FAILURE
        
        # Error: function expects another argument, but there are no Tokens left.
        elif ((n < (self.nArgs-1)) and (len(buffer) == 0)) :
          print("[ERROR] Internal error: arguments are expected, but there a no Tokens left to process.")
          return binary.BINARISE_FAILURE
        
        # "_buildStack" terminated succesfully. 
        # Its remainder is cleared and passed on to the next argument.
        else :
          self.args[n].remainder = []
          self.remainder = buffer

    # No token to process      
    else :
      print("[WARNING] Call to <_buildStack> with an empty list of Token is not supposed to happen.")
      self.remainder = []
      return binary.BINARISE_SUCCESS



  # -----------------------------------------------------------------------------
  # METHOD: Macroleaf.sanityCheck
  # -----------------------------------------------------------------------------
  def sanityCheck(self) :
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """

    print("<macroleaf.sanityCheck> is todo!")



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf._balanceMinus
  # ---------------------------------------------------------------------------
  def _balanceMinus(self) :
    """
    DESCRIPTION
    Calls the <_balanceMinus> method of each Binary object in the <args> list.
    """
    
    for n in range(self.nArgs) :
      self.args[n]._balanceMinus()
    
    
    
  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.nest()
  # ---------------------------------------------------------------------------
  def nest(self) :
    """
    Calls the <nest> method of each Binary object in the <args> list.
    """
    for n in range(self.nArgs) :
      self.args[n].nest()



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
  print("[INFO] Unit tests for the package 'macroleaf.py' will come in a future release.")

