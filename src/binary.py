# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : binary
# File name       : binary.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : 
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



class Binary:
  """
  DESCRIPTION
  A 'Binary' object is an ordered list of infix operators and (Macro)leaves
  arranged in the following pattern: 

  [L1, op1, L2, op2, ... Ln]
  
  where 
  - <L1> ... <Ln> are leaves or Macroleaves
  - <op1> ... <opn> are infix operators.

  'Leaves' are meant here in a binary tree context and represent the last stage 
  of an evaluation stack. 
  In the context of this parser, a 'leaf' is a constant, a variable or a number.

  A 'Macroleaf' is essentially a leaf on which a function is applied.
  Since a Binary object reduces to a leaf, the leaf of the Macroleaf 
  structure can even be generalized to a Binary object.
  Hence the recursive nature.

  Any valid list of tokens can be associated with a unique Binary Object.
  When the expression does not contain any function or parenthesis, 
  the Binary Object simplifies to a list of leaves and infix operators.
  
  A Binary object comes with an <eval> method whose purpose is to reduce 
  the list of (macro)leaves and infix to a single leaf.

  For that, the <eval> method:
  - reduces all the macroleaves to leaves by calling their own <eval> method
  - builds an ordered evaluation tree based on the relative priorities of each infix
  operators

  'Binary' objects and 'Macroleaf' objects are tightly coupled:
  please refer to the 'Macroleaf' definition for more information.
  """
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self) :
    """
    DESCRIPTION
    Creates an initialize a Binary object.
    This constructor does not take any arguments.

    EXAMPLE

    """
    self.stack     = []
    self.remainder = []



  # ---------------------------------------------------------------------------
  # METHOD: Binary.process
  # ---------------------------------------------------------------------------
  def process(self, tokenList) :
    """
    DESCRIPTION
    Takes a list of tokens as input and builds the Binary representation of it.
    The list is available in the <stack> attribute. 
    
    Returns: None.
    Only the internal attributes are updated.

    The function expects the list of token to be valid. 
    Refer to functions:
    - TBD 
    - TBD 
    for the common checks to be done prior to calling this method.
    Only the syntax errors associated with this processing will be caught here.
    
    EXAMPLES
    todo
    """
    
    if (len(tokenList) >= 2) :
      (currToken, tail) = (tokenList[0], tokenList[1:])
      
      # Leaves/infix are simply pushed to the stack.
      if (currToken.type in ["CONSTANT", "VAR", "NUMBER", "INFIX"]) :
        self.stack.append(currToken)
        self.process(tail)
      
      # Function creates a Macroleaf and requires another call to <process> on its argument(s).
      elif (currToken.type == "FUNCTION") :
        M = Macroleaf(function = currToken.name, nArgs = currToken.nArgs)
        
        tailNoParenthesis = tail[1:]
        M.process(tailNoParenthesis)
        
        self.stack.append(M)
        self.process(M.remainder)

      # "(" creates a Macroleaf and requires another call to <process>.
      elif (currToken.type == "BRKT_OPEN") :
        M = Macroleaf(function = "id", nArgs = 1)
        
        M.process(tail)
        
        self.stack.append(M)
        self.process(M.remainder)

      # "," stops the binarisation.
      # The Macroleaf must now process the next argument.
      elif (currToken.type == "COMMA") :
        self.remainder = tail
        return None

      # ")" stops the binarisation.
      # The Macroleaf is now complete. 
      elif (currToken.type == "BRKT_CLOSE") :
        self.remainder = tail
        return None
      
      # Anything else is invalid.
      else :
        print(f"[ERROR] Unexpected token: <{currToken}>")



    # Terminal case: 1 token left
    elif (len(tokenList) == 1) :
      currToken = tokenList[0]

      if (currToken.type in ["CONSTANT", "VAR", "NUMBER"]) :
        self.stack.append(currToken)
        self.remainder = []
        return None
      
      elif (currToken.type == "BRKT_CLOSE") :
        self.remainder = []
        return None

      elif (currToken.type == "COMMA") :
        print("[ERROR] The list of tokens cannot end with a comma.")
        return None

      if (currToken.type == "INFIX") :
        print("[ERROR] The list of tokens cannot end with an infix operator.")
        return None

      else :
        print("[ERROR] Unexpected token.")
        return None



    # Terminal case: no token left
    else :
      return None




  # ---------------------------------------------------------------------------
  # METHOD: Binary.balanceMinus
  # ---------------------------------------------------------------------------
  def balanceMinus(self) :
    """
    DESCRIPTION
    Detects the minus signs used as a shortcut for the 'opposite' function.
    Takes as input a Binary object, edits its stack so that it has full expansion
    of the 'minus' infix operators.
    
    Returns: None.
    
    For that purpose, the function can:
    - either explicit the hidden '0' to balance the infix '-' operator
    - replace the infix operator and its operand with a macroleaf calling the 'opp'
      function.

    Please refer to rules [R7.X]

    EXAMPLES
    todo
    """
    
    self._explicitZeros(self)   # Add zeros when implicit (rule [7.1])
    self._minusAsOpp(self)      # Replace '-' with 'opp' (opposite) according to rule [7.2] and [7.3]
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._explicitZeros()
  # ---------------------------------------------------------------------------
  def _explicitZeros(self) :
    
    nElements = len(self.stack)
    if (nElements >= 2) :
      if (self.stack[0].type == "INFIX") :
        if (self.stack[0].name == "-") :
          binary.stack = [Token("0")] + binary.stack
          
      else :
        for elt in binary.stack :
          if (elt.type == "MACRO") :
            elt._explicitZeros()
    
    # There can't be hidden "0" to explicit when the stack has 
    # less than 2 elements.
    else :
      return None
    


  # ---------------------------------------------------------------------------
  # METHOD: Binary._minusAsOpp()
  # ---------------------------------------------------------------------------
  def _minusAsOpp(self) :
    
    nElements = len(self.stack)
    print("todo")



  # ---------------------------------------------------------------------------
  # METHOD: Binary.eval()
  # ---------------------------------------------------------------------------
  def eval(self) :
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """
    print("TODO")
    
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary.isolateHighestInfix
  # ---------------------------------------------------------------------------
  def isolateHighestInfix(self) :
    """
    DESCRIPTION
    Breaks apart the stack to isolate the sequences of (macro)leaves and 
    infix operator(s), keeping only the infix of highest priority.
    
    The function takes the internal stack as input.
    It returns the stack broken apart as output, as a list of lists.
    
    If all infix have the same priority, the stack is returned as is.

    EXAMPLES
    B = Binary()
    B.stack = [a * b + c / d ^ e + f]
    B.isolateHighestInfix = [[a * b + c /] [d ^ e] [+ f]]
    
    (representation is simplified for the sake of the example)
    """
    print("TODO")
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary.__str__ (print overloading)
  # ---------------------------------------------------------------------------
  # Define the behaviour of print(binaryObj)
  def __str__(self) :
    return str(self.stack)
  
    