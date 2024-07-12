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
# None.



class Macroleaf:

  def __init__(self, function, nArgs) :
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
    self.function   = function
    self.nArgs      = nArgs
    self.args       = [Binary() for _ in range(nArgs)]
    self.remainder  = []
    self.type       = "MACRO"



  # ---------------------------------------------------------------------------
  # METHOD: Macroleaf.process
  # ---------------------------------------------------------------------------
  def process(self, tokenList) :
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
        self.args[n].process(stack)
        stack = self.args[n].remainder
      
      self.remainder = stack
      
    # Terminal case: no token left
    else :
      print("TODO")
      return None



  # -----------------------------------------------------------------------------
  # METHOD: Macroleaf.sanityCheck
  # -----------------------------------------------------------------------------
  def sanityCheck(self, input = "") :
    """
    DESCRIPTION
    
    EXAMPLES
    
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input


