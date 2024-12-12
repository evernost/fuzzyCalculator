# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : qParser
# File name       : qParser.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : built-in parser for the Fuzzy Calculator
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : Saturday, 1 June 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Parser/evaluator for math expression.
#  
# It supports "natural" inputs (e.g. implicit multiplications) and lazy 
# parenthesis.
# Expressions like "(a+b)(c-d)" or "sin(x+cos(y" are valid.
#
# It is based on native Python and does not require any specific library:
# - no regex
# - no complex string manipulation
# 
# However, if transcription to another programming language is needed, 
# the following features would be nice to have:
# - OOP 
# - string to float conversion
# - the math functions you want to support (sin, cos, exp, etc.)
# - random number generation for the Monte-Carlo analysis
# - some plotting features
#
# The calculator provides the most common math operators ('+', '-', '*', '/', '^') 
# and some obscure ones ('//' for parallel resistor association)
# Usual math functions are included (sin, cos, log, exp, abs, ...) 
#
# The parser preserves the order of the input while evaluating, therefore 
# it does not assume commutativity of infix like '+', '*' etc. 
# This could allow to extend the parser to other types, like matrices.
#
# When called as a 'main', the library runs unit tests on the built-in
# parsing functions.
#
#
#
# The following gives the parsing strategy and lists all rules that apply 
# when evaluating an expression.
# 
# -------------
# PARSING RULES
# -------------
# [R1] CASE SENSITIVE
# Parser is case sensitive.
#
# [R2] CONSTANT/VARIABLE/FUNCTION NAME PREFIXING
# The name of a function/variable/constant cannot start with a number.
# It would be impossible to tell if it's a variable or an implicit
# product between a number and a variable.
#
# [R3] FUNCTION CALL SYNTAX
# No space is accepted between the function name and the parenthesis.
# It makes the parsing trickier, and there is no added value.
# "exp(-2t)" -> OK
# "cos (3x)" -> rejected
#
# [R4] VOID ARGUMENTS
# Function cannot be called with empty arguments.
#
# [R5] IMPLICIT MULTIPLICATION RULES
# The following priorities have been defined based on what feels 
# the most "natural" interpretation. 
# In case of ambiguity, a warning is raised.
# [R5.1] "pixel"      -> var("pixel")             The variable as a whole is more likely than a product of smaller variables/const.
#                                                 Why not even "p*i*x*e*l", "pi*x*e*l", "p*ixel", etc.
#
# Rules for prefixing digit/number:
# [R5.2]  "1X"        -> 1*var("X")               A variable cannot start with a digit (rule R2)
# [R5.3]  "1_X"       -> 1*var("_X")              Same as R5.2
# [R5.4]  "1.0X"      -> 1.0*var("X")             Same as R5.2
# [R5.5]  "1.0_X"     -> 1.0*var("_X")            Same as R5.2
#
# Rules for suffixing digit/number:
# [R5.6]  "X2"        -> var("X2")                Typical case of variable suffixing.
# [R5.7]  "X_2"       -> var("X_2")               Same as R5.6
# [R5.8]  "X2.0       -> var("X")*2.0             | A decimal number interrupts the variable parsing.
#                                                 | A bit odd, but it is probably the most plausible meaning.
#                                                 | Raises a warning.
# [R5.9]  "X_2.0      -> var("X_")*2.0            Same as R5.8
#
# Rules for suffixing digit/number (continued):
# [R5.10] "X3Y"       -> var("X3")*var("Y")       | If a variable contains a number, its name can only end with a digit.
#         "R10C2"     -> var("R10")*var("C2")     |
#         "C1cos("    -> var("C1")*cos(...        |
#         "X2cos+3"   -> syntax error!            "cos" is not called according to the rules for functions (R3)
# [R5.11] "X_3Y"      -> var("X_3")*var("Y")      | Same principle as [R5.10]
#         "v_21cos("  -> var("v_21")*cos(...      |
#         "X_2cos("   -> var("X_2")*cos(...       |
# [R5.12] "X2.0cos("  -> var("X")*2.0*cos(...     Consistent with R5.8
# [R5.13] "X_2.0cos(" -> var("X_")*2.0*cos(...    Consistent with R5.9
# [R5.14] "R1_Y*pi"   -> var("R1_Y")*pi           | An underscore allows more complex variable names, even after a digit.
#         "x_1_2_Y*4" -> var("x_1_2_Y")*4         | 
# [R5.15] "X_3.0_Y"    -> var("X_")*3.0*var("_Y") Raises a warning


# Consequences:
# "X_3.1Y" -> var("X_")*3.1"*var("Y")           Consequence of rule R5.9

# Behaviour not decided yet:
# [R5.__] "pi4X"   -> const("pi")*4*var("X")     ??
# [R5.__] "pi4.0X" -> const("pi")*4.0*var("X")   ??
# [R5.__] "pi_5"   -> var("pi_5")                Underscore serves as disembiguation/indexing and overrides the constant

# [R5.__] "pipi"   -> var("pipi")                If "pi*pi" was meant, maybe the user should make an effort here.
# [R5.__] "inf"    -> const("inf")               Parser tries to see as a whole in priority (so not "i*nf", "i" being a constant too)
#                                                See also [R5.10]
# [R5.__] "ipi"    -> var("ipi")                 Same as [R5.13]
#
# [R6] INFIX OPERATOR NAME
# The super common ones (+, -, /, *, ...) along with exotic ones ('//') are already included.
#
# Users are free to customise with their favorite infix if they really want to, 
# but some restrictions apply:
# - infix ops cannot be made of letters, digits, commas, dots: this would mess with the rest of the parsing.
#   Special characters are recommended: @, !, \, $, #, ...
#   Special characters can even be combined: '@*', '+!', ...
# - the special character(s) for your custom infix need to be added to the 'white list' in <sanityCheck>
# - the expected behaviour for this new infix operator needs to be defined.
#
# Infix operators that are not based on special characters will not be supported.
# There are no plans to accept inputs like 'x DONG y' or 'a SUPER+ b'.
# Reasons for that:
# - ruins the readability
# - special characters already give enough flexibility
# - exotic infix operators are not that common. It is not worth the engineering.
# - infix operators are 2 variables functions in disguise.
#   Multiargs functions are already supported and should be the reasonable choice here.
#
# Also, be careful when defining the priority of your new operator (see rules [R7.X] and [R11])
#
# [R7] OMITTED TOKEN RULES
# The infix operator "-" (minus sign) is the only operator that allows an implicit left operand.
# In other words, expressions like "(-3x+..." are accepted.
#
# There are not many cases where the implicit left operand is common and/or makes sense.
# It is mostly used:
# - to negate a number/constant/variable (rule [R7.1]) 
# - for negative exponents               (rule [R7.2])
#
# Based on that, the parser's strategy is the following:
# - "(-3*..."  -> add a leading 0: "(0-3*..."
# - "10^-4..." -> create a macroleaf with the 'opp' function: "10^M..."
#   with M : {f = opp, M = [Num:'4']}.
#   This should not have side effect with the rest of the expression
#   since '^' has the highest priority.
#   Keep that in mind when you define custom infix.
#
# When the '-' appears at the beginning of an expression or subexpression
# (like in a macroleaf) then rule [R7.1] applies.
#
# Otherwise, rule [R7.2] is applied.
# 
# [R7.2] is derived as rule [R7.3] when the infix is not '^' anymore. 
# Behaviour is the same but a warning is raised because the priority between 
# operations becomes ambiguous and the expression does not look 'natural'.
# Use of parenthesis is strongly recommended for both clarity and correctness.
#
# Examples: 
# - "(-5..." is valid                     (rule [7.1])
# - "...^-5" is valid (e.g. for '10^-4')  (rule [7.2])
# - "a^-3u" is be treated as "(a^(-3))*u" (rule [7.2])
#
# The following will raise a warning:
# - "...--4..." becomes "...-M..." with M = {f = opp, M = [Num:'4']}   (rule [7.3])
# - "...*-pi..." becomes "...*M..." with M = {f = opp, M = [Cst:'pi']} (rule [7.3])
#
# [R7.4] "(+4" is not accepted (implicit left operand is for minus sign only)
# [R7.5] "-*4" is not accepted
#
# Note: rule [7.1] only adds a zero and does not add parenthesis.
# This prevents "-x^2" to be turned into "(-x)^2", which is probably
# never what is really meant.
#
# [R8] VARIABLE NAMING
# Variable cannot start with a number.
#
# [R9] WHITE SPACES
# White spaces are not part of the syntax and are simply ignored.
#
# [R10] OPERATORS ASSOCIATIVITY
# Consecutive operators with identical priority are all treated 
# with increasing nesting level (i.e. the 'rightest the deepest'):
# - a+b+c+d -> a+(b+(c+d))
# - a/b/c   -> a/(b/c)
# - a//b//c -> a//(b//c)      (note: '//' is associative, parenthesis do not matter)
# - a^b^c^d -> a^(b^(c^d))    (people will complain anyway, no matter what convention is chosen)
# In doubt: check the output interpretation, add parenthesis.
#
# [R11] OPERATORS PRECEDENCE
# It is not recommended to change the relative priorities of the basic infix
# operators: '+', '-', '*' , '/', '^'.
# - as far as I know, there is no real need for that
# - side effect will emerge due to the parsing strategy 
#   (e.g. rule [R7.2]: '^' is assumed to have the highest precedence for proper operation)
#
# Also, be careful when defining priority of custom infix: think twice about 
# how it interacts with other infix.
# Again, in doubt: use parenthesis and don't blindly rely on precedence. Parenthesis are free!
#
# Priority level is limited to 100 (arbitrary limit)
#



# =============================================================================
# External libs
# =============================================================================
from src.commons import *

import src.binary as binary
import src.symbols as symbols
import src.utils as utils

from enum import Enum
import numpy as np



# =============================================================================
# Constants pool
# =============================================================================
VERBOSE_MODE = True
DEBUG_MODE = False



# =============================================================================
# Main code
# =============================================================================

# -----------------------------------------------------------------------------
# FUNCTION: sanityCheck(string)
# -----------------------------------------------------------------------------
def sanityCheck(inputStr) :
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

  # List the individual characters the infix are made of
  infixListExp = []
  for t in symbols.INFIX :
    infixListExp += list(t["name"])
  
  for (loc, char) in enumerate(inputStr) :
    alphaTest   = utils.isAlpha(char)
    digitTest   = utils.isDigit(char)
    infixTest   = (char in infixListExp)
    othersTest  = (char in [" ", ".", ",", "_", "(", ")"])
    
    if not(alphaTest or digitTest or infixTest or othersTest) :
      if VERBOSE_MODE :
        utils.showInStr(inputStr, loc)
        print("[ERROR] This character is not supported by the parser.")
      return False

  return True



# -----------------------------------------------------------------------------
# FUNCTION: bracketBalanceCheck(string)
# -----------------------------------------------------------------------------
def bracketBalanceCheck(inputStr) :
  """
  Checks if the parentheses in the input expression are valid.
  This function allows "lazy parenthesis": matching closing parenthesis 
  are not required.

  Returns True if the check passed, False otherwise.

  EXAMPLES
  (See unit tests in "main")
  """

  level = 0
  for (loc, char) in enumerate(inputStr) :
    if (char == "(") :
      level += 1
    elif (char == ")") :
      level -= 1

    if (level < 0) :
      if VERBOSE_MODE :
        utils.showInStr(inputStr, loc)
        print("[ERROR] Closing parenthesis in excess.")
      return False

  return True



# -----------------------------------------------------------------------------
# FUNCTION: firstOrderCheck(string)
# -----------------------------------------------------------------------------
def firstOrderCheck(inputStr) :
  """
  Takes the chars 2 by 2 and detects any invalid combination.
  Detailed list of the valid/invalid combinations can be found in 
  "resources/firstOrderCheck.xslx"
  
  Returns True if the check passed, False otherwise.

  EXAMPLES
  (See unit tests in "main")
  """

  for i in (range(len(inputStr)-1)) :
    
    char1 = inputStr[i]; char2 = inputStr[i+1]

    if ((char1, char2) == (".", ".")) :
      if VERBOSE_MODE :
        utils.showInStr(inputStr, i+1)
        print("[ERROR] A valid expression cannot have 2 consecutive dots. Is it a typo?")
      return False
      
    elif ((char1, char2) == (",", ",")) :
      if VERBOSE_MODE :
        utils.showInStr(inputStr, i+1)
        print("[ERROR] A valid expression cannot have 2 consecutive commas. Is it a typo?")
      return False

    elif ((char1, char2) == (",", ")")) :
      if VERBOSE_MODE :     
        utils.showInStr(inputStr, i+1)
        print("[ERROR] Possible missing argument?")
      return False

    # 
    # TODO: this section needs to be completed.
    # 

    else :
      pass

  return True



# -----------------------------------------------------------------------------
# FUNCTION: reservedWordsCheck(string)
# -----------------------------------------------------------------------------
def reservedWordsCheck(inputStr) :
  """
  Checks if reserved words (like function names, constants) are used incorrectly.
  
  EXAMPLES
  (See unit tests in "main")
  """
  
  # Input guard
  assert isinstance(inputStr, str), "'reservedWordsCheck' expects a string as an input."

  print("TODO")
  return True



# -----------------------------------------------------------------------------
# FUNCTION: consumeConst(string)
# -----------------------------------------------------------------------------
def consumeConst(inputStr) :
  """
  Consumes the leading constant in a string.

  If 'inputStr' is a string starting with the name of a constant, the tuple (c, rem) is 
  returned, where:
  - 'c' is the matching constant name
  - 'rem' is the rest of the string.
  
  so that inputStr = c + rem.

  If 'inputStr' does not start with a known constant or the constant is embedded 
  in a larger name, the tuple ("", inputStr) is returned.
  Refer to rules [5.X] for more details about the parsing strategy.

  The list of available constants is fetched from 'symbols.CONSTANTS'.

  EXAMPLES
  (See unit tests in "main")
  """

  # Input guard
  assert isinstance(inputStr, str), "'consumeConst' expects a string as an input."

  constList = [c["name"] for c in symbols.CONSTANTS]

  for n in range(1, len(inputStr)+1) :
    (head, tail) = utils.split(inputStr, n)
    if (head in constList) :
      
      # Case 1: the whole string matches with a known constant
      if (n == len(inputStr)) :
        return (head, "")
      
      # Case 2: there is a match, but something comes after
      else :
        nextChar = tail[0]
        
        # See [R5.10]: underscore forbids to treat as a constant
        if (nextChar == "_") :
          return ("", inputStr)
        
        # From that point: the only way to match is to have a bigger
        # constant name, whose beginning matched with a known constant (see [R5.12])
        # Can't conclude.
        elif utils.isAlpha(nextChar) :  
          pass

        else :
          return (head, tail)

  # Case 3: never matched
  return ("", inputStr)



# -----------------------------------------------------------------------------
# FUNCTION: consumeNumber(string)
# -----------------------------------------------------------------------------
def consumeNumber(inputStr) :
  """
  Consumes the leading number in a string.

  If "input" is a string starting with a number, the tuple (n, rem) is 
  returned, where:
  - "n" is the matching number
  - "rem" is the rest of the string.
  
  so that input = n + rem

  The function does a 'greedy' read: as many chars as possible are stacked
  to the output "n" as long as it makes sense as a number.

  The function accepts fractional numbers ("3.14", "0.2", etc.)
  Omitted leading zero is accepted: ".1", ".0001" etc.

  The function does not accept negative numbers.
  If "input" does not start with a digit or a dot, the tuple ("", inputStr) is returned.

  NOTES
  - the number is returned "as is" without interpretation. 
  Inputs like "0.500000", "4." or "0.0" will not be simplified.
  - integer or fractionnal part can be omitted: "12.", ".34" etc.
  - a single dot is not considered as a number: consumeNumber(".") = ("", ".")
  - minus sign "-" is not accepted
  - scientific notation will be supported in a later version.

  EXAMPLES
  > consumeNumber("42") = ("42", "")
  > consumeNumber("4.2") = ("4.2", "")
  > consumeNumber("4.2.") = ("4.2", ".")
  > consumeNumber("4.2cos(3x)") = ("4.2", "cos(3x)")
  > consumeNumber("-3.14") = ("", "-3.14")
  (See unit tests in "main" for more)
  """

  # Input guard
  assert isinstance(inputStr, str), "'consumeNumber' expects a string as an input."
 
  # Test the first character.
  # A valid number can only start with a digit or a "."
  if not(inputStr[0].isdigit() or (inputStr[0] == ".")) :
    return ("", inputStr)

  # Start from the first character and consume the remaining chars as long as it makes sense as a number.
  # The longest string that passes the "isNumber" test becomes the candidate.
  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = utils.split(inputStr, n)
    if utils.isNumber(head) :
      nMax = n

    else:
      break
  
  return utils.split(inputStr, nMax)



# -----------------------------------------------------------------------------
# FUNCTION: consumeFunc(string)
# -----------------------------------------------------------------------------
def consumeFunc(inputStr) :
  """
  Consumes the leading function name in a string.

  If 'inputStr' is a string starting with a function, the tuple (f, rem) is 
  returned, where:
  - 'f' is the matching function name
  - 'rem' is the rest of the string.
  
  The opening parenthesis is omitted in 'rem', so inputStr = f + '(' + rem

  If "inputStr" does not start with a known function, the tuple ("", inputStr) is 
  returned.

  The list of available functions is fetched from 'symbols.FUNCTIONS'.

  Notes:
  - The function name must be immediatly followed by an opening parenthesis "(".
  There is not point in accepting things like "cos (3x+1)" or "cos ax+1".
  It does not bring anything to the user experience, makes the expression
  harder to read and leads to ambiguity (rule [R3])
  - Opening parenthesis is omitted because later in the parsing engine, a function 
  or a single "(" triggers the same processing. 

  EXAMPLES
  > consumeFunc("sina") = ("", "sina")
  > consumeFunc("sinc(3x+12)") = ("sinc", "3x+12)")
  > consumeFunc("tan (x-pi)") = ("", "tan (x-pi)")
  (See unit tests in "main" for more)
  """
  
  functionsExt = [(f["name"] + "(") for f in symbols.FUNCTIONS]

  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = utils.split(inputStr, n)
    if (head in functionsExt) :
      nMax = n
  
  # Return the function without opening bracket 
  (tmpHead, tmpTail) = utils.split(inputStr, nMax)
  return (tmpHead[0:-1], tmpTail)



# ---------------------------------------------------------------------------
# FUNCTION: consumeVar(string)
# ---------------------------------------------------------------------------
def consumeVar(inputStr) :
  """
  Consumes the leading variable name in a string.
  
  The parsing does not rely on prior variable declaration.
  It only detects and returns a name that is a legal variable name and hence 
  could be a variable.

  If "inputStr" is a string starting with a variable, the tuple (v, rem) is 
  returned, where:
  - "v" is a legal variable name
  - "rem" is the rest of the string.
  
  so that inputStr = v + rem

  Several rules apply to the parsing strategy. 
  In short, the function tries to match the head of the input with what could be
  a plausible variable name based on the rest of the input string.
  
  The function filters out variables when their name matches with a function or a constant.
  In that case, the tuple ("", input) is returned.

  This function is usually followed by a call to "addVariable", that adds 
  the variable found by "consumeVar" to the list of variables ("variables" attribute).

  The function itself does not alter the content of "variables".
  So it can be safely used to test whether an unknown string starts with a potential variable.
  
  Refer to rules [5.X] for more details about the parsing strategy. 

  NOTES
  Future releases might affect this function so that it takes into account the variables 
  that have been declared for the detection.
  This could give some more flexibility in the syntax (especially on rule [5.9])

  EXAMPLES
  (See unit tests in "main" for more)
  """

  # Input guard
  assert isinstance(inputStr, str), "'consumeVar' expects a string as an input."

  OUTPUT_FAILURE = ("", inputStr)
  reservedNames = [x["name"] for x in symbols.CONSTANTS] + [x["name"] for x in symbols.FUNCTIONS]

  class fsmState(Enum) :
    INIT = 0
    UNDERSCORE_FIRST = 1
    PROC = 2
    PROC_NUM = 3
  
  if (inputStr == "") :
    return ("", inputStr)

  state = fsmState.INIT
  stateNext = fsmState.INIT
  splitPoint = 0; splitPointBeforeNum = 0

  for (n, c) in enumerate(inputStr) :
    lastChar = (n == (len(inputStr)-1))
    splitPointCurr = n+1
    
    # Note:
    # Using "splitPointCurr" is defined such that using it as split point i.e. in:
    # > utils.split(inputStr, splitPointCurr)
    # would include the current character "c".
    
    # -----------------------------------------------------------------------
    # State: INIT
    # -----------------------------------------------------------------------
    if (state == fsmState.INIT) :
      if lastChar :
        if utils.isAlpha(c) :
          splitPoint = splitPointCurr
        
        elif utils.isDigit(c) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK01, '{inputStr}': a number cannot be a variable.")
          return ("", inputStr)
        
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK02, '{inputStr}': '{c}' cannot be a variable.")
          return ("", inputStr)
      
      else :      
        if utils.isAlpha(c) :
          splitPoint = splitPointCurr
          stateNext = fsmState.PROC
        
        elif utils.isDigit(c) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK03, '{inputStr}': a variable cannot start with a number.")
          return ("", inputStr)

        elif (c == "_") :
          splitPoint = splitPointCurr
          stateNext = fsmState.UNDERSCORE_FIRST
      
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK04: a variable cannot start with '{c}'.")
          return ("", inputStr)

    # -----------------------------------------------------------------------
    # State: FSM_UNDERSCORE_FIRST
    # -----------------------------------------------------------------------
    elif (state == fsmState.UNDERSCORE_FIRST) :
      if lastChar :
        if (utils.isDigit(c) or (c == "_")) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK05, '{inputStr}': a variable cannot be purely made of a combination of underscores and digits.")
          return ("", inputStr)
        
        elif utils.isAlpha(c) :
          splitPoint = splitPointCurr
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK06, '{inputStr}': the character '{c}' interrupts the parsing of a variable.")
          return ("", inputStr)
      
      else :
        if (utils.isDigit(c) or (c == "_")) :
          splitPoint = splitPointCurr
        
        elif utils.isAlpha(c) :
          splitPoint = splitPointCurr
          stateNext = fsmState.PROC
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK07, '{inputStr}': the character '{c}' interrupts the parsing of a variable.")
          return ("", inputStr)
          
    # -----------------------------------------------------------------------
    # State: FSM_PROC
    # -----------------------------------------------------------------------
    elif (state == fsmState.PROC) :
      if lastChar :
        if (utils.isAlpha(c) or utils.isDigit(c) or (c == "_")) :
          splitPoint = splitPointCurr
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK08, '{inputStr}': the character '{c}' interrupts the parsing of a variable.")
      
      else :        
        if (utils.isAlpha(c) or (c == "_")) :
          splitPoint = splitPointCurr

        elif utils.isDigit(c) :
          splitPointBeforeNum = splitPointCurr-1
          stateNext = fsmState.PROC_NUM
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK09, '{inputStr}': the character '{c}' interrupts the parsing of a variable.")
          break
        
    # -----------------------------------------------------------------------
    # State: FSM_PROC_NUM
    # -----------------------------------------------------------------------
    elif (state == fsmState.PROC_NUM) :
      if lastChar :
        if (utils.isAlpha(c) or utils.isDigit(c) or (c == "_")) :
          splitPoint = splitPointCurr
          
        elif (c == ".") :
          splitPoint = splitPointBeforeNum
          if DEBUG_MODE :
            print(f"[DEBUG] BRK10, '{inputStr}': a decimal number interrupts the parsing of a variable.")
          
        else :
          splitPoint = splitPointCurr-1
          if DEBUG_MODE :
            print(f"[DEBUG] BRK11, '{inputStr}': the character '{c}' interrupts the parsing of a variable.")
      
      else :
        if utils.isDigit(c) :
          pass
        
        elif (c == ".") :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK12, '{inputStr}': a decimal number interrupts the parsing of a variable.")
          splitPoint = splitPointBeforeNum
          break
        
        elif (utils.isAlpha(c) or (c == "_")) :
          splitPoint = splitPointCurr
          stateNext = fsmState.PROC
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK13, '{inputStr}': the character '{c}' interrupts the parsing of a variable.")
          splitPoint = splitPointCurr-1
          break

    # Update FSM
    state = stateNext

  (candidate, _) = utils.split(inputStr, splitPoint)

  if candidate in reservedNames :
    return ("", inputStr)
  
  else: 
    return utils.split(inputStr, splitPoint)



# ---------------------------------------------------------------------------
# FUNCTION: consumeInfix(string)
# ---------------------------------------------------------------------------
def consumeInfix(inputStr) :
  """
  Consumes the leading infix operator in a string.

  If 'inputStr' is a string starting with an infix operator, the tuple (op, rem) is 
  returned, where:
  - 'op' is the matching infix operator name
  - 'rem' is the rest of the string.
  
  so that inputStr = op + rem

  If 'inputStr' does not start with a known infix operator, the tuple 
  ("", inputStr) is returned instead.

  The list of available infix operators is fetched from 'symbols.INFIX'

  The list of infix operators can be extended with custom operators.
  Please refer to [R6] to see the rules that apply for that.

  EXAMPLES
  (See unit tests in "main")
  """

  # Input guard
  assert isinstance(inputStr, str), "'consumeInfix' expects a string as an input."

  infixList = [op["name"] for op in symbols.INFIX]

  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = utils.split(inputStr, n)
    
    # Returns True only if the whole word matches
    if (head in infixList) :
      nMax = n
  
  return utils.split(inputStr, nMax)



# ---------------------------------------------------------------------------
# FUNCTION: tokenise(string)
# ---------------------------------------------------------------------------
def tokenise(inputStr) :
  """
  Generates a list of Token objects from a string containing a valid expression.

  The input characters are read, grouped and classified to an abstract type
  (Token objects) while preserving their information.
  
  This function assumes that syntax checks have been run prior to the call.
  Otherwise, some syntax errors will not be caught.

  EXAMPLES
  todo
  """

  tokenList = []

  while(len(inputStr) > 0) :

    # White spaces do not contribute to the parsing (rule [R9])
    (_, inputStr) = utils.splitSpace(inputStr)
    
    if (len(inputStr) == 0) :
      break

    # Try to interpret the leading characters as a 
    # number, constant, variable, function or infix.
    # TODO: check if there can be conflicts.
    (number, tailNumber)      = consumeNumber(inputStr)
    (constant, tailConstant)  = consumeConst(inputStr)
    (function, tailFunction)  = consumeFunc(inputStr)
    (variable, tailVariable)  = consumeVar(inputStr)
    (infix, tailInfix)        = consumeInfix(inputStr)

    if (number != "") :
      tokenList.append(symbols.Token(number))
      inputStr = tailNumber

    elif (constant != "") :
      tokenList.append(symbols.Token(constant))
      inputStr = tailConstant
    
    elif (function != "") :
      tokenList.append(symbols.Token(function))
      tokenList.append(symbols.Token("("))
      inputStr = tailFunction

    elif (variable != "") :
      print(f"[DEBUG] Found variable: '{variable}'")
      tokenList.append(symbols.Token(variable))
      inputStr = tailVariable
      
    elif (infix != "") :
      tokenList.append(symbols.Token(infix))
      inputStr = tailInfix
    
    # Otherwise: detect brackets and commas
    else :
      (head, tail) = utils.pop(inputStr)

      if (head == "(") :
        tokenList.append(symbols.Token(head))
        inputStr = tail

      elif (head == ")") :
        tokenList.append(symbols.Token(head))
        inputStr = tail

      elif (head == ",") :
        tokenList.append(symbols.Token(head))
        inputStr = tail
        
      else :
        print("[ERROR] Internal error: the input char could not be assigned to any Token.")
        exit()

  return tokenList



# -----------------------------------------------------------------------------
# FUNCTION: secondOrderCheck(tokenList)
# -----------------------------------------------------------------------------
def secondOrderCheck(tokenList) :
  """
  DESCRIPTION
  Takes the tokens 2 by 2 from the list of Tokens and detects any invalid combination.
  Detailed list can be found in "resources/secondOrderCheck.xslx"
  
  It is a complement to "firstOrderCheck".
  Some checks are easier to do on the list of tokens rather than the raw input expression.
  
  EXAMPLES
  todo
  """

  nTokens = len(tokenList)

  for i in range(nTokens-1) :
    
    T1 = tokenList[i]; T2 = tokenList[i+1]

    if (T1.type == "FUNCTION") :
      if not(T2.type == "BRKT_OPEN") :
        print(f"[ERROR] A function must be followed with a parenthesis (Rule R3).")
        return CHECK_FAILED      
      else :
        pass
    
    
    # 
    # TODO: this section needs to be completed.
    # 


  T = tokenList[nTokens-1]
  if (T.type == "FUNCTION") :
    print(f"[ERROR] An expression cannot end with a function.")
    return CHECK_FAILED

  elif (T.type == "BRKT_OPEN") :
    print(f"[ERROR] An expression cannot end with an opening parenthesis.")
    return CHECK_FAILED
  
  elif (T.type == "INFIX") :
    print(f"[ERROR] An expression cannot end with an infix operator.")
    return CHECK_FAILED



  return CHECK_SUCCESS



# ---------------------------------------------------------------------------
# FUNCTION: explicitMult(tokenList)
# ---------------------------------------------------------------------------
def explicitMult(tokenList) :
  """
  DESCRIPTION
  Detects and expands implicit multiplications in a list of tokens.
  Returns the same list with the multiplication tokens explicited at the right place.

  EXAMPLES
  todo
  """
  
  nTokens = len(tokenList)

  # Hidden multiplication requires at least 2 tokens.
  if (nTokens <= 1) :
    return tokenList

  else :
    output = []
    for n in range(nTokens-1) :
      T1 = tokenList[n]; T2 = tokenList[n+1]

      output.append(T1)
      
      # Example: "pi(x+4)"
      if ((T1.type, T2.type) == ("CONSTANT", "BRKT_OPEN")) :
        output.append(symbols.Token("*"))

      # Example: "R1(R2+R3)"
      elif ((T1.type, T2.type) == ("VAR", "BRKT_OPEN")) :
        output.append(symbols.Token("*"))

      # Example: "x_2.1"
      elif ((T1.type, T2.type) == ("VAR", "NUMBER")) :
        output.append(symbols.Token("*"))

      # Example: "(x+1)pi"
      elif ((T1.type, T2.type) == ("BRKT_CLOSE", "CONST")) :
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
      elif ((T1.type, T2.type) == ("NUMBER", "CONST")) :
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

  return output



# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")
  print()

  # Disable the babbling mode while doing the unit tests
  VERBOSE_MODE = False

  assert(sanityCheck("oni_giri*cos(2x+pi") == True)
  assert(sanityCheck("input Str") == True)
  assert(sanityCheck("input Str2.1(a+b)|x|") == False)
  assert(sanityCheck("$inputStr") == False)
  assert(sanityCheck("µinputStr") == False)
  assert(sanityCheck("in#putStr") == False)
  assert(sanityCheck("inputStr%") == False)
  assert(sanityCheck("inpuétStr") == False)
  assert(sanityCheck("inpuàtStr") == False)
  print("- Self-test passed: 'sanityCheck'")

  assert(bracketBalanceCheck("oni_giri*cos(2x+pi") == True)
  assert(bracketBalanceCheck("oni_giri*cos(2x+pi(") == True)
  assert(bracketBalanceCheck("oni_giri*cos(2x+pi()))") == False)
  assert(bracketBalanceCheck("|3x+6|.2x") == True)
  print("- Self-test passed: 'bracketBalanceCheck'")

  assert(firstOrderCheck("sin(2..1x)") == False)
  assert(firstOrderCheck("1+Q(2,)") == False)
  assert(firstOrderCheck("cos(3x+1)*Q(2,,1)") == False)
  print("- Self-test passed: 'firstOrderCheck'")

  assert(consumeConst("pi") == ("pi", ""))
  assert(consumeConst("inf") == ("inf", ""))
  assert(consumeConst("eps*4") == ("eps", "*4"))
  assert(consumeConst("pi3") == ("pi", "3"))          # Rule R5.7
  assert(consumeConst("pi4.0X") == ("pi", "4.0X"))    # Rule R5.8
  assert(consumeConst("pi_3") == ("", "pi_3"))
  assert(consumeConst("pir") == ("", "pir"))
  assert(consumeConst("api") == ("", "api"))
  assert(consumeConst("pi*12") == ("pi", "*12"))
  assert(consumeConst("pi 12") == ("pi", " 12"))
  assert(consumeConst("pi(12+3") == ("pi", "(12+3"))
  assert(consumeConst("pir*12") == ("", "pir*12"))
  assert(consumeConst("pi*r*12") == ("pi", "*r*12"))
  assert(consumeConst("i*pi*r*12") == ("i", "*pi*r*12"))
  print("- Self-test passed: 'consumeConst'")

  assert(consumeNumber("_1") == ("", "_1"))
  assert(consumeNumber("_") == ("", "_"))
  assert(consumeNumber("x") == ("", "x"))
  assert(consumeNumber("42") == ("42", ""))
  assert(consumeNumber("4.2") == ("4.2", ""))
  assert(consumeNumber("4.2.") == ("4.2", "."))
  assert(consumeNumber(".") == ("", "."))
  assert(consumeNumber("-.") == ("", "-."))
  assert(consumeNumber("-12a") == ("", "-12a"))
  assert(consumeNumber("-33.1") == ("", "-33.1"))
  assert(consumeNumber("3.14cos(x)") == ("3.14", "cos(x)"))
  assert(consumeNumber("6.280 sin(y") == ("6.280", " sin(y"))
  assert(consumeNumber(" 64") == ("", " 64"))
  assert(consumeNumber("x86") == ("", "x86"))
  assert(consumeNumber("3_x") == ("3", "_x"))     # Rule R5.4
  print("- Self-test passed: 'consumeNumber'")

  assert(consumeFunc("sina") == ("", "sina"))
  assert(consumeFunc("sinc(3x+12)") == ("sinc", "3x+12)"))
  assert(consumeFunc("tan (x-pi)") == ("", "tan (x-pi)"))
  assert(consumeFunc("floot(-2.4)") == ("", "floot(-2.4)"))
  assert(consumeFunc("floor(-2.4)") == ("floor", "-2.4)"))
  assert(consumeFunc("q(2.4, 0.1)") == ("", "q(2.4, 0.1)"))
  assert(consumeFunc("Q(2.4, 0.1)") == ("Q", "2.4, 0.1)"))
  print("- Self-test passed: 'consumeFunc'")

  assert(consumeVar("x") == ("x", ""))
  assert(consumeVar("1") == ("", "1"))
  assert(consumeVar("_") == ("", "_"))
  assert(consumeVar(".") == ("", "."))
  assert(consumeVar("_1") == ("", "_1"))
  assert(consumeVar("_a") == ("_a", ""))
  assert(consumeVar("a_") == ("a_", ""))
  assert(consumeVar("bonjour") == ("bonjour", ""))
  assert(consumeVar("_var1") == ("_var1", ""))
  assert(consumeVar("3x") == ("", "3x"))          # Rule R5.2
  assert(consumeVar("3_x") == ("", "3_x"))        # Rule R5.3
  assert(consumeVar("3.14x") == ("", "3.14x"))    # Rule R5.4
  assert(consumeVar("3.14_x") == ("", "3.14_x"))  # Rule R5.5
  assert(consumeVar("onigiri12+4") == ("onigiri12", "+4"))          # Rule R5.6
  assert(consumeVar("onigiri_12*pi") == ("onigiri_12", "*pi"))      # Rule R5.7
  assert(consumeVar("onigiri_3.14*pi") == ("onigiri_", "3.14*pi"))  # Rule R5.8
  assert(consumeVar("x_2//4") == ("x_2", "//4"))
  assert(consumeVar("x_23//4") == ("x_23", "//4"))
  assert(consumeVar("x_123456//7") == ("x_123456", "//7"))
  assert(consumeVar("x_3.0+ 1") == ("x_", "3.0+ 1"))    # Raises a warning (this input is seriously odd)
  assert(consumeVar("x_23.0+ 1") == ("x_", "23.0+ 1"))  # Raises a warning
  assert(consumeVar("x_1.+ 1") == ("x_", "1.+ 1"))      # Raises a warning
  assert(consumeVar("x_12.*3") == ("x_", "12.*3"))      # Raises a warning
  assert(consumeVar("var5_3*3") == ("var5_3", "*3"))
  assert(consumeVar("pi*12x") == ("", "pi*12x"))
  assert(consumeVar("R1*3") == ("R1", "*3"))
  assert(consumeVar(".1") == ("", ".1"))
  assert(consumeVar("sin(2pi*x)") == ("", "sin(2pi*x)"))
  assert(consumeVar("R1_2*3") == ("R1_2", "*3"))
  assert(consumeVar("R1_2*exp(-t/4)") == ("R1_2", "*exp(-t/4)"))
  #assert(consumeVar("R1exp(-t/4)") == ("R1", "exp(-t/4)"))      # Rule R5.X
  #assert(consumeVar("R1.4exp(-t/4)") == ("R", "1.4exp(-t/4)"))
  #assert(consumeVar("var5_3cos(x)") == ("var5_3", "cos(x)"))
  #assert(consumeVar("x3y") == ("x3", "y"))              # Rule R5.6 -> "consumeVar" does not work according to R5._ and needs a fix
  print("- Self-test passed: 'consumeVar'")

  assert(consumeInfix("*3x") == ("*", "3x"))
  assert(consumeInfix("**2+1") == ("*", "*2+1"))
  assert(consumeInfix("//2+1") == ("//", "2+1"))
  assert(consumeInfix("x-y") == ("", "x-y"))
  assert(consumeInfix("-2x+y") == ("-", "2x+y"))
  assert(consumeInfix("^-3") == ("^", "-3"))
  print("- Self-test passed: 'consumeInfix'")
  
  # TODO: check some tokenisations
  tokenList = [
    "1X",
    "3.14X",
    "1_x",
    "1.0_x",
    "R1",
    "R_1",
    "R1.0",
    "R_1.0",
    "1+2*pi*R1*C1"
  ]
  print("- TODO: <tokenise>")
  
  # TODO: trigger all the error cases in "secondOrderCheck"
  # secondOrderCheck([Token("sin")])
  print("- TODO: 'secondOrderCheck'")
  
  print()
  
  # Restore the babbling mode
  VERBOSE_MODE = True

  testVect = [
    ("1-2+3-4",           1-2+3-4),
    ("-1-2-3",            -1-2-3),
    ("-1+4(2-1",          -1+4*(2-1)),
    ("-(4+1)*2-3*7",      (-(4+1)*2)-(3*7)),
    ("2^3^4",             (2**3)**4),
    ("2^-1+2",            (2**(-1))+2),
    ("1*2-3*4",           1*2-3*4),
    ("-1*2-3*4",          -1*2-3*4),
    ("(1+2)(3+4)",        (1+2)*(3+4)),
    ("(1+2)(3+4)(5-6",    (1+2)*(3+4)*(5-6)),
    ("-(1+2)(3+4)",       -(1+2)*(3+4)),
    ("12//100",           12*100/(12+100)),
    ("4.7 + 10//100",     4.7+(10*100/(10+100))),
    ("-(-3+9)/(1+2)",     -(-3+9)/(1+2)),
    ("-abs(-15*7)/5",     -105/5),
    ("sin(2*pi*0.1",      np.sin(2*np.pi*0.1)),
    ("1.0//2.5",          1.0*2.5/(1.0+2.5)),
    ("10//100+1",         ((10*100)/(10+100)) + 1),
    ("1+cos(exp(pi*3))",  1 + np.cos(np.exp(3*np.pi))),
    ("1+cos(exp(pi*3))/tan(0.1/2)",  1 + np.cos(np.exp(3*np.pi))/np.tan(0.1/2))
  ]

  for (n, vect) in enumerate(testVect) :
    
    (expr, val) = vect

    print(f"----- Test vector {n}: '{expr}' -----")

    # STEP 1: rewrite the expression as a list of tokens
    tokenList = tokenise(expr)
    
    # STEP 2: detect and add the implicit multiplication tokens
    tokenListFull = explicitMult(tokenList)
    
    # STEP 3: create a binary object from the list of tokens
    B = binary.Binary(tokenListFull)
  
    # STEP 4: group and nest operators with higher precedence
    B.nest()
    
    # STEP 6: evaluate!
    out = B.eval()

    print(f"Tokens          : {tokenList}")
    print(f"Tokens with mult: {tokenListFull}")
    print(f"Binary          : {B}")
    print(f"output          : {out}")
    print(f"expected        : {val}")
    print()


