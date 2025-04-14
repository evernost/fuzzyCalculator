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



# -----------------------------------------------------------------------------
# FUNCTION: pop(string)
# -----------------------------------------------------------------------------
def pop(inputStr) :
  """
  Returns a tuple containing the first character of 'inputStr' and its tail.
  
  EXAMPLES
  - pop("abcde") = ("a", "bcde")
  - pop("a") = ("a", "")
  - pop("") = ("", "")
  """

  if not inputStr :
    return ("", "")
  elif (len(inputStr) == 1) :
    return (inputStr, "")
  else :
    return (inputStr[0], inputStr[1:])



# -----------------------------------------------------------------------------
# FUNCTION: split(string)
# -----------------------------------------------------------------------------
def split(inputStr, n) :
  """
  Splits the string 'inputStr' in two at the breakpoint index 'n'.
  Indexing is 0-based.

  EXAMPLES
  > split("blob", -1) = ("", "blob")
  > split("blob",  0) = ("", "blob")
  > split("blob",  1) = ("b", "lob")
  
  See unit tests in 'main()'
  """  
  
  # Input guard
  assert isinstance(inputStr, str), "First argument in 'split' must be a string."
  assert isinstance(n, int), "Second argument in 'split' must be an integer."
  
  if not(inputStr) :
    return ("", "")
  elif (n > len(inputStr)) :
    return (inputStr, "")
  elif (n <= 0) :
    return ("", inputStr)
  else :
    return(inputStr[0:n], inputStr[n:])



# -----------------------------------------------------------------------------
# FUNCTION: isAlpha(string)
# -----------------------------------------------------------------------------
def isAlpha(inputStr) :
  """
  Returns True if the first char of 'inputStr' is a letter.
  Capitalisation is ignored.
  """

  char = inputStr[0]

  testAlpha = False
  testAlpha = testAlpha or ((ord(char) >= ord("A")) and (ord(char) <= ord("Z")))
  testAlpha = testAlpha or ((ord(char) >= ord("a")) and (ord(char) <= ord("z")))

  return testAlpha



# -----------------------------------------------------------------------------
# FUNCTION: isDigit(string)
# -----------------------------------------------------------------------------
def isDigit(inputStr) :
  """
  Returns True if the first char of 'inputStr' is a digit.
  """

  char = inputStr[0]

  return (ord(char) >= ord("0")) and (ord(char) <= ord("9"))



# -----------------------------------------------------------------------------
# FUNCTION: isNumber(string)
# -----------------------------------------------------------------------------
def isNumber(inputStr) :
  """
  Tests if the input is the string representation of a number (whole or fractional).
  
  The test fails if the string contains anything else than digits and more than
  one dot. 

  The test fails on a single dot "."
  The test fails on negative numbers (the minus sign is treated differently)

  EXAMPLES
  (See unit tests)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "'isNumber' expects a string as an input."

  gotDigit = False

  # Detect invalid inputs
  if (inputStr in ["", "."]) :
    return False

  for char in inputStr :
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
# FUNCTION: splitSpace(string)
# -----------------------------------------------------------------------------
def splitSpace(inputStr) :
  """
  Separates the leading whitespaces from the rest of the string.

  Returns a couple (w, rem) such that inputStr = w + rem 
  with "w" being made of whitespaces only.
  
  EXAMPLES
  (See unit tests in <main>)
  """

  # Input guard
  assert isinstance(inputStr, str), "'splitSpace' expects a string as an input."

  for n in range(len(inputStr)) :
    if (inputStr[n] != " ") :
      return split(inputStr, n)



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











# -----------------------------------------------------------------------------
# FUNCTION: isLegalVariableName(string)
# -----------------------------------------------------------------------------
def isLegalVariableName(inputStr) :
  """
  Test if the input string is a valid variable name.
  
  This test only checks the syntax. It does not indicate if this variable
  has been declared.

  EXAMPLES
  (See unit tests)
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
# FUNCTION: showInStr(string)
# -----------------------------------------------------------------------------
def showInStr(inputStr, loc) :
  """
  Prints 'inputStr' with a "^" char right below the a location
  defined by <loc>.
  It helps to point out a specific char in the string.

  <loc> shall point using a 0-indexing convention.
  """
  
  print(inputStr)  
  if ((loc >= 0) and (loc < len(inputStr))) :
    s = [" "] * len(inputStr)
    s[loc] = "^"
    print("".join(s))



# -----------------------------------------------------------------------------
# Main (unit tests)
# -----------------------------------------------------------------------------
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")
  print()

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
  print("- Passed: <isNumber>")

  assert(split("onigiri", -1) == ("", "onigiri"))
  assert(split("onigiri",  0) == ("", "onigiri"))
  assert(split("onigiri",  1) == ("o", "nigiri"))
  assert(split("onigiri",  2) == ("on", "igiri"))
  assert(split("onigiri",  5) == ("onigi", "ri"))
  assert(split("onigiri",  7) == ("onigiri", ""))
  assert(split("onigiri",  8) == ("onigiri", ""))
  assert(split("onigiri", 15) == ("onigiri", ""))
  print("- Passed: <split>")
  
  assert(splitSpace("pi") == ("", "pi"))
  assert(splitSpace(" pi") == (" ", "pi"))
  assert(splitSpace("   pi") == ("   ", "pi"))
  print("- Passed: <splitSpace>")
  
  assert(isLegalVariableName("x") == True)
  assert(isLegalVariableName("xyz") == True)
  assert(isLegalVariableName("1.2") == False)
  assert(isLegalVariableName("314") == False)
  assert(isLegalVariableName("314_x") == False)
  assert(isLegalVariableName("a_b_c_d_") == True)
  assert(isLegalVariableName("exp") == False)
  assert(isLegalVariableName("_u") == True)
  assert(isLegalVariableName("_sin") == True)
  print("- Passed: <isLegalVariableName>")
