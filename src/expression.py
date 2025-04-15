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
  def __init__(self, input) :
    self.input = input
    
    # Completed after calling "tokenize"
    self.tokens = []
    
    # Completed after calling "binarize"
    self.binary = None
    
    # Completed after calling "detectVar"
    self.vars = []

    # Options
    self.VERBOSE_MODE = False
    self.DEBUG_MODE = False
    


  # ---------------------------------------------------------------------------
  # METHOD: Expression.check()
  # ---------------------------------------------------------------------------
  def check(self) :
    """
    Runs some tests to make sure the expression is valid for parsing.
    """
    
    if not(self._validCharCheck()) :
      print("[ERROR] Parser error: input contains invalid chars.")
      exit()
      
    if not(self._bracketBalanceCheck()) :
      print("[ERROR] Parser error: invalid bracket balance.")
      exit()
      
    if not(self._firstOrderCheck()) :
      print("[ERROR] Parser halted due to an error in the first order check.")
      exit()



  # ---------------------------------------------------------------------------
  # METHOD: Expression._validCharCheck()
  # ---------------------------------------------------------------------------
  def _validCharCheck(self) :
    """
    Checks the input string and makes sure it contains valid characters only.
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
  # METHOD: Expression._bracketBalanceCheck()
  # ---------------------------------------------------------------------------
  def _bracketBalanceCheck(self) :
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



  # -----------------------------------------------------------------------------
  # METHOD: Expression._firstOrderCheck()
  # -----------------------------------------------------------------------------
  def _firstOrderCheck(self) :
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
          print("[ERROR] A valid expression cannot have 2 consecutive dots. Is it a typo?")
        return False
        
      elif ((char1, char2) == (",", ",")) :
        if self.VERBOSE_MODE :
          utils.showInStr(self.input, i+1)
          print("[ERROR] A valid expression cannot have 2 consecutive commas. Is it a typo?")
        return False

      elif ((char1, char2) == (",", ")")) :
        if self.VERBOSE_MODE :     
          utils.showInStr(self.input, i+1)
          print("[ERROR] Possible missing argument?")
        return False

      # 
      # TODO: this section needs to be completed.
      # 

      else :
        pass

    return True



  # ---------------------------------------------------------------------------
  # FUNCTION: tokenise(string)
  # ---------------------------------------------------------------------------
  def tokenise(self) :
    """
    Generates a list of tokens from the input.

    The input characters are read, grouped and classified to an abstract type
    (Token objects) while preserving their information.
    
    This function assumes that syntax checks have been run prior to the call.
    Otherwise, some syntax errors will not be caught.
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
      # TODO: check if there can be conflicts.
      (number, tailNumber)      = utils.consumeNumber(inputStr)
      (constant, tailConstant)  = utils.consumeConst(inputStr)
      (function, tailFunction)  = utils.consumeFunc(inputStr)
      (variable, tailVariable)  = utils.consumeVar(inputStr)
      (infix, tailInfix)        = utils.consumeInfix(inputStr)

      if (number != "") :
        self.tokens.append(symbols.Token(number))
        inputStr = tailNumber

      elif (constant != "") :
        self.tokens.append(symbols.Token(constant))
        inputStr = tailConstant
      
      elif (function != "") :
        self.tokens.append(symbols.Token(function))
        self.tokens.append(symbols.Token("("))
        inputStr = tailFunction

      elif (variable != "") :
        self.tokens.append(symbols.Token(variable))
        inputStr = tailVariable
        
      elif (infix != "") :
        self.tokens.append(symbols.Token(infix))
        inputStr = tailInfix
      
      # Otherwise: detect brackets and commas
      else :
        (head, tail) = utils.pop(inputStr)

        if (head == "(") :
          self.tokens.append(symbols.Token(head))
          inputStr = tail

        elif (head == ")") :
          self.tokens.append(symbols.Token(head))
          inputStr = tail

        elif (head == ",") :
          self.tokens.append(symbols.Token(head))
          inputStr = tail
          
        else :
          print("[ERROR] Internal error: the input char could not be assigned to any Token.")
          exit()


