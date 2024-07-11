# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : utils
# File name       : utils.py
# File type       : Python script (Python 3.10 or higher)
# Purpose         : 
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# All the utilitary functions that haven't enough fame yet to get their 
# own library :(
# 
# Note: when called as a 'main', it runs the unit tests on the functions.


# =============================================================================
# External libs
# =============================================================================
import symbol



# -----------------------------------------------------------------------------
# FUNCTION: pop
# -----------------------------------------------------------------------------
def pop(inputStr) :
  """
  DESCRIPTION
  Return a tuple containing the first character of <inputStr> and its tail.

  Known limitations: 
  None.
  
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
# FUNCTION: pop
# -----------------------------------------------------------------------------
def split(inputStr, n) :
  """
  DESCRIPTION
  Split a string <inputStr> in two at the breakpoint index <n>.

  Known limitations:
  None.

  EXAMPLES
  > split("pouet",-1)   = ("", "pouet")
  > split("pouet",0)    = ("", "pouet")
  > split("pouet",1)    = ("p", "ouet")
  > split("pouet",2)    = ("po", "uet")
  > split("pouet",5)    = ("pouet", "")
  > split("pouet",6)    = ("pouet", "")
  > split("pouet",100)  = ("pouet", "")
  """  
  
  # Input guard
  assert isinstance(inputStr, str), "<split> first argument must be a string."
  assert isinstance(n, int), "<split> second argument must be an integer."
  
  if not(inputStr) :
    return ("", "")
  elif (n > len(inputStr)) :
    return (inputStr, "")
  elif (n <= 0) :
    return ("", inputStr)
  else :
    return(inputStr[0:n], inputStr[n:])



# -----------------------------------------------------------------------------
# FUNCTION: isAlpha
# -----------------------------------------------------------------------------
def isAlpha(inputStr) :
  """
  DESCRIPTION
  Returns True if the first char of inputStr is a letter.
  Capitalisation is ignored.
  """
  char = inputStr[0]

  testAlpha = False
  testAlpha = testAlpha or ((ord(char) >= ord("A")) and (ord(char) <= ord("Z")))
  testAlpha = testAlpha or ((ord(char) >= ord("a")) and (ord(char) <= ord("z")))

  return testAlpha



# -----------------------------------------------------------------------------
# FUNCTION: isAlpha
# -----------------------------------------------------------------------------
def isDigit(inputStr) :
  """
  DESCRIPTION
  Returns True if the first char of inputStr is a digit.
  """
  char = inputStr[0]

  return (ord(char) >= ord("0")) and (ord(char) <= ord("9"))



# -----------------------------------------------------------------------------
# FUNCTION: isBlank
# -----------------------------------------------------------------------------
def isBlank(inputStr) :
  """
  DESCRIPTION
  Returns True if the input string only contains whitespaces.
  """
  print("TODO")



# -----------------------------------------------------------------------------
# FUNCTION: isNumber
# -----------------------------------------------------------------------------
def isNumber(inputStr) :
  """
  DESCRIPTION
  Test if the input is the string representation of a digit or a number (whole or fractional).
  
  The test fails if the string contains anything else than digits and more than
  one dot. 

  The test fails on a single dot.
  The test fails on negative numbers (the minus sign is treated differently)

  EXAMPLES
  (See unit tests)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<isNumber> expects a string as an input."

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
# FUNCTION: isLegalVariableName
# -----------------------------------------------------------------------------
def isLegalVariableName(inputStr) :
  """
  DESCRIPTION
  Test if the input string is a valid variable name.
  
  This test only checks the syntax. It does not indicate if this variable
  has been declared.

  EXAMPLES
  (See unit tests)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<isLegalVariableName> expects a string as an input."

  # Filter out reserved names
  if (inputStr in ([x["name"] for x in symbol.CONSTANTS] + [x["name"] for x in symbol.FUNCTIONS])) :
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



def showInStr(inputStr, loc) :
  """
  DESCRIPTION
  Prints <inputStr> with a "^" char right below the a location
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
  
  print("[INFO] Standalone call: running unit tests...")

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

  assert(checkVariableSyntax("x") == True)
  assert(checkVariableSyntax("xyz") == True)
  assert(checkVariableSyntax("1.2") == False)
  assert(checkVariableSyntax("314") == False)
  assert(checkVariableSyntax("314_x") == False)
  assert(checkVariableSyntax("a_b_c_d_") == True)
  assert(checkVariableSyntax("exp") == False)
  assert(checkVariableSyntax("_u") == True)
  assert(checkVariableSyntax("_sin") == True)
