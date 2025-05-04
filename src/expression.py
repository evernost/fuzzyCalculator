# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : expression
# File name       : expression.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : 'Expression' object definition
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : April 11th, 2025
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
import src.macro as macro
import src.symbols as symbols
import src.utils as utils



# =============================================================================
# Class definition
# =============================================================================
class Expression : 
  
  """
  EXPRESSION class definition

  An Expression object is a placeholder for a mathematical expression (provided
  as a simple string) enhances it by providing all the methods to parse it
  and in the end, evaluate it.

  Elements listed in 'Expression.variables' need to be linked to an actual 
  Variable object, so that the evaluator can call their 'Variable.sample()' attribute.

  Options: 
  - quiet mode  : turns off all outputs (even errors)
  - verbose mode: prints additional info relative to the parsing
  - debug mode  : prints extra info for investigation
  """
  
  def __init__(self, input, quiet = False, verbose = False, debug = False) :
    self.input = input
    
    # Populated after calling "tokenise()"
    self.tokens = []
    self.variables = []
    
    # Options
    self.QUIET_MODE = quiet
    self.VERBOSE_MODE = verbose
    self.DEBUG_MODE = debug
    


  # ---------------------------------------------------------------------------
  # METHOD: Expression.syntaxCheck()
  # ---------------------------------------------------------------------------
  def syntaxCheck(self) -> bool :
    """
    Performs basic validation to ensure the expression is well-formed and 
    suitable for parsing.

    Returns True when the check passes, False if errors were found.
    """
    
    status = True

    if not(self._validCharCheck()) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Expression check: input contains invalid chars.")
      status = False
      
    if not(self._bracketBalanceCheck()) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Expression check: invalid bracket balance.")
      status = False
      
    if not(self._firstOrderCheck()) :
      if not(self.QUIET_MODE) :
        print("[ERROR] Expression check: invalid character sequence.")
      status = False

    if not(self.QUIET_MODE) :
      if status :
        if self.VERBOSE_MODE :
          print("[INFO] Syntax check: SUCCESS")
      else :
        print("[ERROR] Syntax check: FAILED")

    return status



  # ---------------------------------------------------------------------------
  # METHOD: Expression._validCharCheck()                              [PRIVATE]
  # ---------------------------------------------------------------------------
  def _validCharCheck(self) -> bool :
    """
    Checks if the expression contains valid characters only.
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
    'white list' any special character you might be using.

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
        return False

    return True



  # ---------------------------------------------------------------------------
  # METHOD: Expression._bracketBalanceCheck()                         [PRIVATE]
  # ---------------------------------------------------------------------------
  def _bracketBalanceCheck(self) -> bool :
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
        return False

    return True



  # ---------------------------------------------------------------------------
  # METHOD: Expression._firstOrderCheck()                             [PRIVATE]
  # ---------------------------------------------------------------------------
  def _firstOrderCheck(self) -> bool :
    """
    Takes the chars 2 by 2 and detects any invalid combination.
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
        return False
        
      elif ((char1, char2) == (",", ",")) :
        if not(self.QUIET_MODE) :
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: a valid expression cannot have 2 consecutive commas. Is it a typo?")
        return False

      elif ((char1, char2) == (",", ")")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: possible missing argument?")
        return False
      
      elif ((char1, char2) == (",", "+")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: '+' cannot follow ','. Please refer to the parsing rules.")
        return False
      
      # TODO: same holds for any infix operator the user might have declared

      elif ((char1, char2) == ("(", ")")) :
        if not(self.QUIET_MODE) :    
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: content between parethesis cannot be left empty.")
        return False
      
      elif ((char1, char2) == ("(", "+")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: '+' cannot follow '('. Please refer to the parsing rules.")
        return False
      
      elif ((char1, char2) == ("+", ",")) :
        if not(self.QUIET_MODE) :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: ',' cannot follow '+'. Please refer to the parsing rules.")
        return False

      # 
      # TODO: this section needs to be completed.
      # 

      else :
        pass

    return True



  # ---------------------------------------------------------------------------
  # METHOD: Expression.tokenise()
  # ---------------------------------------------------------------------------
  def tokenise(self) -> bool :
    """
    Generates a list of tokens from the input.

    The input characters are read, grouped and classified to an abstract type
    (Token objects) while preserving their information.
    
    This function assumes that syntax checks have been run prior to the call
    (Expression.check() method)
    Otherwise, some syntax errors might not be caught.

    Outcome is generated in the attribute 'Expression.tokens'.

    Returns True if the operation is successful, False otherwise.
    """

    status = True

    buffer = self.input
    self.tokens = []

    while(len(buffer) > 0) :

      # Remove whitespaces (rule [R9])
      (_, buffer) = utils.splitSpace(buffer)
      
      if (len(buffer) == 0) :
        break

      # Try to interpret the leading characters as a 
      # number, constant, variable, function or infix.
      # TODO: check if there can be conflicts.
      (number, tailNumber)      = utils.consumeNumber(buffer)
      (constant, tailConstant)  = utils.consumeConst(buffer)
      (function, tailFunction)  = utils.consumeFunc(buffer)
      (variable, tailVariable)  = utils.consumeVar(buffer)
      (infix, tailInfix)        = utils.consumeInfix(buffer)

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
          status = False


    # Explicit the hidden multiplications
    self._tokeniseExplicitMult()

    # List the variables
    self._tokeniseListVars()

    # Run syntax check on the token sequence
    self._tokeniseSyntaxCheck()

    if self.VERBOSE_MODE :
      if status :
        print("[INFO] Tokenise: SUCCESS")
      else :
        print("[ERROR] Tokenise: FAILED")

    return status



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseExplicitMult()                        [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseExplicitMult(self) :
    """
    Detects and expands implicit multiplications in a list of tokens.
    Updates the internal list of tokens with the multiplication tokens 
    explicited at the right place.

    This function is usually called from 'Expression.tokenise()'
    """
    
    nTokens = len(self.tokens)

    # Hidden multiplication involves at least 2 tokens.
    if (nTokens <= 1) :
      pass

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



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseListVars()                            [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseListVars(self) :
    """
    Inspects the list of Tokens and returns the list of variables that were 
    found in 'Expression.variables'.
    """

    self.variables = []

    for T in self.tokens :
      if (T.type == "VAR") :
        if not(T.name in self.variables) :
          self.variables.append(T.name)

          if self.VERBOSE_MODE :
            print(f"[INFO] Tokenise: new variable found: '{T.name}'")



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseSyntaxCheck()                         [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseSyntaxCheck(self) :
    """
    Takes the tokens 2 by 2 from the list of Tokens and detects any invalid 
    combination.
    Detailed list can be found in "resources/secondOrderCheck.xslx"
    
    It is a complement to 'Expression.syntaxCheck()'.
    Some checks are easier to do on the list of tokens rather than the raw 
    input expression.
    
    Returns True if the check passed, False otherwise.

    EXAMPLES
    > _tokeniseSyntaxCheck(...) -> False (TODO)
    
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
          return False      
        else :
          pass
      
      
      # 
      # TODO: this section needs to be completed.
      # 

    # STEP 2: check how the sequence of tokens ends
    T = self.tokens[nTokens-1]
    if (T.type == "FUNCTION") :
      if not(self.QUIET_MODE) :
        print(f"[ERROR] An expression cannot end with a function.")
      return False

    elif (T.type == "BRKT_OPEN") :
      if not(self.QUIET_MODE) :
        print(f"[ERROR] An expression cannot end with an opening parenthesis.")
      return False
    
    elif (T.type == "INFIX") :
      if not(self.QUIET_MODE) :
        print(f"[ERROR] An expression cannot end with an infix operator.")
      return False

    # STEP 3: return status
    return True



  # ---------------------------------------------------------------------------
  # METHOD: Expression.nest()
  # ---------------------------------------------------------------------------
  def nest(self) :
    """
    The nesting operation consists in isolating expressions between round
    brackets '(' and ')' and assigning them to their own Expression object.

    That process turns the list of Tokens into a recursive structure that makes 
    the next operations much easier.
    
    Different scenarios can happen:
    - Round brackets used as simple context: the content is nested in 
    an Expression object.
    EXAMPLE: "R1*(C1+C2)+R2" -> "R1*[EXPR_OBJECT]+R2" 

    - Round brackets used for functions: the content is isolated in a 
    Macro object, a sort of super-'Expression' embedding 1 or more expressions
    with a top-level function applied to the result.
    Having more than 1 expression is used for functions with multiple arguments
    (1 expression for each argument)
    EXAMPLE: "R1C1*exp(-t)" -> "R1C1*[MACRO_OBJECT: 'exp']"
    """

    nTokens = len(self.tokens)

    if (nTokens == 0) :
      pass

    elif (nTokens == 1) :
      if self.tokens[0].type in ("BRKT_OPEN", "BRKT_CLOSE", "FUNCTION") :
        if not(self.QUIET_MODE) :
          print("[WARNING] Expression.nest(): odd input")
      else :
        pass
    
    else :
      a = utils.consumeAtomic(self.tokens)


    buffer = self.tokens.copy()
    output = []

    while (len(buffer) > 0) :
      nTokens = len(buffer)
      
      if (nTokens >= 2) :
        (T, tail) = (buffer[0], buffer[1:])
        
        # (Macro)Leaves/infix are simply pushed to the stack.
        if (T.type in ["CONSTANT", "VAR", "NUMBER", "INFIX", "MACRO"]) :
          output.append(T)
          buffer = tail
        
        # A function creates a Macro expression and requires another call to <_buildStack> on its argument(s).
        elif (T.type == "FUNCTION") :
          #M = macroleaf.Macroleaf(function = T.name, tokenList = tailNoParenthesis)
          M = macro.Macro(buffer)

          self.stack.append(M)
          buffer = M.remainder

        # A "(" creates a Macroleaf and requires another call to <_buildStack>.
        elif (T.type == "BRKT_OPEN") :
          #M = macroleaf.Macroleaf(function = "id", tokenList = tail)
          M = macro.Macro(buffer)
          
          self.stack.append(M)
          buffer = M.remainder
          
        # A "," occurs when <_buildStack> is called from a Macroleaf.
        # It stops the binarisation.
        # The Macroleaf must now process the next argument.
        elif (T.type == "COMMA") :
          self.remainder = tail
          return True

        # A ")" stops the binarisation.
        # The Macroleaf is now complete. 
        elif (T.type == "BRKT_CLOSE") :
          self.remainder = tail
          return True
        
        # Anything else is invalid.
        else :
          if not(self.QUIET_MODE) :
            print(f"[ERROR] Unexpected token: {T}")
          return False



      elif (nTokens == 1) :
        T = buffer[0]; buffer = []

        if (T.type in ["CONSTANT", "VAR", "NUMBER", "MACRO"]) :
          self.stack.append(T)
          self.remainder = []
          return True
        
        elif (T.type == "BRKT_CLOSE") :
          self.remainder = []
          return True

        elif (T.type == "COMMA") :
          if not(self.QUIET_MODE) :
            print("[ERROR] A list of tokens cannot end with a comma.")
          self.remainder = [T]
          return False

        elif (T.type == "INFIX") :
          if not(self.QUIET_MODE) :
            print(f"[ERROR] A list of tokens cannot end with an infix operator (here: '{T.name}')")
          self.remainder = [T]
          return False

        else :
          if not(self.QUIET_MODE) :
            print(f"[ERROR] Unexpected token: {T}")
          self.remainder = [T]
          return False

      
      # nTokens = 0
      else :
        self.remainder = []
        return True



  # ---------------------------------------------------------------------------
  # METHOD: Expression._nestBalanceMinus()                            [PRIVATE]
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
  # METHOD: Expression._nestExplicitZeros()                           [PRIVATE]
  # ---------------------------------------------------------------------------
  def _nestExplicitZeros(self) :
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
          # print("[DEBUG] Binary._explicitZeros(): added an implicit zero.")

    # STEP 2: detect the pattern recursively in the macroleaves
    # for node in self.stack :
    #   if (node.type == "MACRO") :
    #     node._explicitZeros()

    # return None



  # ---------------------------------------------------------------------------
  # METHOD: Expression._nestMinusAsOpp()                              [PRIVATE]
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






# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...\n")

  assert(Expression("oni_giri*cos(2x+pi"  , quiet=True)._validCharCheck() == True)
  assert(Expression("input Str"           , quiet=True)._validCharCheck() == True)
  assert(Expression("input Str2.1(a+b)|x|", quiet=True)._validCharCheck() == False)
  assert(Expression("$inputStr"           , quiet=True)._validCharCheck() == False)
  assert(Expression("µinputStr"           , quiet=True)._validCharCheck() == False)
  assert(Expression("in#putStr"           , quiet=True)._validCharCheck() == False)
  assert(Expression("inputStr%"           , quiet=True)._validCharCheck() == False)
  assert(Expression("inpuétStr"           , quiet=True)._validCharCheck() == False)
  assert(Expression("inpuàtStr"           , quiet=True)._validCharCheck() == False)
  print("- Unit test passed: 'Expression._sanityCheck()'")

  assert(Expression("oni_giri*cos(2x+pi"      , quiet=True)._bracketBalanceCheck() == True)
  assert(Expression("oni_giri*cos(2x+pi("     , quiet=True)._bracketBalanceCheck() == True)
  assert(Expression("oni_giri*cos(2x+pi()))"  , quiet=True)._bracketBalanceCheck() == False)
  assert(Expression("|3x+6|.2x"               , quiet=True)._bracketBalanceCheck() == True)
  print("- Unit test passed: 'Expression._bracketBalanceCheck()'")

  assert(Expression("sin(2..1x)"        , quiet=True)._firstOrderCheck() == False)
  assert(Expression("1+Q(2,)"           , quiet=True)._firstOrderCheck() == False)
  assert(Expression("cos(3x+1)*Q(2,,1)" , quiet=True)._firstOrderCheck() == False)
  print("- Unit test passed: 'Expression._firstOrderCheck()'")

  # TODO: unit tests for the tokeniser
  # ...




  e = Expression("1+2*pi*R1C1cos(x/7.1//y*Z+sin(exp(-9t)))", verbose = True)
  e.syntaxCheck()
  e.tokenise()
  e.nest()

  print("[INFO] End of unit tests.")
