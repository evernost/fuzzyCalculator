# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : -
# File name       : parser.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : parsing machinery for the Fuzzy Calculator
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : Friday, April 11 2025
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# EXTERNALS
# =============================================================================
# Project libraries
import src.symbols as symbols
import src.utils as utils
from src.commons import Status

# Standard libraries
from enum import Enum



# =============================================================================
# CONSTANTS
# =============================================================================
# None.



# =============================================================================
# EXPRESSION()
# =============================================================================
class Expression : 
  
  """
  EXPRESSION class definition

  An Expression object is a container for a mathematical expression.
  The expression is provided as a simple string. 
  
  The object provides all the methods to parse and evaluate this string.

  Elements listed in 'Expression.variables' need to be linked to an actual 
  Variable object, so that the evaluator can call their 'Variable.sample()' 
  attribute.

  Examples:
  > Expression("sin(x + y)")
  > Expression("(a-b)(a+3b)")
  > Expression("1/(2pi*(R1//R2)C)")
  > Expression("12+logN(10,2)/4")
  > Expression("3+logN(10, exp(y-2)+1)/4")
  > Expression("-3exp(-9t)")

  Options: 
  - quiet mode  : turns off all outputs (even errors)
  - verbose mode: prints additional info relative to the parsing
  - debug mode  : prints extra info for investigation
  """

  def __init__(self, input, quiet = False, verbose = False, debug = False) :
    
    # Input expression
    self.input = input
    
    # Populated after calling "tokenise()"
    self.tokens     = []    # Same as 'input', but expressed as a list of tokens
    self.variables  = []    # Variables found in the expression
    self.nInfix     = 0     # Number of infix operators found
    self.nOp        = 0     # Number of operands found (TODO: is it recursive?)

    # Status of the compilation steps
    self.statusSyntaxCheck  = Status.NOT_RUN
    self.statusTokenise     = Status.NOT_RUN
    self.statusBalance      = Status.NOT_RUN
    self.statusNest         = Status.NOT_RUN
    self.statusStage        = Status.NOT_RUN

    # Options
    self.QUIET_MODE   = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE   = debug



  # ---------------------------------------------------------------------------
  # METHOD: Expression.syntaxCheck()
  # ---------------------------------------------------------------------------
  def syntaxCheck(self) -> Status :
    """
    Runs basic tests on the input string to ensure the expression is 
    well-formed and suitable for parsing.

    Result is also available in 'Expression.statusSyntaxCheck'.
    """
    
    self.statusSyntaxCheck = Status.OK

    if not(self._validCharCheck()) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Expression check: input contains invalid chars.")
      self.statusSyntaxCheck = Status.FAIL
      
    if not(self._bracketBalanceCheck()) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Expression check: invalid bracket balance.")
      self.statusSyntaxCheck = Status.FAIL
      
    if not(self._firstOrderCheck()) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Expression check: invalid character sequence.")
      self.statusSyntaxCheck = Status.FAIL

    if not(self.QUIET_MODE) :
      if (self.statusSyntaxCheck == Status.OK) :
        if self.VERBOSE_MODE :
          print("[INFO] Syntax check: SUCCESS")
      else :
        print("[ERROR] Syntax check: FAILED")
 
    return self.statusSyntaxCheck



  # ---------------------------------------------------------------------------
  # METHOD: Expression._validCharCheck()                              [PRIVATE]
  # ---------------------------------------------------------------------------
  def _validCharCheck(self) -> Status :
    """
    Checks if the expression string is made of valid characters only.
    
    Valid characters are:
    - letters: "a" to "z" and "A" to "Z"
    - space: " "
    - digits: "0" to "9"
    - minus sign: "-"
    - dot: "."
    - comma: ","
    - underscore "_"
    - round brackets: "(" and ")"
    - characters in the infix op list

    Returns True if the check passed, False otherwise.

    NOTE
    In case you want to add custom infix operators, you need to add to the 
    'white list' any special character you want to use.

    EXAMPLES
    (See unit tests in "main")
    """

    # List all chars contained in infixes
    infixListExp = []
    for t in symbols.INFIX :
      infixListExp += list(t["name"])
    
    for (loc, char) in enumerate(self.input) :
      alphaTest   = utils.isAlpha(char)
      digitTest   = utils.isDigit(char)
      infixTest   = (char in infixListExp)
      othersTest  = (char in [" ", ".", ",", "_", "(", ")"])
      
      if not(alphaTest or digitTest or infixTest or othersTest) :
        if not(self.QUIET_MODE) :
          utils.showInStr(self.input, loc)
          print("[ERROR] This character is not supported by the parser.")
        return Status.FAIL

    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression._bracketBalanceCheck()                         [PRIVATE]
  # ---------------------------------------------------------------------------
  def _bracketBalanceCheck(self) -> Status :
    """
    Checks if the parentheses in the input expression are valid.
    "lazy parenthesis" are allowed: matching closing parenthesis 
    are not required.

    Returns True if the check passed, False otherwise.

    EXAMPLES
    (See unit tests in "main")
    """

    level = 0
    for (loc, char) in enumerate(self.input) :
      if (char == "(") :
        level += 1
      elif (char == ")") :
        level -= 1

      if (level < 0) :
        if not(self.QUIET_MODE) :
          utils.showInStr(self.input, loc)
          print("[ERROR] Closing parenthesis in excess.")
        return Status.FAIL

    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression._firstOrderCheck()                             [PRIVATE]
  # ---------------------------------------------------------------------------
  def _firstOrderCheck(self) -> Status :
    """
    Takes the chars 2 by 2 in the expression and detects invalid combinations.
    Detailed list of the valid/invalid combinations can be found in 
    "resources/firstOrderCheck.xslx"
    
    Returns True if the check passed, False otherwise.

    EXAMPLES
    (See unit tests in "main")
    """

    for i in (range(len(self.input)-1)) :
      
      char1 = self.input[i]; char2 = self.input[i+1]

      if ((char1, char2) == (".", ".")) :
        if not(self.QUIET_MODE) :
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: a valid expression cannot have 2 consecutive dots. Is it a typo?")
        return Status.FAIL
        
      elif ((char1, char2) == (",", ",")) :
        if not(self.QUIET_MODE) :
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: a valid expression cannot have 2 consecutive commas. Is it a typo?")
        return Status.FAIL

      elif ((char1, char2) == (",", ")")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: possible missing argument?")
        return Status.FAIL
      
      elif ((char1, char2) == (",", "+")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: '+' cannot follow ','. Please refer to the parsing rules.")
        return Status.FAIL
      
      # TODO: same holds for any infix operator the user might have declared

      elif ((char1, char2) == ("(", ")")) :
        if not(self.QUIET_MODE) :    
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: content between parethesis cannot be left empty.")
        return Status.FAIL
      
      elif ((char1, char2) == ("(", "+")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: '+' cannot follow '('. Please refer to the parsing rules.")
        return Status.FAIL
      
      elif ((char1, char2) == ("+", ",")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: ',' cannot follow '+'. Please refer to the parsing rules.")
        return Status.FAIL

      # 
      # TODO: this section needs to be completed.
      # 

      else :
        pass

    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression.tokenise()
  # ---------------------------------------------------------------------------
  def tokenise(self) -> "Expression.Status" :
    """
    Converts the input string to a list of tokens.

    The input characters are read, grouped and classified to an abstract type
    (Token objects) while preserving their information.
    
    Implicit multiplications like in '3cos(-2t)' are detected and explicited.

    Conversion status is returned by the function and also available in 
    'Expression.statusTokenise'

    If successful, the output product is generated in 'Expression.tokens'.

    This function assumes that syntax checks have been run before.
    Otherwise, some syntax errors might not be caught and could yield odd 
    results.
    """
    
    self.statusTokenise = Status.OK

    # Make sure the previous steps were successful
    if (self.statusSyntaxCheck == Status.FAIL) :
      if not(self.QUIET_MODE) : print("[WARNING] Expression.tokenise() skipped due to previous errors.")
      self.statusTokenise = Status.NOT_RUN
      return self.statusTokenise
    elif (self.statusSyntaxCheck == Status.NOT_RUN) :
      if not(self.QUIET_MODE) : print("[WARNING] Expression.syntaxCheck() must be run before Expression.tokenise()")
      self.statusTokenise = Status.NOT_RUN
      return self.statusTokenise

    # Call the tokeniser
    ret = self._tokeniseReader()
    
    if (ret == Status.OK) :

      # Explicit the hidden multiplications
      self._tokeniseExplicitMult()

      # List the variables
      self._tokeniseListVars()

      # Run syntax check on the token sequence
      self._tokeniseSyntaxCheck()

    if self.VERBOSE_MODE :
      if (self.statusTokenise == Status.OK) :
        print("[INFO] Tokenise: SUCCESS")
      else :
        print("[ERROR] Tokenise: FAILED")

    return self.statusTokenise



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseReader()                              [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseReader(self) -> "Expression.Status" :
    """
    Core processing function of the tokenise operation.

    Processes the input 'Expression.input'
    Result is available in 'Expression.tokens'
    """
    
    buffer = self.input
    self.tokens = []

    while(len(buffer) > 0) :

      # Remove whitespaces (rule [R9])
      (_, buffer) = utils.splitSpace(buffer)
      
      if (len(buffer) == 0) :
        break

      # Try to interpret the leading characters as a 
      # number, constant, variable, function or infix.
      # TODO: detect and handle conflicts.
      (number,    tailNumber)     = utils.consumeNumber(buffer)
      (constant,  tailConstant)   = utils.consumeConst(buffer)
      (function,  tailFunction)   = utils.consumeFunc(buffer)
      (variable,  tailVariable)   = utils.consumeVar(buffer)
      (infix,     tailInfix)      = utils.consumeInfix(buffer)

      if (number != "") :
        self.tokens.append(symbols.Token(number))
        buffer = tailNumber

      elif (constant != "") :
        self.tokens.append(symbols.Token(constant))
        buffer = tailConstant
      
      elif (function != "") :
        self.tokens.append(symbols.Token(function))
        self.tokens.append(symbols.Token("("))
        buffer = tailFunction

      elif (variable != "") :
        self.tokens.append(symbols.Token(variable))
        buffer = tailVariable
        
      elif (infix != "") :
        self.tokens.append(symbols.Token(infix))
        buffer = tailInfix
      
      # Otherwise: detect brackets and commas
      else :
        (head, tail) = utils.pop(buffer)

        if (head == "(") :
          self.tokens.append(symbols.Token(head))
          buffer = tail

        elif (head == ")") :
          self.tokens.append(symbols.Token(head))
          buffer = tail

        elif (head == ",") :
          self.tokens.append(symbols.Token(head))
          buffer = tail
          
        else :
          if not(self.QUIET_MODE) :
            print(f"[ERROR] Internal error: the input char '{head}' could not be assigned to any Token.")
          self.statusTokenise = Status.FAIL
          return Status.FAIL

    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseExplicitMult()                        [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseExplicitMult(self) -> Status :
    """
    Detects and expands implicit multiplications in a list of tokens.
    Updates the internal list of tokens with the multiplication tokens
    explicited at the right place.

    This function is usually called from 'Expression.tokenise()'

    The function does not return any status.
    """
    
    nTokens = len(self.tokens)

    # A hidden multiplication needs at least 2 tokens.
    if (nTokens <= 1) :
      return Status.OK

    else :
      output = []
      
      # Read the tokens 2 by 2, with a 1 overlap.
      # If the tokens are "ABCDE..." the loop will read
      # "AB" then "BC", "CD", "DE", etc.
      for n in range(nTokens-1) :
        T1 = self.tokens[n]; T2 = self.tokens[n+1]

        output.append(T1)
        
        # Example: "pi(x+4)"
        if ((T1.type, T2.type) == ("CONSTANT", "BRKT_OPEN")) :
          output.append(symbols.Token("*"))

        # Example: "R1C1*cos(x)"
        elif ((T1.type, T2.type) == ("VAR", "VAR")) :
          output.append(symbols.Token("*"))

        # Example: "R1(R2+R3)"
        elif ((T1.type, T2.type) == ("VAR", "BRKT_OPEN")) :
          output.append(symbols.Token("*"))

        # Example: "x_2.1"
        elif ((T1.type, T2.type) == ("VAR", "NUMBER")) :
          output.append(symbols.Token("*"))

        # Example: "(x+1)pi"
        elif ((T1.type, T2.type) == ("BRKT_CLOSE", "CONSTANT")) :
          output.append(symbols.Token("*"))

        # Example: "(x+1)cos(y)"
        elif ((T1.type, T2.type) == ("BRKT_CLOSE", "FUNCTION")) :
          output.append(symbols.Token("*"))

        # Example: "(R2+R3)R1"
        elif ((T1.type, T2.type) == ("BRKT_CLOSE", "VAR")) :
          output.append(symbols.Token("*"))

        # Example: "(x+y)(x-y)"
        elif ((T1.type, T2.type) == ("BRKT_CLOSE", "BRKT_OPEN")) :
          output.append(symbols.Token("*"))

        # Example: "(x+y)100"
        elif ((T1.type, T2.type) == ("BRKT_CLOSE", "NUMBER")) :
          output.append(symbols.Token("*"))

        # Example: "2pi"
        elif ((T1.type, T2.type) == ("NUMBER", "CONSTANT")) :
          output.append(symbols.Token("*"))

        # Example: "2exp(t)"
        elif ((T1.type, T2.type) == ("NUMBER", "FUNCTION")) :
          output.append(symbols.Token("*"))

        # Example: "2x"
        elif ((T1.type, T2.type) == ("NUMBER", "VAR")) :
          output.append(symbols.Token("*"))

        # Example: "2(x+y)"
        elif ((T1.type, T2.type) == ("NUMBER", "BRKT_OPEN")) :
          output.append(symbols.Token("*"))
        
        # Anything else: no multiplication hidden
        else :
          pass
      
      if (n == (nTokens-2)) :
        output.append(T2)

    if (self.VERBOSE_MODE) :
      nAdded = len(output) - nTokens
      if (nAdded == 1) :
        print("[INFO] Tokenise: added 1 implicit multiplication")
      elif (nAdded > 1) :
        print(f"[INFO] Tokenise: added {nAdded} implicit multiplications")

    self.tokens = output
    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseListVars()                            [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseListVars(self) -> Status :
    """
    Inspects the expression in tokenised form and returns the list of all the 
    variables found.

    In verbose mode, the function logs the variables found.

    Returns a status OK when done (the function can't fail)
    """

    self.variables = []

    for T in self.tokens :
      if (T.type == "VAR") :
        if not(T.name in self.variables) :
          self.variables.append(T.name)

          if self.VERBOSE_MODE :
            print(f"[INFO] Tokenise: new variable found: '{T.name}'")

    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseSyntaxCheck()                         [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseSyntaxCheck(self) -> Status :
    """
    Takes the tokens 2 by 2 from the list of Tokens and detects any invalid 
    combination.
    Detailed list of the valid/invalid combinations can be found in 
    'resources/secondOrderCheck.xslx'
    
    It is a complement to 'Expression.syntaxCheck()'.
    Some checks are easier to do on a list of tokens rather than the raw 
    input expression.
    
    Returns True if the check passed, False otherwise.

    EXAMPLES
    > _tokeniseSyntaxCheck(...) -> Status.FALSE (TODO)
    
    See unit tests in 'main()' for more examples.
    """

    nTokens = len(self.tokens)

    # STEP 1: check tokens by pairs
    for i in range(nTokens-1) :
      T1 = self.tokens[i]; T2 = self.tokens[i+1]

      if (T1.type == "FUNCTION") :
        if not(T2.type == "BRKT_OPEN") :
          if not(self.QUIET_MODE) :
            print(f"[ERROR] A function must be followed with a parenthesis (Rule R3).")
          return Status.FAIL      
        else :
          pass
      
      # 
      # TODO: this section needs to be completed with all the possible pairs of tokens.
      # 

    # STEP 2: check how the sequence of tokens ends
    T = self.tokens[nTokens-1]
    if (T.type == "FUNCTION") :
      if not(self.QUIET_MODE) :
        print(f"[ERROR] An expression cannot end with a function.")
      return Status.FAIL

    elif (T.type == "BRKT_OPEN") :
      if not(self.QUIET_MODE) :
        print(f"[ERROR] An expression cannot end with an opening parenthesis.")
      return Status.FAIL
    
    elif (T.type == "INFIX") :
      if not(self.QUIET_MODE) :
        print(f"[ERROR] An expression cannot end with an infix operator.")
      return Status.FAIL

    # STEP 3: return status
    return Status.OK



  # ---------------------------------------------------------------------------
  # METHOD: Expression.balance()
  # ---------------------------------------------------------------------------
  def balance(self) -> Status :
    """
    Balances the minus signs used as a shortcut for the 'opposite' function by
    adding the implicit zero.
    Takes as input the expression as list of tokens and adds (in place) the 
    'minus' infix operators fully expanded.
        
    Expression 'balancing' has 2 different scenarios that require different
    processing:
    - Low precedence context: "-2+x" -> "0-2+x"
    - High precedence context: "1+2^-x/4"

    Please refer to rules [R7.X] in 'doc/parsingRules.md'
    """
    
    # The previous steps failed
    if (self.statusTokenise == Status.FAIL) :
      if not(self.QUIET_MODE) : print("[WARNING] Expression.balance() skipped due to previous errors.")
      self.statusBalance = self.Status.NOT_RUN
      return self.statusBalance
    
    # The previous steps were skipped
    elif (self.statusSyntaxCheck == Status.NOT_RUN) :
      if not(self.QUIET_MODE) : print("[WARNING] Expression.tokenise() must be run before Expression.balance()")
      self.statusBalance = Status.NOT_RUN
      return self.statusBalance

    # Add zeros in low priority context (rule [7.1])
    self.tokens = explicitZerosWeak(self.tokens)
    
    # Add zeros in high priority context (rules [7.2] and [7.3])
    self.tokens = explicitZeros(self.tokens)

    return Status.OK
  


  # ---------------------------------------------------------------------------
  # METHOD: Expression.nest()
  # ---------------------------------------------------------------------------
  def nest(self) -> Status :
    """
    Nests the list of tokens.
    
    The nesting operation consists in isolating tokens between round
    brackets - '(' and ')' - and storing them in a bigger Token object.

    In that case, since the 'big' Token contains an expression, it becomes a Macro
    object (a sort of "super-Token")

    After this function call, the list of Tokens becomes a recursive structure 
    that makes the next operations (staging, evaluation) much easier.
    
    In some cases, a 'Macro' object carries a top level function that applies 
    to the terms betweens parenthesis. 
    This accounts for the difference between 'simple parenthesis' 
    (isolating a part of the expression) and parenthesis in the context of a 
    function call:
    - For 'simple' parenthesis, the terms are stored in a dedicated internal 
      expression, the top level function is void ('identity' function)
    - For 'function' parenthesis, the function is used as the top level 
      function, the terms in-between are stored in the internal expression.
    
    See the examples for more information. 
    """

    # Note: nestProcessor() and nestCheck() are externalised because they are shared
    # with the Macro object.
    (self.tokens, status) = nestProcessor(self.tokens)
    if (status == Status.FAIL) :
      return status  
    
    self.statusNest = nestCheck(self.tokens) 
    
    

  # ---------------------------------------------------------------------------
  # METHOD: Expression.stage()
  # ---------------------------------------------------------------------------
  def stage(self) :
    """
    Isolates (stages) the operators with higher relative precedence so that the 
    operations are done in the right order.

    Operators and the operands are isolated in a Macro expression, in a 
    similar principle to 'Expression.nest()'

    The list of Tokens ends up being simplified to an expression involving 
    operators with lowest priority only.

    The function does not assume commutativity of the infix operators.
    """

    self.statusStage = False

    if not(self.statusBalance) :
      if not(self.QUIET_MODE) : print("[WARNING] Expression.stage() skipped due to previous errors.")
      return self.statusStage

    (nTokens, nLeaves, nInfix) = utils.countTokens(self.tokens)

    # Staging is required as soon as there are 2 or more infix: "L op L op L"
    if (nInfix >= 2) :
      
      # STEP 1: look for the infix of highest priority in [L op L op L ...]
      (minPriority, maxPriority) = self._getPriorityRange()
      # print(f"[DEBUG] Binary.nest(): priority range = ({minPriority}, {maxPriority})")
      
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
        (minPriority, maxPriority) = self._stagePriorityRange()

      # END: stacks now looks like [L op L op L], all with identical precedence.

    # Only 1 infix operator: nothing to do, leave the stack as it is.
    else :
      pass



    # Stage the content of the macros
    for T in self.tokens :
      if (T.type == "MACRO") :
        T.stage()



  # ---------------------------------------------------------------------------
  # METHOD: Expression._stagePriorityRange()                          [PRIVATE]
  # ---------------------------------------------------------------------------
  def _stagePriorityRange(self) :
    """
    Inspects the list of tokens and returns the (min, max) priority of the
    infix operators encountered.
    
    The function is not recursive: content of the macros is not inspected.

    Returns (-1, -1) when there is no infix in the list.
    """
    
    firstInfix = True
    minPriority = -1
    maxPriority = -1

    for T in self.tokens :
      if (T.type == "INFIX") :
        if firstInfix :
          minPriority = T.priority
          maxPriority = T.priority
          firstInfix = False
        else :
          if (T.priority > maxPriority) :
            maxPriority = T.priority

          if (T.priority < minPriority) :
            minPriority = T.priority

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





  # # ---------------------------------------------------------------------------
  # # METHOD: Binary.nest()
  # # ---------------------------------------------------------------------------
  # def nest(self) :
  #   """
  #   Simplifies the stack to an expression involving operators with lowest priority
  #   only.
    
  #   Rewriting is done by repeatingly isolating away the operators of higher priority
  #   and their operands in a Macroleaf.

  #   It does not assume commutativity of the infix operators.

  #   Associativity strategy are detailed in [R10].
    
  #   Note: minus signs '-' must have been balanced prior to calling this function
  #   (function 'balanceMinus')
  #   """
    
  #   # CHECK 1: number of nodes must be even.
  #   if ((self.nNodes % 2) == 0) :
  #     print(f"[ERROR] Binary.nest(): cannot nest an even number of nodes (size = {self.nNodes})")
  #     exit()

  #   # CHECK 2: nodes in the stack (top level and macros) must follow a 'L op L ... op L' pattern
  #   nInfix = 0
  #   for (n, element) in enumerate(self.stack) :        
  #     if ((n % 2) == 0) :
  #       if (not(element.type in ["NUMBER", "VAR", "CONSTANT", "MACRO"])) :
  #         print("[ERROR] Binary.nest(): the expression does not follow the pattern [L op L op ...] (ERR_NOT_A_LEAF)")
  #         exit()

  #     else :
  #       if (element.type != "INFIX") :
  #         print("[ERROR] Binary.nest(): the expression to nest does not follow the pattern [L op L op ...] (ERR_NOT_AN_INFIX)")
  #         exit()

  #       else :
  #         nInfix += 1

  #   # Nest the stacks in the Macroleaves
  #   for element in self.stack :
  #     if (element.type == "MACRO") :
  #       element.nest()

  #   # Nest the actual stack.
  #   # Nesting can be required as soon as there are 2 or more infix: "L op L op L"
  #   # i.e. more than 5 nodes.
  #   if (nInfix >= 2) :
      
  #     # STEP 1: look for the infix of highest priority in [L op L op L ...]
  #     (minPriority, maxPriority) = self._getPriorityRange()
  #     # print(f"[DEBUG] Binary.nest(): priority range = ({minPriority}, {maxPriority})")
      
  #     # Call to "nest()" is necessary if there are 2 different levels of priority
  #     while (maxPriority != minPriority) :

  #       # STEP 2: split apart the highest operator and its adjacent leaves
  #       # from the rest: [L op L op], [L op L], [op L op L op L op L]
  #       (chunks, chunkNeedsMacro) = self._splitOp(maxPriority)

  #       # STEP 3: create a macro for the highest operators 
  #       # Result = [L op L op], M, [op L op L op L op L]
  #       # Then merge into a new stack.
  #       if (len(chunks) > 1) :
  #         newStack = []
  #         for i in range(len(chunks)) :
  #           if chunkNeedsMacro[i] :
  #             M = macroleaf.Macroleaf(function = "id", tokenList = chunks[i])
  #             newStack.append(M)
            
  #           else :
  #             newStack += chunks[i]

  #         self.stack = newStack

  #         # TODO: update the other properties
  #         self.nNodes = len(self.stack)
  #         # self.nLeaves = ...
        
  #       # STEP 4: repeat until the stack is 'flat' 
  #       # (all operators have the same priority)
  #       (minPriority, maxPriority) = self._getPriorityRange()

  #     # END: stacks now looks like [L op L op L], all with identical precedence.

  #   # Only 1 infix operator: nothing to do, leave the stack as it is.
  #   else :
  #     pass



# -----------------------------------------------------------------------------
# FUNCTION: nestProcessor()                                         [RECURSIVE]
# -----------------------------------------------------------------------------
def nestProcessor(tokens, quiet = False, verbose = False, debug = False) :
  """
  Consumes a list of tokens, returns another list of tokens where functions and 
  round brackets are replaced with a Macro token.

  Note: this function is recursive.
  """
  
  nTokens = len(tokens)

  # CASE 1: empty list
  if (nTokens == 0) :
    return ([], Status.OK)

  # CASE 2: singleton token
  elif (nTokens == 1) :
    if tokens[0].type in ("BRKT_OPEN", "BRKT_CLOSE", "FUNCTION") :
      if not(quiet) : print("[WARNING] nestProcessor(): input is not nestable (singleton meaningless token)")
      return (tokens, Status.FAIL)
    else :
      return (tokens, Status.OK)
  
  # CASE 3: most general case
  else :
    (tokensFlat, tokensRecurse) = utils.consumeFlat(tokens)

    # The input has no recursive part
    if not(tokensRecurse) :
      return (tokens, Status.OK)
    
    # The input has at least one recursive element
    else :
      
      # CASE 1: function or opening bracket
      if ((tokensRecurse[0].type == "BRKT_OPEN") or (tokensRecurse[0].type == "FUNCTION")) :
        
        # Create a Macro object from the recursive part
        M = symbols.Macro(tokensRecurse)
        if (M.statusArgs != Status.OK) :
          print("[ERROR] nestProcessor(): Macro generation failed.")
          return ([], Status.FAIL)

        rem = M.getRemainder()
        
        # Nest the macro's remainder (recursive call to 'nestProcessor')
        (remNested, status) = nestProcessor(rem)
        if (status != Status.OK) :
          print("[ERROR] nestProcessor(): error(s) occurred while nesting in a Macro.")
          return ([], Status.FAIL)
        
        # Concatenate and return the result
        return (tokensFlat + [M] + remNested, Status.OK)

      # CASE 2: comma (not possible in this context -> syntax error)
      elif (tokensRecurse[0].type == "COMMA") :
        if not(quiet) : print("[WARNING] nestProcessor(): possible uncaught syntax error (comma at top level)")
        return ([], Status.FAIL)

      # CASE 3: closing parenthesis (not possible in this context -> syntax error)
      elif (tokensRecurse[0].type == "BRKT_CLOSE") :
        if not(quiet) : print("[WARNING] nestProcessor(): possible closing parenthesis in excess")
        return ([], Status.FAIL)

      # CASE 4: anything else (-> syntax error)
      else :
        if not(quiet) : print("[WARNING] nestProcessor(): possible uncaught syntax error (unexpected token)")
        return ([], Status.FAIL)



# -----------------------------------------------------------------------------
# FUNCTION: nestArg()
# -----------------------------------------------------------------------------
def nestArg(tokens, quiet = False, verbose = False, debug = False) :
  """
  Weaker version of nest() specific to arguments processing: 
  - function content
  - round parenthesis content
  
  Like 'nest()' the function returns a nested list of tokens. 
  
  Unlike 'nest()', it halts on ',' and ')' and returns the remainder.
  Therefore, the return objects are:
  - the nested list of tokens
  - the remainder

  'nest()' consumes all the tokens, hence it does not return a remainder.
  'nestArg()' must stop when the argument processing is done.
  """
  
  nTokens = len(tokens)

  # List of tokens is empty: nothing to do
  if (nTokens == 0) :
    return ([], [])

  # List of tokens has 1 element
  elif (nTokens == 1) :
    if tokens[0].type in ("BRKT_OPEN", "BRKT_CLOSE", "FUNCTION") :
      if not(quiet) : print("[WARNING] utils.nestArg(): odd input (single meaningless token)")
      return (tokens, [])
    else :
      return (tokens, [])
  
  # List of tokens with > 1 element
  else :
    (tokensFlat, remainder) = utils.consumeFlat(tokens)

    if not(remainder) :
      return (tokens, [])

    else :
      if (remainder[0].type in ("BRKT_OPEN", "FUNCTION")) :
        
        # Create a Macro object with the new context as input
        M = symbols.Macro(remainder)
        
        # Nest what is not part of the macro
        # TODO: not sure 'nestArg' must be called here
        rem = M.getRemainder()
        (arg, rem) = nestArg(rem)
        
        return (tokensFlat + [M] + arg, rem)

      elif (remainder[0].type == "COMMA") :  
        if (len(remainder) >= 2) :
          # Note: the comma is included in 'remainder' so that it is
          # easier to detected if there are too many arguments
          return (tokensFlat, remainder)
        else :
          if not(quiet) : print("[WARNING] utils.nestArg(): possible missing argument")
          return (tokensFlat, [])

      elif (remainder[0].type == "BRKT_CLOSE") :
        if (len(remainder) > 1) :
          return (tokensFlat, remainder[1:])
        else :
          return (tokensFlat, [])

      else :
        if not(quiet) : print("[WARNING] Expression.nest(): possible uncaught syntax error (unexpected token)")
        return (tokens, [])



# ---------------------------------------------------------------------------
# FUNCTION: nestCheck()
# ---------------------------------------------------------------------------
def nestCheck(tokens, quiet = False, verbose = False, debug = False) :
  """
  Checks the outcome of the 'nest()' operation.
  
  After nesting, the list of tokens should look like 'L op L op ... op L'
  where 'L' is a leaf (number, variable, constant, macro) and 'op' is an 
  infix operator.
  """

  # CHECK 1: number of tokens must be odd.
  if ((len(tokens) % 2) == 0) :
    if not(quiet) : 
      print("[ERROR] Nesting returned an even number of tokens. Something wrong happened (possible internal error).")
      return Status.FAIL

  # CHECK 2: tokens (at top level and in macros) must follow a 'L op L ... op L' pattern.
  nInfix = 0
  for (n, element) in enumerate(tokens) :        
    if ((n % 2) == 0) :
      if (not(element.type in ["NUMBER", "VAR", "CONSTANT", "MACRO"])) :
        print("[ERROR] The nested expression does not follow the pattern 'L op L op ... L' (unexpected leaf)")
        return Status.FAIL

    else :
      if (element.type != "INFIX") :
        print("[ERROR] The nested expression does not follow the pattern [L op L op ...] (unexpected infix)")
        return Status.FAIL

      else :
        nInfix += 1

  # CHECK 3: check recursively inside the Macro
  for T in tokens :
    if (T.type == "MACRO") :
      status = T.nestCheck()

      if (status == Status.FAIL) :
        return Status.FAIL

  return Status.OK



# ---------------------------------------------------------------------------
# FUNCTION: explicitZeros()
# ---------------------------------------------------------------------------
def explicitZeros(tokens, quiet = False, verbose = False, debug = False) :
  """
  This function is part of the 'balancing' operation.
  
  Adds a '0' Token to the list of tokens every time the minus sign '-' 
  is meant as the 'opposite' function.
  
  This variant of the function adds the implicit zeros when they appear 
  in a mixed priority context i.e. where it combines operators with different
  precedence as '-'.
  Example: "2^-4+3" -> "2^Macro+3"
  """
  
  nTokens = len(tokens)
  
  # Using the "-" in the context of rule [7.2]/[7.3] requires at least 4 elements
  # Example: "2^-4"
  if (nTokens >= 4) :
    output = []
    
    n = 0
    while (n <= (nTokens-2)) :
      eltA = tokens[n]; eltB = tokens[n+1]

      # ---------------------------
      # Detect the "^-" combination
      # ---------------------------
      if ((eltA.type == "INFIX") and (eltB.type == "INFIX")) :
        if ((eltA.id == "^") and (eltB.id == "-")) :
          
          # Guard
          if ((n+2) > (nTokens-1)) :
            print("[ERROR] utils.explicitZeros(): premature end; it should have been caught before the balancing operation.")
            exit()
          
          M = symbols.Macro([symbols.Token("opp"), symbols.Token("("), tokens[(n+2)]])
          output.append(eltA)
          output.append(M)
          n += 3
          if debug : print("[DEBUG] utils.explicitZeros(): added a Token because of implicit call to 'opp'.")

      # ------------------------------------------------
      # Detect any other combination of an infix and "-"
      # ------------------------------------------------
      elif ((eltA.type == "INFIX") and (eltB.type == "INFIX")) :
        if (eltB.id == "-") :
          print("[WARNING] Odd use of '-' with implicit 0. Cross check the result or use parenthesis.")

          # Guard
          if ((n+2) > (nTokens-1)) :
            print("[ERROR] Premature end; it should have been caught before calling 'utils.explicitZeros()'")
            exit()

          M = symbols.Macro([symbols.Token("opp"), symbols.Token("("), tokens[(n+2)]])
          #M = macroleaf.Macroleaf(function = "opp", tokenList = [tokens[n+2]])
          output.append(eltA)
          output.append(M)
          n += 3
          print("[DEBUG] utils.explicitZeros(): added a Token because of implicit call to 'opp'.")

        else :
          print("[ERROR] Invalid combination of infixes; it should have been caught before calling 'utils.explicitZeros()'")
          exit()

      # ---------------
      # Last 2 elements
      # ---------------
      elif (n == (nTokens-2)) :
        output.append(eltA)
        output.append(eltB)
        n += 1

      # ------------------------
      # Nothing special detected
      # ------------------------
      else :
        output.append(eltA)
        n += 1

    return output

  # Less than 4 elements
  # There is nothing to be expanded.
  # TODO: maybe recursively?
  else :
    return tokens
    # for elt in self.stack :
      # if (elt.type == "MACRO") :
        # elt._minusAsOpp()
    


# ---------------------------------------------------------------------------
# FUNCTION: explicitZerosWeak()
# ---------------------------------------------------------------------------
def explicitZerosWeak(tokens) :
  """
  This function is part of the 'balancing' operation.
  
  Adds a '0' Token to the list of tokens every time the minus sign '-' 
  is meant as the 'opposite' function.
  
  This variant of the function adds the implicit zeros when they appear 
  in a low priority context (like additions) i.e. where all operators have
  the same precedence as '-'.
  Example: "-2+3x" -> "0-2+3x"

  Incidentally, the only possible location for the '0' token is at the
  beginning of an expression/context.

  All the other cases (like "2^-4") are more complex because they need to 
  isolate the context and create a Macro. 
  For that case, use the function 'explicitZeros' instead.
  """
  
  nTokens = len(tokens)
  
  # Detect a "-..." pattern.  
  # Using the "-" in the context of rule [7.1] requires at least 2 elements.
  # Example: "-x"
  if (nTokens >= 2) : 
    if (tokens[0].type == "INFIX") :
      if (tokens[0].id == "-") :
        tokens = [symbols.Token("0")] + tokens

  return tokens



# ---------------------------------------------------------------------------
# FUNCTION: countTokens()
# ---------------------------------------------------------------------------
def countTokens(tokens) :
  """
  Inspects the list of tokens and returns:
  - the number of tokens
  - the number of infix operators
  - the number of leaves
  The function is not recursive (macros will not be inspected)
  """
  
  nTokens = len(tokens)
  nInfix = 0
  nLeaves = 0
  for T in tokens :
    if T.type in ["NUMBER", "VARIABLE", "CONSTANT", "MACRO"] : nLeaves += 1
    if (T.type == "INFIX") : nInfix += 1

  return (nTokens, nLeaves, nInfix)
















# =============================================================================
# UNIT TESTS
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")
  assert(Expression("oni_giri*cos(2x+pi"  , quiet=True)._validCharCheck() == Status.OK)
  assert(Expression("input Str"           , quiet=True)._validCharCheck() == Status.OK)
  assert(Expression("input Str2.1(a+b)|x|", quiet=True)._validCharCheck() == Status.FAIL)
  assert(Expression("$inputStr"           , quiet=True)._validCharCheck() == Status.FAIL)
  assert(Expression("µinputStr"           , quiet=True)._validCharCheck() == Status.FAIL)
  assert(Expression("in#putStr"           , quiet=True)._validCharCheck() == Status.FAIL)
  assert(Expression("inputStr%"           , quiet=True)._validCharCheck() == Status.FAIL)
  assert(Expression("inpuétStr"           , quiet=True)._validCharCheck() == Status.FAIL)
  assert(Expression("inpuàtStr"           , quiet=True)._validCharCheck() == Status.FAIL)
  print("- Unit test passed: 'Expression._sanityCheck()'")

  assert(Expression("oni_giri*cos(2x+pi"      , quiet=True)._bracketBalanceCheck() == Status.OK)
  assert(Expression("oni_giri*cos(2x+pi("     , quiet=True)._bracketBalanceCheck() == Status.OK)
  assert(Expression("|3x+6|.2x"               , quiet=True)._bracketBalanceCheck() == Status.OK)
  assert(Expression("oni_giri*cos(2x+pi()))"  , quiet=True)._bracketBalanceCheck() == Status.FAIL)
  print("- Unit test passed: 'Expression._bracketBalanceCheck()'")

  assert(Expression("1+2x//4cos(exp(-t" , quiet=True)._firstOrderCheck() == Status.OK)
  assert(Expression("sin(2..1x)"        , quiet=True)._firstOrderCheck() == Status.FAIL)
  assert(Expression("1+Q(2,)"           , quiet=True)._firstOrderCheck() == Status.FAIL)
  assert(Expression("cos(3x+1)*Q(2,,1)" , quiet=True)._firstOrderCheck() == Status.FAIL)
  print("- Unit test passed: 'Expression._firstOrderCheck()'")

  
  print("[INFO] End of unit tests.\n")



  # --------
  # EXAMPLES
  # --------
  #e = Expression("1+sin(2+exp(-9t)+1)", verbose = True)
  #e = Expression("1+2*pi*R1C1cos(x/7.1//y*Z+exp(-9t)+1)", verbose = True)
  #e = Expression("sin( a+b*sin(z)/2)(a-2b/tan(x^2 )", verbose = True)
  #e = Expression("(a+b)/(((12-z)+tan(x))/z", verbose = True)
  #e = Expression("sin(a+b)+2", verbose = True)
  #e = Expression("(a)(b)", verbose = True)
  #e = Expression("3+logN(10,2)/4", verbose = True)
  #e = Expression("3+logN(10, exp(y-2)+1)/4", verbose = True)
  #e = Expression("1-exp(3x,y)", verbose = True)
  #e = Expression("3+logN(10, Q(10,0.1/2))/4", verbose = True)
  #e = Expression("-3exp(-9t)", verbose = True)
  e = Expression("exp(ln(x^y)-z)exp(x+y)", verbose = True)
  #e = Expression("2^-3exp(7^-9t)", verbose = True)
  #e = Expression("1+2*3^'", verbose = True)

  print(f"[INFO] Processing expression: '{e.input}'")
  e.syntaxCheck()
  e.tokenise()
  e.balance()

  # TODO:
  e.nest()
  e.stage()
  

  print("[INFO] End of unit tests.")
