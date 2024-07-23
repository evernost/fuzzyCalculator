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

  There are as many Binary objects <B1>, ..., <Bn> as arguments taken by the function.
  
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
    No need to create a Token.

    EXAMPLE
    M = Macroleaf("exp", myListOfTokens)
    M = Macroleaf("cos", myListOfTokens)
    etc.
    """    
    self.function   = function
    self.nArgs      = symbols.nArgsFromFunctionName(function)
    self.args       = [binary.Binary() for _ in range(self.nArgs)]
    self.remainder  = []
    self.type       = "MACRO"

    if (len(tokenList) >= 1) :
      self._process(tokenList)



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.process(tokenList)
  # ---------------------------------------------------------------------------
  def _process(self, tokenList) :
    """
    DESCRIPTION
    Takes a list of tokens as input, assigns them to each
    argument of the function and binarizes them.
    Returns: None.
    Only the internal attributes are updated.
    
    Note: the parenthesis token must be removed before calling this function.

    EXAMPLES
    todo
    """
    if (len(tokenList) >= 1) :
      
      stack = tokenList
      for n in range(self.nArgs) :
        self.args[n]._process(stack)
        stack = self.args[n].remainder
      
      self.remainder = stack
      
    # Terminal case: no token left
    else :
      print("<macroleaf.process> is todo!")
      return None



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
  # METHOD: Macroleaf._explicitZeros()
  # ---------------------------------------------------------------------------
  def _explicitZeros(self) :
    
    for n in range(self.nArgs) :
      self.args[n]._explicitZeros()



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf._minusAsOpp()
  # ---------------------------------------------------------------------------
  def _minusAsOpp(self) :
    
    for n in range(self.nArgs) :
      self.args[n]._minusAsOpp()



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.flatten()
  # ---------------------------------------------------------------------------
  def flatten(self) :
    
    for n in range(self.nArgs) :
      self.args[n].flatten()



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
    argsStr = [str(a) for a in self.args]
    return "{" + f"fct = {self.function}, args = {argsStr}" + "}"



