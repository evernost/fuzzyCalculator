# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : utils
# File name       : utils.py
# File type       : Python script (Python 3.10 or higher)
# Purpose         : various parsing utilities
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
# EXTERNALS
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

  In other words, if (a,b) = split(s,n) then len(a) = n.

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

  Returns a tuple (s_w, s_rem) such that s = s_w + s_rem 
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
  - the number is returned "as is" without interpretation
    Inputs like "0.500000", "4." or "0.0" will not be simplified
    to "0.5", "4", "0" etc.
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
  
  The opening parenthesis is omitted in 's_rem', such that 
  s = s_f + "(" + s_rem.

  If 's' does not start with a known function, the tuple ("", s) is 
  returned.

  The list of functions the parser compares against is read from 
  'symbols.FUNCTIONS'.

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
def consumeVar(s: str, quiet = False, verbose = False, debug = False) :
  """
  Consumes what could be the name of a variable in the beginning of a string.
  
  If 's' is a string starting with a valid variable name, the tuple (s_v, s_rem) 
  is returned, where:
  - 's_v' is the name of the variable
  - 's_rem' is the rest of the string.
  such that s = s_v + s_rem

  It tries to extract a name that is a legal variable name.
  The parsing does not rely on prior variable declaration.

  Several rules apply to the parsing strategy. 
  - the function tries to match the head of the input with what could be
  a plausible variable name based on the rest of the input string
  - the function filters out variables whose name matches with a function or a constant.
  In that case, the tuple ("", s) is returned.
  
  Refer to rules [5.X] for more details about the parsing strategy. 

  EXAMPLES
  > consumeVar("onigiri_12*pi") -> ("onigiri_12", "*pi")
  > consumeVar("onigiri_3.14*pi") -> ("onigiri_", "3.14*pi")
  > consumeVar("logN (12, 2)") -> ("", "logN (12, 2)")
  > consumeVar("sin(") -> ("", "sin(")
  > consumeVar("R1 sin(") -> ("R1", " sin(")
  > consumeVar("tan (x+pi)") -> ("", "tan (x+pi)")
  > consumeVar("R1.4exp(-t/4)") -> ("R", "1.4exp(-t/4)")
  > consumeVar("var1var2") -> ("var1", "var2")
  > consumeVar("var1_1var2") -> ("var1_1", "var2")
  > consumeVar("R1exp(-t/4)") -> ("R1", "exp(-t/4)")
  
  See unit tests in 'main()' for more examples.
  """

  # Enables a babbling mode that describes all exit cases
  DEBUG_MODE = debug

  # Input guard
  assert isinstance(s, str), "'consumeVar' expects a string as an input."

  RET_NO_MATCH = ("", s)
    
  # Void input case
  if (s == "") :
    return RET_NO_MATCH
  
  class fsmState(Enum) :
    INIT = 0
    LETTER_BLOCK = 1
    NUM_BLOCK = 2
    UNDERSCORE_FIRST = 3
  
  state = fsmState.INIT
  stateNext = fsmState.INIT
  splitPoint = 0; splitPointBeforeNum = 0

  for (n, c) in enumerate(s) :
    isLastChar = (n == (len(s)-1))
    splitPointCurr = n+1
    
    # Note:
    # Using "splitPointCurr" is defined such that using it as split point i.e. in:
    # > utils.split(inputStr, splitPointCurr)
    # would include the current character "c".
    
    # -------------------------------------------------------------------------
    # State: INIT
    # Description: entry point of the FSM 
    # -------------------------------------------------------------------------
    if (state == fsmState.INIT) :
      if isLastChar :
        if isAlpha(c) :
          splitPoint = splitPointCurr
        
        elif isDigit(c) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK1, '{s}': a number cannot be a variable.")
          return RET_NO_MATCH
        
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK2, '{s}': '{c}' cannot be a variable.")
          return RET_NO_MATCH
      
      else :      
        if isAlpha(c) :
          splitPoint = splitPointCurr
          stateNext = fsmState.LETTER_BLOCK
        
        elif isDigit(c) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK3, '{s}': a variable cannot start with a number.")
          return RET_NO_MATCH

        elif (c == "_") :
          splitPoint = splitPointCurr
          stateNext = fsmState.UNDERSCORE_FIRST
      
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK4: a variable cannot start with '{c}'.")
          return RET_NO_MATCH
          
    # -------------------------------------------------------------------------
    # State: LETTER_BLOCK
    # Description: consumes an aggregate of letters
    # -------------------------------------------------------------------------
    elif (state == fsmState.LETTER_BLOCK) :
      if isLastChar :
        if (isAlpha(c) or isDigit(c) or (c == "_")) :
          splitPoint = splitPointCurr
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK5, '{s}': the character '{c}' interrupts the parsing of a variable.")
      
      else :        
        if (isAlpha(c) or (c == "_")) :
          splitPoint = splitPointCurr

        elif isDigit(c) :
          splitPointBeforeNum = splitPointCurr-1
          stateNext = fsmState.NUM_BLOCK
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK6, '{s}': the character '{c}' interrupts the parsing of a variable.")
          break
        
    # -------------------------------------------------------------------------
    # State: NUM_BLOCK
    # Description: consumes an aggregate of digits
    # -------------------------------------------------------------------------
    elif (state == fsmState.NUM_BLOCK) :
      if isLastChar :
        if (isDigit(c) or (c == "_")) :
          splitPoint = splitPointCurr
        
        # A block of digits suffixing a variable necessarily ends it
        elif isAlpha(c) :
          splitPoint = splitPointCurr-1

        elif (c == ".") :
          splitPoint = splitPointBeforeNum
          if not(quiet) :
            print(f"[WARNING] utils.consumeVar(): detected an odd use of decimal number for suffixing. Please check the interpretation")
            if DEBUG_MODE :
              print(f"[DEBUG] BRK7, '{s}': a decimal number interrupts the parsing of a variable.")
          
        else :
          splitPoint = splitPointCurr-1
          if DEBUG_MODE :
            print(f"[DEBUG] BRK8, '{s}': the character '{c}' interrupts the parsing of a variable.")
      
      else :
        # Another digit in a sequence of digits: keep stacking
        if isDigit(c) :
          pass
        
        # A number with a decimal point cannot be part of a variable name
        elif (c == ".") :
          if not(quiet) :
            print(f"[WARNING] utils.consumeVar(): detected an odd use of decimal number for suffixing. Please check the interpretation")
            if DEBUG_MODE :
              print(f"[DEBUG] BRK9, '{s}': a decimal number interrupts the parsing of a variable.")
          splitPoint = splitPointBeforeNum
          break
        
        # A letter after a number suffixing a variable necessarily ends that variable
        # Example: "var1var2" -> "var1"
        elif isAlpha(c) :
          splitPoint = splitPointCurr-1
          break
          
        elif (c == "_") :
          splitPoint = splitPointCurr
          stateNext = fsmState.LETTER_BLOCK

        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK10, '{s}': the character '{c}' interrupts the parsing of a variable.")
          splitPoint = splitPointCurr-1
          break

    # -------------------------------------------------------------------------
    # State: UNDERSCORE_FIRST
    # Description: special case when the expression starts with a "_"
    # -------------------------------------------------------------------------
    elif (state == fsmState.UNDERSCORE_FIRST) :
      if isLastChar :
        if (isDigit(c) or (c == "_")) :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK11, '{s}': a variable cannot be purely made of a combination of underscores and digits.")
          return RET_NO_MATCH
        
        elif isAlpha(c) :
          splitPoint = splitPointCurr
          
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK12, '{s}': the character '{c}' interrupts the parsing of a variable.")
          return RET_NO_MATCH
      
      # A sequence of "_" and digits make the FSM stay in this state.
      # The only successful way out is a letter.
      # Anything else cannot be a variable.
      else :
        if (isDigit(c) or (c == "_")) :
          splitPoint = splitPointCurr
        
        elif isAlpha(c) :
          splitPoint = splitPointCurr
          stateNext = fsmState.LETTER_BLOCK
        
        else :
          if DEBUG_MODE :
            print(f"[DEBUG] BRK13, '{s}': the character '{c}' interrupts the parsing of a variable.")
          return RET_NO_MATCH

    else :
      print("[ERROR] consumeVar: internal error. This state cannot be reached.")

    # Update FSM state
    state = stateNext

  (candidate, _) = split(s, splitPoint)

  # Exclude reserved names
  reservedNames = [x["name"] for x in symbols.CONSTANTS] + [x["name"] for x in symbols.FUNCTIONS]
  if candidate in reservedNames :
    return RET_NO_MATCH
  else : 
    return split(s, splitPoint)



# -----------------------------------------------------------------------------
# FUNCTION: consumeInfix()
# -----------------------------------------------------------------------------
def consumeInfix(s: str) :
  """
  Consumes the leading infix operator in a string.

  If 's' is a string starting with an infix operator, the tuple (s_op, s_rem) is 
  returned, where:
  - 's_op' is the matching infix operator name
  - 's_rem' is the rest of the string.
  such that s = op + rem

  If 's' does not start with a known infix operator, the tuple 
  ("", s) is returned instead.

  The list of infix operators the parser compares against is read from 
  'symbols.INFIX'.

  The list of infix operators can be extended with custom operators.
  Please refer to [R6] to see the rules that apply for that.

  EXAMPLES
  (See unit tests in "main")
  """

  # Input guard
  assert isinstance(s, str), "'consumeInfix' expects a string as an input."

  infixList = [op["name"] for op in symbols.INFIX]

  nMax = 0
  for n in range(1, len(s)+1) :
    (head, _) = split(s, n)
    
    # Returns True only if the whole word matches
    if (head in infixList) :
      nMax = n
  
  return split(s, nMax)



# -----------------------------------------------------------------------------
# FUNCTION: consumeAtomic()
# -----------------------------------------------------------------------------
def consumeAtomic(tokens) :
  """
  Consumes the tokens in a list until it hits tokens implying either 
  recursivity or a change in the processing:  
  - an opening parenthesis  (-> recursivity)
  - a function              (-> recursivity)
  - a comma                 (-> processing changes)
  - a closing parenthesis   (-> processing changes)

  If so, it stops and returns the 'atomic' part and the remainder.

  The remainder part is not analysed: if there is another function 
  call or opening parenthesis, it will remain as is in the remainder.
  Another call to consumeAtomic() is needed. 

  EXAMPLES
  > consumeAtomic(...) = ...
  
  See unit tests in 'main()' for more examples.
  """
  
  nTokens = len(tokens)

  # List of tokens is empty: nothing to do
  if (nTokens == 0) :
    return ([], [])
  
  # List of tokens has 1 element
  elif (nTokens == 1) :
    if tokens[0].type in ("BRKT_OPEN", "BRKT_CLOSE", "FUNCTION") :
      print("[WARNING] utils.consumeAtomic(): possible uncaught syntax error.")
      return ([], tokens)
    else :
      return (tokens, [])

  # List of tokens with > 1 element
  else :
    for i in range(nTokens) :
      if (tokens[i].type in ["BRKT_OPEN", "BRKT_CLOSE", "FUNCTION", "COMMA"]) :
        return (tokens[0:i], tokens[i:])

      elif (tokens[i].type in ["CONSTANT", "VARIABLE", "NUMBER", "INFIX", "MACRO"]) :
        if (i == (nTokens-1)) :
          return (tokens, [])

      else :
        print(f"[ERROR] Unexpected type of Token: {tokens[i].type}")



# -----------------------------------------------------------------------------
# FUNCTION: nest()
# -----------------------------------------------------------------------------
def nest(tokens, quiet = False, verbose = False, debug = False) :
  """
  Consumes a list of tokens, returns another list of tokens where functions and 
  round brackets are replaced with a Macro token.
  """
  
  nTokens = len(tokens)

  # The list of tokens is empty: nothing to do
  if (nTokens == 0) :
    return []

  # The list of tokens has exactly 1 element
  elif (nTokens == 1) :
    if tokens[0].type in ("BRKT_OPEN", "BRKT_CLOSE", "FUNCTION") :
      if not(quiet) : print("[WARNING] utils.nest(): odd input (single meaningless token)")
      return tokens
    else :
      return tokens
  
  # The list of tokens has 2 elements or more
  else :
    
    # Consume anything that does not require a macro
    (tokensFlat, remainder) = consumeAtomic(tokens)

    # The list of tokens is flat (no function or parenthesis)
    if not(remainder) :
      return tokens
    
    # The list of tokens contains hierarchical elements 
    else :
      
      # A function or an opening parenthesis opens a new context
      if (remainder[0].type in ("BRKT_OPEN", "FUNCTION")) :
        
        # Create a Macro object with the new context as input
        M = symbols.Macro(remainder)
        
        # Nest whatever the macro did not consume (recursive call)
        rem = M.getRemainder()
        remNested = nest(rem)
        
        # Return the whole set
        return tokensFlat + [M] + remNested

      # A comma is not possible in this context
      elif (remainder[0].type == "COMMA") :
        if not(quiet) : print("[WARNING] Expression.nest(): possible uncaught syntax error (comma at top level)")
        return []

      # A closing parenthesis is not possible in this context
      elif (remainder[0].type == "BRKT_CLOSE") :
        if not(quiet) : print("[WARNING] Expression.nest(): possible closing parenthesis in excess")
        return []

      # Anything else is not possible in this context
      else :
        if not(quiet) : print("[WARNING] Expression.nest(): possible uncaught syntax error (unexpected token)")
        return []



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
    (tokensFlat, remainder) = consumeAtomic(tokens)

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
      return False

  # CHECK 2: tokens (at top level and in macros) must follow a 'L op L ... op L' pattern.
  nInfix = 0
  for (n, element) in enumerate(tokens) :        
    if ((n % 2) == 0) :
      if (not(element.type in ["NUMBER", "VAR", "CONSTANT", "MACRO"])) :
        print("[ERROR] The nested expression does not follow the pattern 'L op L op ... L' (unexpected leaf)")
        return False

    else :
      if (element.type != "INFIX") :
        print("[ERROR] The nested expression does not follow the pattern [L op L op ...] (unexpected infix)")
        return False

      else :
        nInfix += 1

  # TODO: check the nesting recursively
  for T in tokens :
    if (T.type == "MACRO") :
      status = T.nest()


  return True



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



# -----------------------------------------------------------------------------
# FUNCTION: isLegalVariableName()
# -----------------------------------------------------------------------------
def isLegalVariableName(inputStr) :
  """
  Test if the input string is a valid variable name.
  
  This test only checks the syntax. It does not indicate if this variable
  has been declared.

  This function is used in symbols.py to detect variables.

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
def showInStr(s: str, loc) -> None :
  """
  Prints 's' with a "^" char right below the location defined by 'loc'.
  It helps to point out at a specific char in the string.

  'loc' shall point using a 0-indexing convention.
  """
  
  if isinstance(loc, int) :
    locTuple = (loc, )
  elif isinstance(loc, tuple):
    locTuple = loc

  # Line 1: input string
  print(s)
  
  # Line 2: cursor
  s = [" "] * len(s)
  for i in locTuple :
    if ((i >= 0) and (i < len(s))) :
      s[i] = "^"
  print("".join(s))



# =============================================================================
# UNIT TESTS
# =============================================================================
if (__name__ == '__main__') :
  
  print("[INFO] Library called as main: running unit tests...")


  assert(isNumber("1") == True)
  assert(isNumber("23") == True)
  assert(isNumber("4.5") == True)
  assert(isNumber("6.0") == True)
  assert(isNumber("789.0000000") == True)
  assert(isNumber(".123456") == True)
  assert(isNumber(".1") == True)
  assert(isNumber(".0") == True)
  assert(isNumber("") == False)
  assert(isNumber("4.2.") == False)
  assert(isNumber(" 12") == False)
  assert(isNumber("2 ") == False)
  assert(isNumber("120 302") == False)
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
  
  assert(splitSpace("pi")             == ("", "pi"))
  assert(splitSpace(" pi")            == (" ", "pi"))
  assert(splitSpace("   pi")          == ("   ", "pi"))
  assert(splitSpace("   test123   ")  == ("   ", "test123   "))
  assert(splitSpace(" *test123  ")    == (" ", "*test123  "))
  assert(splitSpace("  ")             == ("  ", ""))
  assert(splitSpace("")               == ("", ""))
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
  assert(consumeFunc("si  (ax+b)") == ("si", "ax+b)"))
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
  assert(consumeVar("_1.1") == ("", "_1.1"))
  assert(consumeVar("_a") == ("_a", ""))
  assert(consumeVar("a_") == ("a_", ""))
  assert(consumeVar("R112a") == ("R112", "a"))
  assert(consumeVar("R112_") == ("R112_", ""))
  assert(consumeVar("__1") == ("", "__1"))
  assert(consumeVar("__1_a") == ("__1_a", ""))
  assert(consumeVar("__1a") == ("__1a", ""))
  assert(consumeVar("x3_y") == ("x3_y", ""))
  assert(consumeVar("x3_y_") == ("x3_y_", ""))
  assert(consumeVar("x3_y__") == ("x3_y__", ""))
  assert(consumeVar("bonjour") == ("bonjour", ""))
  assert(consumeVar("_var1") == ("_var1", ""))
  assert(consumeVar("3x") == ("", "3x"))          # Rule R5.2
  assert(consumeVar("3_x") == ("", "3_x"))        # Rule R5.3
  assert(consumeVar("3.14x") == ("", "3.14x"))    # Rule R5.4
  assert(consumeVar("3.14_x") == ("", "3.14_x"))  # Rule R5.5
  assert(consumeVar("onigiri12+4") == ("onigiri12", "+4"))      # Rule R5.6
  assert(consumeVar("onigiri_12*pi") == ("onigiri_12", "*pi"))  # Rule R5.7
  assert(consumeVar("abc_2//4") == ("abc_2", "//4"))
  assert(consumeVar("abc_23//4") == ("abc_23", "//4"))
  assert(consumeVar("abc_123456//7") == ("abc_123456", "//7"))
  assert(consumeVar("onigiri_3.14*pi" , quiet=True) == ("onigiri_", "3.14*pi"))  # Rule R5.8
  assert(consumeVar("abc_3.0+ 1"      , quiet=True) == ("abc_", "3.0+ 1"))    # Raises a warning
  assert(consumeVar("abc_23.0+ 1"     , quiet=True) == ("abc_", "23.0+ 1"))   # Raises a warning
  assert(consumeVar("abc_1.+ 1"       , quiet=True) == ("abc_", "1.+ 1"))     # Raises a warning
  assert(consumeVar("abc_12.*3"       , quiet=True) == ("abc_", "12.*3"))     # Raises a warning
  assert(consumeVar("ax1."            , quiet=True) == ("ax", "1."))          # Raises a warning
  assert(consumeVar("R1.4exp(-t/4)"   , quiet=True) == ("R", "1.4exp(-t/4)")) # Raises a warning
  assert(consumeVar("var5_3*3") == ("var5_3", "*3"))
  assert(consumeVar("pi*12x") == ("", "pi*12x"))
  assert(consumeVar("R1*3") == ("R1", "*3"))
  assert(consumeVar(".1") == ("", ".1"))
  assert(consumeVar("sin(2pi*x)") == ("", "sin(2pi*x)"))
  assert(consumeVar("R1_2*3") == ("R1_2", "*3"))
  assert(consumeVar("R1_2*exp(-t/4)") == ("R1_2", "*exp(-t/4)"))
  assert(consumeVar("R1//R2") == ("R1", "//R2"))
  assert(consumeVar("logN (12, 2)") == ("", "logN (12, 2)"))
  assert(consumeVar("sin(") == ("", "sin("))
  assert(consumeVar("R1 sin(") == ("R1", " sin("))
  assert(consumeVar("tan (x+pi)") == ("", "tan (x+pi)"))

  assert(consumeVar("var1var2") == ("var1", "var2"))
  assert(consumeVar("var1_1var2") == ("var1_1", "var2"))
  assert(consumeVar("var1_1_var2") == ("var1_1_var2", ""))
  assert(consumeVar("R1exp(-t/4)") == ("R1", "exp(-t/4)"))
  assert(consumeVar("R1C2exp (-t/8)") == ("R1", "C2exp (-t/8)"))
  assert(consumeVar("C2exp (-t/8)") == ("C2", "exp (-t/8)"))
  assert(consumeVar("var5_3cos(x)") == ("var5_3", "cos(x)"))
  assert(consumeVar("pi(") == ("", "pi("))
  print("- Unit test passed: 'utils.consumeVar()'")

  assert(consumeInfix("*3x") == ("*", "3x"))
  assert(consumeInfix("**2+1") == ("*", "*2+1"))
  assert(consumeInfix("//2+1") == ("//", "2+1"))
  assert(consumeInfix("x-y") == ("", "x-y"))
  assert(consumeInfix("-2x+y") == ("-", "2x+y"))
  assert(consumeInfix("^-3") == ("^", "-3"))
  print("- Unit test passed: 'utils.consumeInfix()'")

  #consumeAtomic([symbols.Token("("), symbols.Token("(")])
  print("- Unit test TODO: 'utils.consumeAtomic()'")

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
