# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : binary
# File name       : binary.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : Binary object definition
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
import symbols
import macroleaf



# =============================================================================
# Constant pool
# =============================================================================
BINARY_INIT = 0
BINARY_BALANCED = 1
BINARY_FLATTENED = 2



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

    self.status = BINARY_INIT
    
    self.lookUpTable = {}

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
      if (currToken.type in ["CONSTANT", "VAR", "NUMBER", "INFIX", "MACRO"]) :
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

      if (currToken.type in ["CONSTANT", "VAR", "NUMBER", "MACRO"]) :
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

    The process is done recursively on the Binary objects integrated within 
    macroleaves.

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
    
    # Detect a "-..." pattern.
    # STEP 1: detect the pattern on the own stack
    # Using the "-" in the context of rule [7.1] requires at least 2 elements.
    # Example: "-x"
    if (nElements >= 2) : 
      if (self.stack[0].type == "INFIX") :
        if (self.stack[0].name == "-") :
          self.stack = [symbols.Token("0")] + self.stack
          print("[DEBUG] Added an implicit zero.")

    # STEP 2: detect the pattern recursively on the macroleaves
    for elt in self.stack :
      if (elt.type == "MACRO") :
        elt._explicitZeros()

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

    # Less than 4 elements
    # There is nothing to be expanded in the stack, but there might in the macroleaves.
    else :
      for elt in self.stack :
        if (elt.type == "MACRO") :
          elt._minusAsOpp()
      
      
      
    return None



  # ---------------------------------------------------------------------------
  # METHOD: Binary.flatten()
  # ---------------------------------------------------------------------------
  def flatten(self) :
    """
    DESCRIPTION
    Simplifies the stack to an expression involving operators with lowest priority
    only.
    Operators with high priority are stored in a Macroleaf
    
    It does not assume commutativity of the infix operators.

    Associativity strategy are detailed in [R10].
    
    Note: minus signs '-' must have been balanced prior to calling this function
    (function <balanceMinus>)

    EXAMPLES
    todo
    """
    
    nElements = len(self.stack)

    # -------------------------------------------
    # CHECKS
    # -------------------------------------------
    # The stack MUST be like [L op L op ...]
    
    # CHECK 1: is the number of elements odd?
    if ((nElements % 2) == 0) :
      print(f"[ERROR] nElements should be odd at that point!")

    # CHECK 2: is it a pattern of alternating (macro)leaf and operators?
    nInfix = 0
    for (n, element) in enumerate(self.stack) :        
      if ((n % 2) == 0) :
        if (not(element.type in ["NUMBER", "VAR", "CONSTANT", "MACRO"])) :
          print("[ERROR] The expression to flatten must follow the pattern [L op L op ...]")
          exit()

      else :
        if (element.type != "INFIX") :
          print("[ERROR] The expression to flatten must follow the pattern [L op L op ...]")
          exit()

        else :
          nInfix += 1


    # Process recursively the stacks in the macroleaves
    for element in self.stack :
      if (element.type == "MACRO") :
        element.flatten()


    # 'Flatten' is required for 2 or more infix i.e. 5 elements
    if (nInfix >= 2) :
      
      # STEP 1: look for the infix of highest priority in [L op L op L ...]
      (minPriority, maxPriority) = self._getPriorityRange(self.stack)
      print(f"[DEBUG] Priority range = ({minPriority}, {maxPriority})")
      
      # <Flatten> is necessary if there are 2 different levels of priority
      while (maxPriority != minPriority) :

        # STEP 2: split apart the highest operator and its adjacent leaves
        # from the rest: [L op L op], [L op L], [op L op L op L op L]
        (chunks, chunkNeedsMacro) = self._splitOp(self.stack, maxPriority)

        # STEP 3: create a macro for the highest operators 
        # Result = [L op L op], M, [op L op L op L op L]
        # Then merge into a new stack.
        if (len(chunks) > 1) :
          newStack = []
          for i in range(len(chunks)) :
            if chunkNeedsMacro[i] :
              M = macroleaf.Macroleaf(function = "id", tokenList = chunks[i])
              newStack.append(M)
            
            else :
              newStack += chunks[i]

          self.stack = newStack  
        
        # STEP 4: repeat until the stack is 'flat' 
        # (all operators have the same priority)
        (minPriority, maxPriority) = self._getPriorityRange(self.stack)

      # Ends up with [L op L op L], all with identical precedence



    # Only 1 infix operator: nothing to do, leave the stack as it is.
    else :
      pass



  # ---------------------------------------------------------------------------
  # METHOD: Binary._getPriorityRange()
  # ---------------------------------------------------------------------------
  def _getPriorityRange(self, elementList) :
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """
    minPriority = 100; maxPriority = -1
    for element in elementList :
      if (element.type == "INFIX") :
        if (element.priority > maxPriority) :
          maxPriority = element.priority

        if (element.priority < minPriority) :
          minPriority = element.priority

    return (minPriority, maxPriority)



  # ---------------------------------------------------------------------------
  # METHOD: Binary._splitOp()
  # ---------------------------------------------------------------------------
  def _splitOp(self, tokenList, priority) :
    """
    DESCRIPTION
    Breaks apart the stack to isolate the sequences of (macro)leaves and 
    infix operator(s), keeping only the infix(es) of highest priority.
    
    The function takes the internal stack as input.
    It returns the stack broken apart as output, as a list of lists.
    
    If all infix have the same priority, the stack is returned as is.

    EXAMPLES
    B = Binary()
    B.stack = [a * b + c / d ^ e + f]
    B._splitOp = [[a * b + c /] [d ^ e] [+ f]]
    
    (representation is simplified for the sake of the example)
    """

    nElements = len(tokenList)
    isTopElement = [False for _ in range(nElements)]

    # STEP 1: create a 'side array' indicating where the split must be done.
    for (n, element) in enumerate(tokenList) :
      if (element.type == "INFIX") :
        if (element.priority > priority) :
          print("[ERROR] This is not supposed to happen! (function <_splitOp>)")

        elif (element.priority == priority) :
          isTopElement[n-1] = True
          isTopElement[n]   = True
          isTopElement[n+1] = True

    # STEP 2: do the actual split
    chunksOut = []; chunkIsTop = []
    for (n, element) in enumerate(tokenList) :
      if (n == 0) :
        tmp = [tokenList[0]]

      else :
        if (isTopElement[n-1] != isTopElement[n]) :
          if (n == (nElements-1)) :
            chunksOut.append(tmp)
            chunkIsTop.append(isTopElement[n-1])

            chunksOut.append([tokenList[n]])
            chunkIsTop.append(isTopElement[n])
          else :
            chunksOut.append(tmp)
            chunkIsTop.append(isTopElement[n-1])

            tmp = [tokenList[n]]

        else :
          if (n == (nElements-1)) :
            tmp.append(tokenList[n])
            chunksOut.append(tmp)
            chunkIsTop.append(isTopElement[n])
          else :
            tmp.append(tokenList[n])

    return (chunksOut, chunkIsTop)



  # ---------------------------------------------------------------------------
  # METHOD: Binary.setVariables()
  # ---------------------------------------------------------------------------
  def setVariables(self, variables) :
    """
    DESCRIPTION
    Declares the variables and their values to the parser.
    
    Necessary before any evaluation.
    
    The variables are given as a dictionary that pairs the variable name with 
    either a number (fixed variables) or a generator (random variables)
    
    EXAMPLES
    variables = {
      "R1": 10000.0, 
      "R2": variable.Scalar(10.0, "k"),
      "R3": variable.rand(val = 10, tol = 0.05)
    }
    """
    
    self.lookUpTable = variables
    
    # Propagate the <lookUpTable> to the macroleaves
    for element in self.stack :
      if (element.type == "MACRO") :
        element.setVariables(lookUpTable)



  # ---------------------------------------------------------------------------
  # METHOD: Binary.eval()
  # ---------------------------------------------------------------------------
  def eval(self) :
    """
    DESCRIPTION
    Evaluates the Binary object.
    
    The Binary object must have been flattened prior to calling this function.
    
    The list of variables and their value must be initialized using <setVariables>
    before calling this function.

    Undeclared variables will return an error.

    EXAMPLES
    todo
    """
    
    if (self.state != BINARY_FLATTENED) :
      print("[ERROR] The binary object must be flattened before evaluation.")
    
    nElements = len(self.stack)
    
    if (nElements > 1) :
      # Stack is flattened, so its structure is necessarily [L op L op ... L]
      # <op> being all of the same priority.
      # Then rule [R10] applies: the righter part gets evaluated first.
      output = self._evalOp(op = self.stack[1], leftOperand = self.stack[0], rightOperand = self.stack[2:])
    
    else :
      output = self._evalLeaf(self.stack[0])
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._evalLeaf()
  # ---------------------------------------------------------------------------
  def _evalLeaf(self, leaf) :
    """
    DESCRIPTION
    Evaluates a Token (variable, constant, number) or a Macroleaf.

    EXAMPLES
    todo
    """
    
    if (leaf.type in ["CONSTANT", "NUMBER"]) :
      return leaf.value
    
    elif (leaf.type == "VARIABLE") :
      print("TODO")
      
      # Fetch the variable and its value from <lookUpTable>
    
    elif (leaf.type == "MACRO") :
      return leaf.eval()
    
    
    else :
      print(f"[INTERNAL ERROR] Expected a leaf, but got a Token of type '{leaf.type}' instead.")
    
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._evalOp()
  # ---------------------------------------------------------------------------
  def _evalOp(self, leaf) :
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """
    
    print("todo!")
    
  
  
  
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


