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
import src.binary as binary
import src.symbols as symbols
import src.utils as utils



# =============================================================================
# Class definition
# =============================================================================
class Expression : 
  
  # ---------------------------------------------------------------------------
  # METHOD: Expression.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, input, verbose = False, debug = False) :
    self.input = input
    
    # Populated after calling "tokenise()"
    self.tokens = []
    
    # Populated after calling "binarise()"
    self.binary = None
    
    # Populated after calling "detectVar()"
    self.vars = []

    # Options
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
      print("[ERROR] Expression check: input contains invalid chars.")
      status = False
      
    if not(self._bracketBalanceCheck()) :
      print("[ERROR] Expression check: invalid bracket balance.")
      status = False
      
    if not(self._firstOrderCheck()) :
      print("[ERROR] Expression check: invalid character sequence.")
      status = False

    if self.VERBOSE_MODE :
      if status :
        print("[INFO] Syntax check: success")
      else :
        print("[ERROR] Syntax check: failed")

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
        if self.VERBOSE_MODE :
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
        if self.VERBOSE_MODE :
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
        if self.VERBOSE_MODE :
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: a valid expression cannot have 2 consecutive dots. Is it a typo?")
        return False
        
      elif ((char1, char2) == (",", ",")) :
        if self.VERBOSE_MODE :
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: a valid expression cannot have 2 consecutive commas. Is it a typo?")
        return False

      elif ((char1, char2) == (",", ")")) :
        if self.VERBOSE_MODE :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: possible missing argument?")
        return False
      
      elif ((char1, char2) == (",", "+")) :
        if self.VERBOSE_MODE :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: '+' cannot follow ','. Please refer to the parsing rules.")
        return False
      
      # TODO: same holds for any infix operator the user might have declared

      elif ((char1, char2) == ("(", ")")) :
        if self.VERBOSE_MODE :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: content between parethesis cannot be left empty.")
        return False
      
      elif ((char1, char2) == ("(", "+")) :
        if self.VERBOSE_MODE :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Syntax: '+' cannot follow '('. Please refer to the parsing rules.")
        return False
      
      elif ((char1, char2) == ("+", ",")) :
        if self.VERBOSE_MODE :     
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

    Internally, tokenise runs in 2 steps:
    - create tokens for each block encountered
    - explicit the hidden multiplication tokens
    
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
          print(f"[ERROR] Internal error: the input char '{head}' could not be assigned to any Token.")
          status = False


    # Explicit the hidden multiplications
    self._tokeniseExplicitMult()

    if self.VERBOSE_MODE :
      if status :
        print("[INFO] Tokenise: success")
      else :
        print("[ERROR] Tokenise: failed")

    return status



  # ---------------------------------------------------------------------------
  # METHOD: Expression._tokeniseExplicitMult()                        [PRIVATE]
  # ---------------------------------------------------------------------------
  def _tokeniseExplicitMult(self) :
    """
    Detects and expands implicit multiplications in a list of tokens.
    Updates the internal list of tokens with the multiplication tokens 
    explicited at the right place.

    This function is usually called from Expression.tokenise()
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



# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")

  assert(Expression("oni_giri*cos(2x+pi")._validCharCheck() == True)
  assert(Expression("input Str")._validCharCheck() == True)
  assert(Expression("input Str2.1(a+b)|x|")._validCharCheck() == False)
  assert(Expression("$inputStr")._validCharCheck() == False)
  assert(Expression("µinputStr")._validCharCheck() == False)
  assert(Expression("in#putStr")._validCharCheck() == False)
  assert(Expression("inputStr%")._validCharCheck() == False)
  assert(Expression("inpuétStr")._validCharCheck() == False)
  assert(Expression("inpuàtStr")._validCharCheck() == False)
  print("- Unit test passed: 'Expression._sanityCheck()'")

  assert(Expression("oni_giri*cos(2x+pi")._bracketBalanceCheck() == True)
  assert(Expression("oni_giri*cos(2x+pi(")._bracketBalanceCheck() == True)
  assert(Expression("oni_giri*cos(2x+pi()))")._bracketBalanceCheck() == False)
  assert(Expression("|3x+6|.2x")._bracketBalanceCheck() == True)
  print("- Unit test passed: 'Expression._bracketBalanceCheck()'")

  assert(Expression("sin(2..1x)")._firstOrderCheck() == False)
  assert(Expression("1+Q(2,)")._firstOrderCheck() == False)
  assert(Expression("cos(3x+1)*Q(2,,1)")._firstOrderCheck() == False)
  print("- Unit test passed: 'Expression._firstOrderCheck()'")

  # TODO: unit tests for the tokeniser




  print("[INFO] End of unit tests.")
