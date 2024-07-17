# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : binary
# File name       : binary.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : Binary object definition
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
import symbols
import macroleaf



class Binary :
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

  A 'Macroleaf' is essentially a function and a leaf; the function is applied to the leaf.
  Since a Binary object ultimately reduces to a leaf, a Macroleaf can also be made
  of a function and a Macroleaf.
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
  def __init__(self, tokenList = []) :
    """
    DESCRIPTION
    Creates and initializes a Binary object from a list of Tokens.
    Takes a list of Tokens as input, returns a Binary object as output.

    NOTES
    The implicit multiplications must be explicited prior to calling the function.
    Refer to <explicitMult> for that purpose.

    EXAMPLE
    todo
    """
    self.stack     = []
    self.remainder = []

    if (len(tokenList) >= 1) :
      self._process(tokenList)



  # ---------------------------------------------------------------------------
  # METHOD: Binary.process(tokenList)
  # ---------------------------------------------------------------------------
  def _process(self, tokenList) :
    """
    DESCRIPTION
    Takes a list of tokens as input and builds the Binary representation of it.
    The binary list is available in the <stack> attribute. 
    
    Returns: None.
    Only the internal attributes are updated.

    The tokens that did not get binarized stay in the <remainder> attribute.
    It usually concerns the tokens that are not at the same level.

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
        self._process(tail)
      
      # Function creates a Macroleaf and requires another call to <process> on its argument(s).
      elif (currToken.type == "FUNCTION") :
        tailNoParenthesis = tail[1:]
        M = macroleaf.Macroleaf(function = currToken.name, tokenList = tailNoParenthesis)

        self.stack.append(M)
        self._process(M.remainder)

      # "(" creates a Macroleaf and requires another call to <process>.
      elif (currToken.type == "BRKT_OPEN") :
        M = macroleaf.Macroleaf(function = "id", tokenList = tail)
        
        self.stack.append(M)
        self._process(M.remainder)

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
        print(f"[ERROR] Unexpected token: {currToken}")



    # Terminal case: 1 token left
    elif (len(tokenList) == 1) :
      currToken = tokenList[0]

      if (currToken.type in ["CONSTANT", "VAR", "NUMBER"]) :
        self.stack.append(currToken)
        self.remainder = []
      
      elif (currToken.type == "BRKT_CLOSE") :
        self.remainder = []

      elif (currToken.type == "COMMA") :
        print("[ERROR] The list of tokens cannot end with a comma.")

      elif (currToken.type == "INFIX") :
        print("[ERROR] The list of tokens cannot end with an infix operator.")

      else :
        print(f"[ERROR] Unexpected token: {currToken}")

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
    - explicit the hidden '0' to balance the infix '-' operator
    - replace the infix operator and its operand with a macroleaf calling the 'opp'
      function.

    Please refer to rules [R7.X] in <parser.py>

    EXAMPLES
    todo
    """
    
    self._explicitZeros()   # Add zeros when implicit (rule [7.1])
    self._minusAsOpp()      # Replace '-' with 'opp' (opposite) according to rule [7.2] and [7.3]
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._explicitZeros()
  # ---------------------------------------------------------------------------
  def _explicitZeros(self) :
    
    nElements = len(self.stack)
    
    # Using the "-" in the context of rule [7.1] requires at least 2 elements.
    # Example: "-x"
    if (nElements >= 2) :
      
      # STEP 1: apply the processing to the own stack
      if (self.stack[0].type == "INFIX") :
        if (self.stack[0].name == "-") :
          self.stack = [symbols.Token("0")] + self.stack

      # STEP 2: apply the processing recursively to the stacks in the macroleaves.
      else :
        for elt in self.stack :
          if (elt.type == "MACRO") :
            elt._explicitZeros()
    
      return None

    else :
      return None
    


  # ---------------------------------------------------------------------------
  # METHOD: Binary._minusAsOpp()
  # ---------------------------------------------------------------------------
  def _minusAsOpp(self) :
    
    nElements = len(self.stack)
    
    # Using the "-" in the context of rule [7.2]/[7.3] requires at least 4 elements
    # Example: "2^-4"
    if (nElements >= 4) :
      newStack = []
      
      n = 0
      while (n <= (nElements-2)) :
        eltA = self.stack[n]; eltB = self.stack[n+1]

        # ---------------------------
        # Detect the "^-" combination
        # ---------------------------
        if ((eltA.type == "INFIX") and (eltB.type == "INFIX")) :
          if ((eltA.name == "^") and (eltB.name == "-")) :
            
            # Guard
            if ((n+2) > (nElements-1)) :
              print("[ERROR] Premature end; it should have been caught before calling <_minusAsOpp>!")
            
            M = macroleaf.Macroleaf(function = "opp", tokenList = [self.stack[n+2]])
            newStack.append(eltA)
            newStack.append(M)
            n += 3

        # ------------------------------------------------
        # Detect any other combination of an infix and "-"
        # ------------------------------------------------
        elif ((eltA.type == "INFIX") and (eltB.type == "INFIX")) :
          if (eltB.type == "-") :
            print("[WARNING] Odd use of '-' with implicit 0. Cross check the result or use parenthesis.")

            # Guard
            if ((n+2) > (nElements-1)) :
              print("[ERROR] Premature end; it should have been caught before calling <_minusAsOpp>!")
              exit()

            M = macroleaf.Macroleaf(function = "opp", tokenList = [self.stack[n+2]])
            newStack.append(eltA)
            newStack.append(M)
            n += 3

          else :
            print("[ERROR] Invalid combination of infixes; it should have been caught before calling <_minusAsOpp>!")
            exit()

        # ---------------
        # Last 2 elements
        # ---------------
        elif (n == (nElements-2)) :
          newStack.append(eltA)
          newStack.append(eltB)
          n += 1

        # ------------------------
        # Nothing special detected
        # ------------------------
        else :
          newStack.append(eltA)
          n += 1

      self.stack = newStack
      return None

    else :
      return None



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
    print("<binary.eval> is todo!")
    
  
  
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
    print("<binary.isolateHighestInfix> is todo!")
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary.__str__ (print overloading)
  # ---------------------------------------------------------------------------
  # Define the behaviour of print(binaryObj)
  def __str__(self) :
    return str(self.stack)
  
  
  
# -----------------------------------------------------------------------------
# Main (unit tests)
# -----------------------------------------------------------------------------
if (__name__ == '__main__') :
  
  print("[INFO] No unit tests available for this library.")


