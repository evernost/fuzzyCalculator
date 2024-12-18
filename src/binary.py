# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : binary
# File name       : binary.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : 'Binary' object definition
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : Saturday, 1 June 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# 'Binary' object definition.



# =============================================================================
# External libs
# =============================================================================
import src.symbols as symbols
import src.macroleaf as macroleaf



# =============================================================================
# Constants pool
# =============================================================================
# Binarization status
BINARISE_SUCCESS = 0
BINARISE_SUCCESS_WITH_REMAINDER = 1
BINARISE_FAILURE = -1



# =============================================================================
# Main code
# =============================================================================
class Binary :
  """
  DESCRIPTION
  A 'Binary' object is essentially a Python list (the 'stack') made of  
  infix operators and leaves, always arranged in the following pattern: 

  binaryObj.stack = [L1, op1, L2, op2, ... Ln]
  
  where 
  - <L1> ... <Ln> are leaves (or Macroleaves objects)
  - <op1> ... <opn> are infix operators.

  A 'leaf' refers here to the binary tree vocabulary. It represents the very last
  object that is encountered upon evaluation of an expression.
  In this parser, a leaf is either a constant, a variable or a number.

  A 'Macroleaf' is an object that combines one or more Binary objects
  and a function (sin, cos, exp, ...)
  It a nutshell, it models the part of the expression where a function is 
  applied to a sub-expression.
  The built-in Binary object(s) are the argument(s) the function applies to.
  
  Simple parenthesis are also modelled with a Macroleaf: the function becomes 
  "id" (mathematical identity) in this case (i.e. no processing)
  
  Please note the recursive nature of the Binary object / Macroleaf object.

  The claim: a valid expression can always be represented as a chain 'L op L op L op ... L'
  (a 'binary' expression) where <op> are the infix operators and <L> the leaves/macroleaves.

  Though, this assumes that:
  - implicit multiplications have been explicited
  - implicit zeros (when '-' is meant as 'opposite of') have been explicited

  Examples (using pseudo-notation): 
  - "4*x+3"    becomes   'L("4")   op("*")   L("x")   op("+")   L("3")'
  - "2cos(a^2) becomes   'L("2")   L("*")   M("cos"; L(L("a")   op("^")   L("2")))
  - etc.
  L("...") is a leaf
  M("fun"; ...) is a Macroleaf applying the function "fun" to its internal Binary objects.
  
  Once in the "flattened form" i.e. 'L op L op ... L', the processing is much easier.
  - Nesting (functions, parenthesis) is abstracted by the Macroleaves: processing can
  be done recursively.
  - Identifying the operators with higher precedence is easier.
  - Evaluating the expression is much simpler too.
  
  USAGE
  The Binary object is directly initialized from a list of Tokens.
  The initialisation function does the following automatically:
  - it expands the implicit multiplications
  - it balances the minus operators by adding the implicit zeros 
  - it packs the functions calls/parenthesis in macroleaves
  - it generates the binary chain 'L op L op ...'
  
  The binary chain is available in "binaryObj.stack"
  
  NOTES
  - Implicit multiplications must have been expanded before.
  - A simple Python list could have done the job, but it makes more sense 
  to have it packed in an object since:
    - processing is required and it is specific to this structure
    - the content of the list is not arbitrary and has to follow a pattern.
    Packing it as an object helps to enforce this pattern and catch
    invalid inputs.
  - 'Binary' objects and 'Macroleaf' objects are tightly coupled.
  Please refer to the 'Macroleaf' definition for more information.
  - The attributes distinguish between 'tokens' and 'nodes'
  """
  


  # ---------------------------------------------------------------------------
  # METHOD: Binary.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, tokenList = [], context = "TOP") :
    """
    Creates a Binary object and initialises it from a list of Tokens.
    Takes a list of Tokens as input, returns a Binary object as output.

    The function tries to represent the list of tokens as a binary list:
    'L op L op L op ... L'
    The result is stored in the <stack> attribute.
    
    The "remainder" attribute is only used internally. 
    It should remain empty when called from top level.
    """
   
    self.stack     = []
    self.remainder = []

    self.lookUpTable = {}

    if (len(tokenList) >= 1) :
      self.context = context
     
      self.status = self._buildStack(tokenList)
      self._balanceMinus()

      self.nNodes = len(self.stack)
      self.nLeaves = 0
      self.nOps = 0
    
    # Init with empty list of tokens. 
    else :
      print("[ERROR] Binary.__init__: this section should not have been reached (empty list of Tokens)")
      


  # ---------------------------------------------------------------------------
  # METHOD: Binary._buildStack(tokenList)
  # ---------------------------------------------------------------------------
  def _buildStack(self, tokenList) :
    """
    Takes a list of tokens as input and builds the Binary representation of it
    i.e. a list made of the pattern [L, op, L, op, ..., L]
    The binary list is available in the "stack" attribute. 
    
    It returns a status that depends on the parsing outcome:
    - BINARISE_SUCCESS: all good! the entire input could be binarised.
    - BINARISE_SUCCESS_WITH_REMAINDER: todo
    - BINARISE_FAILURE: todo

    Special case for the Macroleaf object: 
    Binarisation might process only the beginning of the list of Tokens.
    The tokens that did not get binarised are stored in the "remainder" attribute.
    It is used in 2 scenarios:
    - when binarising arguments of a multiargs function.
    Each argument is binarised individually. The comma "," is the separator and stops
    the binarisation for the current arguemnt. 
    Binarisation should be called again on the remainder to get the content of the 
    next argument.
    - when a closing parenthesis is found, it closes the Macroleaf (end of sub-expression)
    Binarisation stops here. 
    
    See <macroleaf.py> for more details.
    """
    
    buffer = tokenList.copy()

    while (len(buffer) > 0) :
      nTokens = len(buffer)
      
      if (nTokens > 1) :
        (T, tail) = (buffer[0], buffer[1:])
        
        # (Macro)Leaves/infix are simply pushed to the stack.
        if (T.type in ["CONSTANT", "VAR", "NUMBER", "INFIX", "MACRO"]) :
          self.stack.append(T)
          buffer = tail
        
        # A function creates a Macroleaf and requires another call to <_buildStack> on its argument(s).
        elif (T.type == "FUNCTION") :
          tailNoParenthesis = tail[1:]
          M = macroleaf.Macroleaf(function = T.name, tokenList = tailNoParenthesis)

          self.stack.append(M)
          buffer = M.remainder

        # A "(" creates a Macroleaf and requires another call to <_buildStack>.
        elif (T.type == "BRKT_OPEN") :
          M = macroleaf.Macroleaf(function = "id", tokenList = tail)
          
          self.stack.append(M)
          buffer = M.remainder
          
        # A "," occurs when <_buildStack> is called from a Macroleaf.
        # It stops the binarisation.
        # The Macroleaf must now process the next argument.
        elif (T.type == "COMMA") :
          self.remainder = tail
          return BINARISE_SUCCESS_WITH_REMAINDER

        # A ")" stops the binarisation.
        # The Macroleaf is now complete. 
        elif (T.type == "BRKT_CLOSE") :
          self.remainder = tail
          return BINARISE_SUCCESS_WITH_REMAINDER
        
        # Anything else is invalid.
        else :
          print(f"[ERROR] Unexpected token: {T}")
          return BINARISE_FAILURE



      elif (nTokens == 1) :
        T = buffer[0]; buffer = []

        if (T.type in ["CONSTANT", "VAR", "NUMBER", "MACRO"]) :
          self.stack.append(T)
          self.remainder = []
          return BINARISE_SUCCESS
        
        elif (T.type == "BRKT_CLOSE") :
          self.remainder = []
          return BINARISE_SUCCESS

        elif (T.type == "COMMA") :
          print("[ERROR] A list of tokens cannot end with a comma.")
          self.remainder = [T]
          return BINARISE_FAILURE

        elif (T.type == "INFIX") :
          print(f"[ERROR] A list of tokens cannot end with an infix operator (here: '{T.name}')")
          self.remainder = [T]
          return BINARISE_FAILURE

        else :
          print(f"[ERROR] Unexpected token: {T}")
          self.remainder = [T]
          return BINARISE_FAILURE

      
      # nTokens = 0
      else :
        self.remainder = []
        return BINARISE_SUCCESS



  # ---------------------------------------------------------------------------
  # METHOD: Binary._balanceMinus
  # ---------------------------------------------------------------------------
  def _balanceMinus(self) :
    """
    Detects the minus signs used as a shortcut for the 'opposite' function.
    Takes as input a Binary object, edits its stack so that it has full expansion
    of the 'minus' infix operators.
    
    Returns: None.
    
    The balancing is done by two means:
    - explicit the hidden '0' to balance the infix '-' operator
    - replace the infix operator and its operand with a macroleaf calling the 'opp'
      function.

    Please refer to rules [R7.X] in <parser.py>

    The process is done recursively on the Binary objects embedded inside 
    macroleaves.
    """
    
    self._explicitZeros()   # Add zeros when implicit (rule [7.1])
    self._minusAsOpp()      # Replace '-' with 'opp' (opposite) according to rule [7.2] and [7.3]
  

  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._explicitZeros()
  # ---------------------------------------------------------------------------
  def _explicitZeros(self) :
    """
    Adds a "0" Token to the stack every time the minus sign "-" 
    is meant as the 'opposite' function in the beginning of an expression 
    e.g. "-2+3x" -> "0-2+3x"

    The function operates on the "stack" property directly.

    Cases like "2^-4" are treated in "_minusAsOpp".

    It is highly recommended to let the constructor "__init__" do the calling 
    to "_explicitZeros" instead of calling it manually.
    In particular, it does the processing recursively so that it applies properly
    to all the nested stacks (e.g. in Macroleaves)
    
    See "_balanceMinus" for more information.
    """
    
    nNodes = len(self.stack)
    
    # Detect a "-..." pattern.
    # STEP 1: detect the pattern in the stack
    
    # Using the "-" in the context of rule [7.1] requires at least 2 elements.
    # Example: "-x"
    if (nNodes >= 2) : 
      if (self.stack[0].type == "INFIX") :
        if (self.stack[0].name == "-") :
          self.stack = [symbols.Token("0")] + self.stack
          print("[DEBUG] Binary._explicitZeros(): added an implicit zero.")

    # STEP 2: detect the pattern recursively in the macroleaves
    # for node in self.stack :
    #   if (node.type == "MACRO") :
    #     node._explicitZeros()

    # return None



  # ---------------------------------------------------------------------------
  # METHOD: Binary._minusAsOpp()
  # ---------------------------------------------------------------------------
  def _minusAsOpp(self) :
    """
    Replaces the minus signs '-' with a Macroleaf expansion with function 'opp'.
    e.g. "2^-4" -> "2^Macro"
    
    The function operates on the 'stack' property directly.

    It is highly recommended to let the constructor "__init__" do the calling 
    to "_minusAsOpp" instead of calling it manually.
    In particular, it does the processing recursively so that it applies properly
    to all the nested stacks (e.g. in Macroleaves)
    
    See "_balanceMinus" for more information.
    """
    
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
              print("[ERROR] Premature end; it should have been caught before calling 'Binary._minusAsOpp()'")
              exit()
            
            M = macroleaf.Macroleaf(function = "opp", tokenList = [self.stack[n+2]])
            newStack.append(eltA)
            newStack.append(M)
            n += 3
            print("[DEBUG] Binary._minusAsOpp(): added a Token because of implicit call to 'opp'.")

        # ------------------------------------------------
        # Detect any other combination of an infix and "-"
        # ------------------------------------------------
        elif ((eltA.type == "INFIX") and (eltB.type == "INFIX")) :
          if (eltB.type == "-") :
            print("[WARNING] Odd use of '-' with implicit 0. Cross check the result or use parenthesis.")

            # Guard
            if ((n+2) > (nElements-1)) :
              print("[ERROR] Premature end; it should have been caught before calling 'Binary._minusAsOpp()'")
              exit()

            M = macroleaf.Macroleaf(function = "opp", tokenList = [self.stack[n+2]])
            newStack.append(eltA)
            newStack.append(M)
            n += 3
            print("[DEBUG] Binary._minusAsOpp(): added a Token because of implicit call to 'opp'.")

          else :
            print("[ERROR] Invalid combination of infixes; it should have been caught before calling 'Binary._minusAsOpp()'")
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
    # There is nothing to be expanded in the stack.
    else :
      pass
      # for elt in self.stack :
        # if (elt.type == "MACRO") :
          # elt._minusAsOpp()
      
    return None



  # ---------------------------------------------------------------------------
  # METHOD: Binary.nest()
  # ---------------------------------------------------------------------------
  def nest(self) :
    """
    Simplifies the stack to an expression involving operators with lowest priority
    only.
    
    Rewriting is done by repeatingly isolating away the operators of higher priority
    and their operands in a Macroleaf.

    It does not assume commutativity of the infix operators.

    Associativity strategy are detailed in [R10].
    
    Note: minus signs '-' must have been balanced prior to calling this function
    (function <balanceMinus>)
    """
    
    # CHECK 1: number of nodes must be even.
    if ((self.nNodes % 2) == 0) :
      print(f"[ERROR] Binary.nest(): cannot nest an even number of nodes (size = {self.nNodes})")
      exit()

    # CHECK 2: nodes in the stack (top level and macros) must follow a 'L op L ... op L' pattern
    nInfix = 0
    for (n, element) in enumerate(self.stack) :        
      if ((n % 2) == 0) :
        if (not(element.type in ["NUMBER", "VAR", "CONSTANT", "MACRO"])) :
          print("[ERROR] Binary.nest(): the expression does not follow the pattern [L op L op ...] (ERR_NOT_A_LEAF)")
          exit()

      else :
        if (element.type != "INFIX") :
          print("[ERROR] Binary.nest(): the expression to nest does not follow the pattern [L op L op ...] (ERR_NOT_AN_INFIX)")
          exit()

        else :
          nInfix += 1

    # Nest the stacks in the Macroleaves
    for element in self.stack :
      if (element.type == "MACRO") :
        element.nest()

    # Nest the actual stack.
    # Nesting can be required as soon as there are 2 or more infix: "L op L op L"
    # i.e. more than 5 nodes.
    if (nInfix >= 2) :
      
      # STEP 1: look for the infix of highest priority in [L op L op L ...]
      (minPriority, maxPriority) = self._getPriorityRange()
      print(f"[DEBUG] Binary.nest(): priority range = ({minPriority}, {maxPriority})")
      
      # Call to "nest()" is necessary if there are 2 different levels of priority
      while (maxPriority != minPriority) :

        # STEP 2: split apart the highest operator and its adjacent leaves
        # from the rest: [L op L op], [L op L], [op L op L op L op L]
        (chunks, chunkNeedsMacro) = self._splitOp(maxPriority)

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

          # TODO: update the other properties
          self.nNodes = len(self.stack)
          # self.nLeaves = ...
        
        # STEP 4: repeat until the stack is 'flat' 
        # (all operators have the same priority)
        (minPriority, maxPriority) = self._getPriorityRange()

      # END: stacks now looks like [L op L op L], all with identical precedence.

    # Only 1 infix operator: nothing to do, leave the stack as it is.
    else :
      pass



  # ---------------------------------------------------------------------------
  # METHOD: Binary._getPriorityRange()
  # ---------------------------------------------------------------------------
  def _getPriorityRange(self) :
    """
    Browses the stack and returns the (min, max) priority encountered while 
    inspecting the infix operators.
    
    The method is used for the nesting operations, the goal being to
    'flatten' the expression i.e. abstract away infix with higher precedence
    in a Macroleaf.
    
    It does not inspect the content of the Macroleaves (it is done already
    by the recursive call in the "nest()" method)
    """
    
    minPriority = 100; maxPriority = -1
    for node in self.stack :
      if (node.type == "INFIX") :
        if (node.priority > maxPriority) :
          maxPriority = node.priority

        if (node.priority < minPriority) :
          minPriority = node.priority

    return (minPriority, maxPriority)



  # ---------------------------------------------------------------------------
  # METHOD: Binary._splitOp()
  # ---------------------------------------------------------------------------
  def _splitOp(self, priority) :
    """
    Breaks apart the stack to isolate the sequences of (macro)leaves and 
    infix operator(s), keeping only the infix(es) of highest priority.
    
    The function operates on the stack.
    It returns the stack broken apart as output, as a list of lists.
    
    If all infix have the same priority, the stack is returned as is.

    EXAMPLES
    B = Binary()
    B.stack = [a * b + c / d ^ e + f]
    B._splitOp = [[a * b + c /] [d ^ e] [+ f]]
    (representation is simplified for the sake of the example)
    """

    #self.nNodes = len(self.stack)
    isTopElement = [False for _ in range(self.nNodes)]

    # STEP 1: create a 'side array' indicating where the split must be done.
    for (n, element) in enumerate(self.stack) :
      if (element.type == "INFIX") :
        if (element.priority > priority) :
          print("[DEBUG] Error: inconsistency in '_splitOp'. The requested 'break' priority is higher than any infix in the stack.")

        elif (element.priority == priority) :
          isTopElement[n-1] = True
          isTopElement[n]   = True
          isTopElement[n+1] = True

    # STEP 2: do the actual split
    chunksOut = []; chunkIsTop = []
    for (n, element) in enumerate(self.stack) :
      lastNode = (n == (self.nNodes-1))
      if (n == 0) :
        subStack = [self.stack[0]]

      else :
        # CASE 1: priority of the node has changed.
        # Either:
        # - the node before was involved in a high priority infix, but now not anymore.
        # - the node before was not involved in a high priority infix, but now it does.
        if (isTopElement[n] != isTopElement[n-1]) :
          if lastNode :
            chunksOut.append(subStack)
            chunkIsTop.append(isTopElement[n-1])

            chunksOut.append([self.stack[n]])
            chunkIsTop.append(isTopElement[n])
          
          else :
            
            # Push the current "sub stack" to the output list
            # and mark its status (top priority element or not)
            chunksOut.append(subStack)
            chunkIsTop.append(isTopElement[n-1])

            # Start a new sub stack
            subStack = [self.stack[n]]
        
        # CASE 2: priority of the node remains the same.
        else :
          if (n == (self.nNodes-1)) :
            subStack.append(self.stack[n])
            chunksOut.append(subStack)
            chunkIsTop.append(isTopElement[n])
          
          else :
            subStack.append(self.stack[n])

    return (chunksOut, chunkIsTop)



  # ---------------------------------------------------------------------------
  # METHOD: Binary.setVariables()
  # ---------------------------------------------------------------------------
  def setVariables(self, variables) :
    """
    DESCRIPTION
    Declares the variables and their values to the parser.
    
    This function must be called before any evaluation.
    
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
  def eval(self, stack = []) :
    """
    Evaluates the stack in the Binary object.
    A specific stack can be given as argument, but this mode is usually used
    by the internal machinery.
    
    The Binary object must have been nested prior to calling this function.
    
    The list of variables and their value must be initialized using <setVariables>
    before calling this function.

    Undeclared variables will return an error.
    """

    # By default, process the own stack.
    if (len(stack) == 0) :
      stack = self.stack

    # The expression must has been nested so its structure is: [L op1 L op2 ... opN L]
    # 'op1', ..., 'opN' having all the same priority.
    # Then rule [R10] applies: the righter part gets evaluated first.
    nNodes = len(stack)

    if (nNodes > 1) :
      firstLoop = True
      resultToken = symbols.Token("0.0", value = 0)
      
      while (nNodes > 1) :
        if firstLoop :
          resultToken.value = self._evalOp(leftLeaf = stack[0], op = stack[1], rightLeaf = stack[2])
          firstLoop = False
        else :
          resultToken.value = self._evalOp(leftLeaf = resultToken, op = stack[1], rightLeaf = stack[2])
        
        stack = stack[2:]; nNodes -= 2      
      
      return resultToken.value

    # Only 1 node: it is a leaf, evaluate it.
    else :
      output = self._evalLeaf(stack[0])
      return output
  
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._evalLeaf()
  # ---------------------------------------------------------------------------
  def _evalLeaf(self, leaf) :
    """
    Evaluates a Token (variable, constant, number) or a Macroleaf.
    Returns a scalar.

    EXAMPLES
    todo
    """
    
    if (leaf.type in ["CONSTANT", "NUMBER"]) :
      return leaf.value
    
    elif (leaf.type == "VAR") :
     
      # Fetch the variable and its value from <lookUpTable>
      # todo!
      input(f"Assign value to variable '{leaf.name}': ")

    elif (leaf.type == "MACRO") :
      return leaf.eval()
    
    else :
      print(f"[ERROR] Binary._evalLeaf(): expected a leaf, but got a Token of type '{leaf.type}' instead.")
    
  
  
  # ---------------------------------------------------------------------------
  # METHOD: Binary._evalOp()
  # ---------------------------------------------------------------------------
  def _evalOp(self, leftLeaf, op, rightLeaf) :
    """
    Evaluates a triplet 'leftLeaf op rightLeaf' (like "2 + 3")
    Returns the scalar the expression evaluates to.
    """
    
    # Checks: make sure each argument is of the right type
    if not(leftLeaf.type in ["NUMBER", "CONSTANT", "VAR", "MACRO"]) :
      print(f"[ERROR] Binary._evalOp(): 'leftLeaf' must be a leaf, got a type '{leftLeaf.type}' instead.")
        
    if not(rightLeaf.type in ["NUMBER", "CONSTANT", "VAR", "MACRO"]) :
      print(f"[ERROR] Binary._evalOp(): 'leftLeaf' must be a leaf, got a type '{leftLeaf.type}' instead.")

    if (op.type != "INFIX") :
      if hasattr(op, "name") :
        print(f"[ERROR] Binary._evalOp(): '{op.name}' is not a valid infix operator.")
      else :
        print(f"[ERROR] Binary._evalOp(): while evaluating, got an invalid infix operator.")
        
    # Evaluation of each argument of the operator
    leftArg = self._evalLeaf(leftLeaf)
    rightArg = self._evalLeaf(rightLeaf)

    #
    # TODO: find a more elegant way to be aware of all existing infix operators
    #

    if (op.name == "+") :
      return (leftArg + rightArg)
  
    elif (op.name == "-") :
      return (leftArg - rightArg)

    elif (op.name == "*") :
      return (leftArg * rightArg)

    elif (op.name == "/") :
      # TODO: check for division by zero
      return (leftArg / rightArg)

    elif (op.name == "^") :
      return (leftArg ** rightArg)

    elif (op.name == "//") :
      a = leftArg; b = rightArg
      return ((a*b)/(a+b))

    else :      
      print(f"[ERROR] Binary._evalOp(): unknown infix operator '{op.name}'.")
  
  

  # ---------------------------------------------------------------------------
  # METHOD: Binary.__str__ (print overloading)
  # ---------------------------------------------------------------------------
  def __str__(self) :
    return str(self.stack)
  
  # def __repr__(self) :
  #   return str(self.stack)
  
  # def getOverviewStr(self) :
  #   s = [t.getOverviewStr() for t in self.stack]
  #   return str(s)
  
  
  
# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  print("[INFO] Unit tests for the package 'binary.py' will come in a future release.")

