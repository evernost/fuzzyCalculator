# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : macroleaf
# File name       : macroleaf.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : Macroleaf object definition
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
import binary
import symbols



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

    The function to be used is identified by its name; just pass the name as a string
    in the argument.
    No need to create a Token.

    EXAMPLE
    M = Macroleaf("exp", myListOfTokens)
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
  # METHOD: Macroleaf._explicitZeros()
  # ---------------------------------------------------------------------------
  def flatten(self) :
    
    for n in range(self.nArgs) :
      self.args[n].flatten()



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.__str__ (print overloading)
  # ---------------------------------------------------------------------------
  # Define the behaviour of print(macroleafObj)
  def __str__(self) :
    argsStr = [str(a) for a in self.args]
    return "{" + f"fct = {self.function}, args = {argsStr}" + "}"



