# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : utils
# File name       : utils.py
# File type       : Python script (Python 3.10 or higher)
# Purpose         : 
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# All the utilitary functions that haven't enough fame yet to get their 
# own library :(
# 
# Run is as a 'main()' to call the unit tests.


# =============================================================================
# External libs
# =============================================================================
import src.symbols as symbols

from enum import Enum



# -----------------------------------------------------------------------------
# FUNCTION: pop()
# -----------------------------------------------------------------------------
def pop(s: str) :
  """
  Returns a 2-elements tuple containing the first character of 's' and its tail.
  
  EXAMPLES
  - pop("abcde") = ("a", "bcde")
  - pop("a") = ("a", "")
  - pop("") = ("", "")

  See unit tests in 'main()' for more examples.
  """

  # 0-length string
  if not s :
    return ("", "")
  
  # 1-length string
  elif (len(s) == 1) :
    return (s, "")
  
  # Any length > 1
  else :
    return (s[0], s[1:])



# -----------------------------------------------------------------------------
# FUNCTION: split()
# -----------------------------------------------------------------------------
def split(s: str, n: int) :
  """
  Splits the string 's' in two at the breakpoint index 'n'.
  Indexing is 0-based.

  EXAMPLES
  > split("blob", -1) = ("", "blob")
  > split("blob",  0) = ("", "blob")
  > split("blob",  1) = ("b", "lob")
  > split("blob",  2) = ("bl", "ob")
  
  See unit tests in 'main()' for more examples.
  """  
  
  # Input guard
  assert isinstance(s, str), "First argument in 'split' must be a string."
  assert isinstance(n, int), "Second argument in 'split' must be an integer."
  
  if not(s) :
    return ("", "")
  elif (n > len(s)) :
    return (s, "")
  elif (n <= 0) :
    return ("", s)
  else :
    return(s[0:n], s[n:])



# -----------------------------------------------------------------------------
# FUNCTION: isAlpha()
# -----------------------------------------------------------------------------
def isAlpha(s: str) -> bool :
  """
  Returns True if the first char of 's' is a letter.
  Capitalisation is ignored.
  """

  # Keep the first char, ignore the rest.
  char = s[0]

  testAlpha = False
  testAlpha = testAlpha or ((ord(char) >= ord("A")) and (ord(char) <= ord("Z")))
  testAlpha = testAlpha or ((ord(char) >= ord("a")) and (ord(char) <= ord("z")))

  return testAlpha



# -----------------------------------------------------------------------------
# FUNCTION: isDigit()
# -----------------------------------------------------------------------------
def isDigit(s: str) -> bool :
  """
  Returns True if the first char of 's' is a digit.
  """

  # Keep the first char, ignore the rest.
  char = s[0]

  return (ord(char) >= ord("0")) and (ord(char) <= ord("9"))



# -----------------------------------------------------------------------------
# FUNCTION: isNumber()
# -----------------------------------------------------------------------------
def isNumber(s: str) -> bool :
  """
  Tests if the input is the string representation of a number (integer or fractional).
  
  The test fails if the input:
  - contains anything else than digits
  - contains more than one dot 

  Special cases:
  - the test fails on a single dot: s = '.'
  - the test fails on any input with a negative sign '-'

  EXAMPLES
  > isNumber("23") = True
  > isNumber("4.5") = True
  > isNumber(".1") = True
  > isNumber("-1") = False

  See unit tests in 'main()' for more examples.
  """
  
  # Input guard
  assert isinstance(s, str), "'isNumber' expects a string as an input."

  gotDigit = False

  # Detect invalid inputs
  if (s in ["", "."]) :
    return False

  for char in s :
    if (char == ".") :
      if gotDigit :
        return False
      
      else :
        gotDigit = True
    
    # Anything else than a dot or a digit is invalid
    elif not(isDigit(char)) :
      return False
  
  # If we made it up to here, it's a valid number.
  return True



# -----------------------------------------------------------------------------
# FUNCTION: splitSpace()
# -----------------------------------------------------------------------------
def splitSpace(s: str) :
  """
  Separates the leading whitespaces from the rest of the string.

  Returns a couple (s_w, s_rem) such that s = s_w + s_rem 
  with 's_w' being made of whitespaces only.
  
  EXAMPLES
  > splitSpace("blah") = ("", "blah")
  > splitSpace("   123") = ("   ", "123")
  > splitSpace("") = ("", "")
  > splitSpace("  ") = ("  ", "")
  
  
  See unit tests in 'main()'.
  """

  # Input guard
  assert isinstance(s, str), "'splitSpace' expects a string as an input."

  # Empty input
  if (len(s) == 0) :
    return ("", "")
  
  nMax = len(s)
  for n in range(1, len(s)+1) :
    (head, _) = split(s, n)
    if (head[-1] != " ") :
      nMax = n-1
      break
  
  return split(s, nMax)



# -----------------------------------------------------------------------------
# FUNCTION: consumeConst()
# -----------------------------------------------------------------------------
def consumeConst(s: str) :
  """
  Consumes any leading constant name in a string.

  If 's' is a string starting with the name of a constant, the tuple (s_c, s_rem) is 
  returned, where:
  - 's_c' is the matching constant name
  - 's_rem' is the rest of the string.
  
  and such that s = s_c + s_rem.

  If 's' does not start with a known constant or the constant is embedded 
  in a larger name, the tuple ("", s) is returned.
  Refer to rules [5.X] in parsingRules.md for more details about the parsing strategy.

  The function tries to match with the constants listed in 'symbols.CONSTANTS'.

  EXAMPLES
  See unit tests in 'main()'.
  """

  # Input guard
  assert isinstance(s, str), "'consumeConst' expects a string as an input."

  constList = [c["name"] for c in symbols.CONSTANTS]

  for n in range(1, len(s)+1) :
    (head, tail) = split(s, n)
    if (head in constList) :
      
      # Case 1: the entire string matches with a known constant
      if (n == len(s)) :
        return (head, "")
      
      # Case 2: the beginning matches, but something comes next
      else :
        nextChar = tail[0]
        
        # See [R5.10]: underscore forbids to treat as a constant
        if (nextChar == "_") :
          return ("", s)
        
        # From that point: the only way to match is to have a bigger
        # constant name, whose beginning matched with a known constant (see [R5.12])
        # Can't conclude.
        elif isAlpha(nextChar) :  
          pass

        else :
          return (head, tail)

  # Case 3: never matched
  return ("", s)



# -----------------------------------------------------------------------------
# FUNCTION: consumeNumber()
# -----------------------------------------------------------------------------
def consumeNumber(s: str) :
  """
  Consumes any leading number in a string.

  If 's' is a string starting with a number, the tuple (s_n, s_rem) is 
  returned, where:
  - 's_n' is the matching number
  - 's_rem' is the remainder of the string.
  
  and such that s = s_n + s_rem.

  The function does a "greedy" read: as many chars as possible are stacked
  to the output 's_n' as long as it makes sense as a number.

  The function accepts fractional numbers ("3.14", "0.2", etc.)
  Omitted/extra leading zeros are accepted: ".1", ".0001", "00000.01" etc.

  The function does not accept negative numbers.
  If 's' does not start with a digit or a dot, the tuple ("", s) is returned.

  NOTE
  - the number is returned "as is" without interpretation. 
  Inputs like "0.500000", "4." or "0.0" will not be simplified.
  - integer or fractionnal part can be omitted: "12.", ".34" etc.
  - a single dot is not considered as a number: consumeNumber(".") = ("", ".")
  - minus sign "-" is not accepted
  - scientific notation will be supported in a later version
  - 's_n' always passes the 'isNumber()' test

  EXAMPLES
  > consumeNumber("42abc") = ("42", "abc")
  > consumeNumber("4.2def") = ("4.2", "def")
  > consumeNumber("4.2.") = ("4.2", ".")
  > consumeNumber("4.2cos(3x)") = ("4.2", "cos(3x)")
  > consumeNumber("-3.14") = ("", "-3.14")

  See unit tests in 'main()' for more examples.
  """

  # Input guard
  assert isinstance(s, str), "'consumeNumber' expects a string as an input."
 
  # Test the first character.
  # A valid number can only start with a digit or a "."
  if not(s[0].isdigit() or (s[0] == ".")) :
    return ("", s)

  # Start from the first character and consume the remaining chars as long as it makes sense as a number.
  # The longest string that passes the "isNumber" test becomes the candidate.
  nMax = 0
  for n in range(1, len(s)+1) :
    (head, _) = split(s, n)
    if isNumber(head) :
      nMax = n

    else :
      break
  
  return split(s, nMax)



# -----------------------------------------------------------------------------
# FUNCTION: consumeFunc()
# -----------------------------------------------------------------------------
def consumeFunc(s: str) :
  """
  Consumes any leading function name in a string.

  If 's' is a string starting with a function, the tuple (s_f, s_rem) is 
  returned, where:
  - 's_f' is the matching function name
  - 's_rem' is the remainder of the string.
  
  The opening parenthesis is omitted in 's_rem', such that s = s_f + '(' + s_rem.

  If 's' does not start with a known function, the tuple ("", s) is 
  returned.

  The list of available functions is fetched from 'symbols.FUNCTIONS'.

  NOTE
  - The opening parenthesis is mandatory (rule [R3])
  - Opening parenthesis is omitted because later in the parsing engine, a function 
  or a single "(" triggers the same processing. 

  EXAMPLES
  > consumeFunc("sin") = ("", "sin")
  > consumeFunc("sina") = ("", "sina")
  > consumeFunc("sinc(3x+12)") = ("sinc", "3x+12)")
  > consumeFunc("tan (x-pi)") = ("tan", "x-pi)")
  
  See unit tests in 'main()' for more examples.
  """
  
  funcList = [f["name"] for f in symbols.FUNCTIONS]

  RET_NO_MATCH = ("", s)

  nMax = 0
  for n in range(1, len(s)+1) :
    (head, tail) = split(s, n)
    if (head in funcList) :
      nMax = n
  
  # No function matched
  if (nMax == 0) :
    return RET_NO_MATCH
    
  # Extract the match, analyse the remainder
  (headMax, tailMax) = split(s, nMax)
  (_, tail) = splitSpace(tailMax)

  # The remainder has no information (spaces eventually)
  # In particular, no parenthesis: reject the match.
  if (len(tail) == 0) :
    return RET_NO_MATCH   
  
  # The remainder has meaningful characters
  if (tail[0] == "(") :
      return (headMax, tail[1:])
  else :
    return RET_NO_MATCH



# ---------------------------------------------------------------------------
# FUNCTION: consumeVar()
# ---------------------------------------------------------------------------
def consumeVar(s: str) :
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
  assert isinstance(s, str), "'consumeVar' expects a string as an input."

  OUTPUT_FAILURE = ("", s)
  reservedNames = [x["name"] for x in symbols.CONSTANTS] + [x["name"] for x in symbols.FUNCTIONS]

  class fsmState(Enum) :
    INIT = 0
    UNDERSCORE_FIRST = 1
    PROC = 2
    PROC_NUM = 3
  
  if (s == "") :
    return ("", s)

  state = fsmState.INIT
  stateNext = fsmState.INIT
  splitPoint = 0; splitPointBeforeNum = 0

  for (n, c) in enumerate(s) :
    lastChar = (n == (len(s)-1))
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
        if isAlpha(c) :
          splitPoint = splitPointCurr
        
        elif isDigit(c) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK01, '{s}': a number cannot be a variable.")
          return ("", s)
        
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK02, '{s}': '{c}' cannot be a variable.")
          return ("", s)
      
      else :      
        if isAlpha(c) :
          splitPoint = splitPointCurr
          stateNext = fsmState.PROC
        
        elif isDigit(c) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK03, '{s}': a variable cannot start with a number.")
          return ("", s)

        elif (c == "_") :
          splitPoint = splitPointCurr
          stateNext = fsmState.UNDERSCORE_FIRST
      
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK04: a variable cannot start with '{c}'.")
          return ("", s)

    # -----------------------------------------------------------------------
    # State: FSM_UNDERSCORE_FIRST
    # -----------------------------------------------------------------------
    elif (state == fsmState.UNDERSCORE_FIRST) :
      if lastChar :
        if (isDigit(c) or (c == "_")) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK05, '{s}': a variable cannot be purely made of a combination of underscores and digits.")
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



# -----------------------------------------------------------------------------
# FUNCTION: isLegalVariableName()
# -----------------------------------------------------------------------------
def isLegalVariableName(inputStr) :
  """
  Test if the input string is a valid variable name.
  
  This test only checks the syntax. It does not indicate if this variable
  has been declared.

  EXAMPLES
  TODO
  """
  
  # Input guard
  assert isinstance(inputStr, str), "'isLegalVariableName' expects a string as an input."

  # Filter out reserved names
  if (inputStr in ([x["name"] for x in symbols.CONSTANTS] + [x["name"] for x in symbols.FUNCTIONS])) :
    return False

  # First character must start with a letter or an underscore (rule [R2])
  if not(isAlpha(inputStr[0]) or inputStr[0] == "_") :
    return False

  # Look for forbidden characters:
  for char in inputStr :
    testAlpha = isAlpha(char)
    testDigit = isDigit(char)
    testUnder = (char == "_")
    if not(testAlpha or testDigit or testUnder) :
      return False

  return True



# -----------------------------------------------------------------------------
# FUNCTION: showInStr()
# -----------------------------------------------------------------------------
def showInStr(inputStr, loc) :
  """
  Prints 'inputStr' with a "^" char right below the a location
  defined by <loc>.
  It helps to point out a specific char in the string.

  'loc' shall point using a 0-indexing convention.

  TODO: support for multiple loc (tuples) to point more than one char.
  """
  
  print(inputStr)  
  if ((loc >= 0) and (loc < len(inputStr))) :
    s = [" "] * len(inputStr)
    s[loc] = "^"
    print("".join(s))



# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")

  assert(isNumber("") == False)
  assert(isNumber("1") == True)
  assert(isNumber("23") == True)
  assert(isNumber("4.5") == True)
  assert(isNumber("6.0") == True)
  assert(isNumber("789.000000000") == True)
  assert(isNumber(".123456") == True)
  assert(isNumber(".1") == True)
  assert(isNumber("4.2.") == False)
  assert(isNumber(" 12") == False)
  assert(isNumber("2 ") == False)
  assert(isNumber("120 302") == False)
  assert(isNumber(".0") == True)
  assert(isNumber(".") == False)
  assert(isNumber("-") == False)
  assert(isNumber("-1") == False)
  assert(isNumber("-0") == False)
  assert(isNumber("-.") == False)
  assert(isNumber("-.0") == False)
  assert(isNumber("1-") == False)
  print("- Unit test passed: 'utils.isNumber()'")

  assert(split("onigiri", -1) == ("", "onigiri"))
  assert(split("onigiri",  0) == ("", "onigiri"))
  assert(split("onigiri",  1) == ("o", "nigiri"))
  assert(split("onigiri",  2) == ("on", "igiri"))
  assert(split("onigiri",  5) == ("onigi", "ri"))
  assert(split("onigiri",  7) == ("onigiri", ""))
  assert(split("onigiri",  8) == ("onigiri", ""))
  assert(split("onigiri", 15) == ("onigiri", ""))
  print("- Unit test passed: 'utils.split()'")
  
  assert(splitSpace("pi") == ("", "pi"))
  assert(splitSpace(" pi") == (" ", "pi"))
  assert(splitSpace("   pi") == ("   ", "pi"))
  assert(splitSpace("   test123   ") == ("   ", "test123   "))
  assert(splitSpace(" *test123  ") == (" ", "*test123  "))
  assert(splitSpace("  ") == ("  ", ""))
  assert(splitSpace("") == ("", ""))
  print("- Unit test passed: 'utils.splitSpace()'")
  
  assert(consumeConst("pi") == ("pi", ""))
  assert(consumeConst("inf") == ("inf", ""))
  assert(consumeConst(" pi") == ("", " pi"))
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
  print("- Unit test passed: 'utils.consumeConst()'")

  assert(consumeNumber("42") == ("42", ""))
  assert(consumeNumber("4.2") == ("4.2", ""))
  assert(consumeNumber("4.2.") == ("4.2", "."))
  assert(consumeNumber(" 42") == ("", " 42"))
  assert(consumeNumber("_1") == ("", "_1"))
  assert(consumeNumber("_") == ("", "_"))
  assert(consumeNumber("x") == ("", "x"))
  assert(consumeNumber(".") == ("", "."))
  assert(consumeNumber("-.") == ("", "-."))
  assert(consumeNumber("-12a") == ("", "-12a"))
  assert(consumeNumber("-33.1") == ("", "-33.1"))
  assert(consumeNumber("3.14cos(x)") == ("3.14", "cos(x)"))
  assert(consumeNumber("6.280 sin(y") == ("6.280", " sin(y"))
  assert(consumeNumber(" 64") == ("", " 64"))
  assert(consumeNumber("x86") == ("", "x86"))
  assert(consumeNumber("3_x") == ("3", "_x"))     # Rule R5.4
  assert(consumeNumber("00.1") == ("00.1", ""))
  assert(consumeNumber("02.11235sin(3x)") == ("02.11235", "sin(3x)"))
  print("- Unit test passed: 'utils.consumeNumber()'")

  assert(consumeFunc("sin") == ("", "sin"))
  assert(consumeFunc("sina") == ("", "sina"))
  assert(consumeFunc("sin(") == ("sin", ""))
  assert(consumeFunc("si(") == ("si", ""))
  assert(consumeFunc("sin  (") == ("sin", ""))
  assert(consumeFunc("si  ") == ("", "si  "))
  assert(consumeFunc("sinc(3x+12)") == ("sinc", "3x+12)"))
  assert(consumeFunc("tan (x-pi)") == ("tan", "x-pi)"))
  assert(consumeFunc("floot(-2.4)") == ("", "floot(-2.4)"))
  assert(consumeFunc("floor(-2.4)") == ("floor", "-2.4)"))
  assert(consumeFunc("q(2.4, 0.1)") == ("", "q(2.4, 0.1)"))
  assert(consumeFunc("Q(2.4, 0.1)") == ("Q", "2.4, 0.1)"))
  assert(consumeFunc("logN (12, 2)") == ("logN", "12, 2)"))
  print("- Unit test passed: 'utils.consumeFunc()'")

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
  assert(consumeVar("R1//R2") == ("R1", "//R2"))
  
  # The following should work, but doesn't. Needs a fix.
  #assert(consumeVar("R1exp(-t/4)") == ("R1", "exp(-t/4)"))       # FAILS
  #assert(consumeVar("R1.4exp(-t/4)") == ("R", "1.4exp(-t/4)"))   # FAILS
  #assert(consumeVar("var5_3cos(x)") == ("var5_3", "cos(x)"))     # FAILS
  #assert(consumeVar("x3y") == ("x3", "y"))                       # FAILS
  print("- Self-test passed: 'consumeVar'")

  assert(consumeInfix("*3x") == ("*", "3x"))
  assert(consumeInfix("**2+1") == ("*", "*2+1"))
  assert(consumeInfix("//2+1") == ("//", "2+1"))
  assert(consumeInfix("x-y") == ("", "x-y"))
  assert(consumeInfix("-2x+y") == ("-", "2x+y"))
  assert(consumeInfix("^-3") == ("^", "-3"))
  print("- Self-test passed: 'consumeInfix'")

  assert(isLegalVariableName("x") == True)
  assert(isLegalVariableName("xyz") == True)
  assert(isLegalVariableName("1.2") == False)
  assert(isLegalVariableName("314") == False)
  assert(isLegalVariableName("314_x") == False)
  assert(isLegalVariableName("a_b_c_d_") == True)
  assert(isLegalVariableName("exp") == False)
  assert(isLegalVariableName("_u") == True)
  assert(isLegalVariableName("_sin") == True)
  print("- Unit test passed: 'utils.isLegalVariableName()'")
