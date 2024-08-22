# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : qParser
# File name       : qParser.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : built-in parser for the Fuzzy Calculator
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
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
# Expressions like "(a+b)(c-d)" or "sin(x+cos(y" are legal.
#
# It is based on native Python and does not require any specific library.
# - no need for regex
# - no complex string manipulation
# 
# However, if transcription to another programming language is needed, 
# the following features will be required:
# - OOP 
# - string to float conversion
# - the math functions you want to support (sin, cos, exp, etc.)
# - random number generation
#
# Parser grants the most classical math operators ('+', '-', '*', '/', '^') 
# and more obscure ones ('//' for parallel resistor association)
# Usual math functions are included (sin, cos, log, exp, abs, ...) 
#
# The parser preserves the order of the input, therefore does not 
# assume commutativity of infix like '+', '*' etc. 
# This could allow to extend the parser to other types, like matrices.
#
# When called as a 'main', the library runs unit tests on the built-in
# parsing functions.
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
# The following priorities have been defined based on what feels the most "natural"
# interpretation. 
# In case of ambiguity, a warning is raised.
# [R5.1]  "1X"     -> 1*var("X")                 See R2.
# [R5.2]  "1.0X"   -> 1.0*var("X")               See R2.
# [R5.3]  "X2"     -> var("X2")                  Perfectly OK: typical case of variable suffixing.
# [R5.4]  "X_2"    -> var("X_2")                 Same as R5.3
# [R5.5]  "X2.0    -> var("X")*2.0               A bit odd, but the most plausible meaning.
# [R5.6]  "X3Y"    -> var("X3")*var("Y")   or    | Behaviour can be defined with the TBD attribute.
#                     var("X3Y")                 | In both cases, it raises a warning.
# [R5.7]  "pi4X"   -> const("pi")*4*var("X")     Acceptable, but raises a warning.
# [R5.8]  "pi4.0X" -> const("pi")*4.0*var("X")   Acceptable.
# [R5.9]  "pi_5"   -> var("pi_5")                Underscore serves as disembiguation/indexing and overrides the constant
# [R5.10] "pixel"  -> var("pixel")               The variable as a whole is more likely than a const/variables product.
#                                                Otherwise, why not even "p*i*x*e*l"?

# [R5.11] "pipi"   -> var("pipi")                If "pi*pi" was meant, maybe the user should make an effort here
# [R5.12] "inf"    -> const("inf")               Parser tries to see as a whole in priority (so not "i*nf", "i" being a constant too)
#                                                See also [R5.9]
# [R5.13] "ipi"    -> var("ipi")                 Same as [R5.12]
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
import symbols
import binary
import utils



# =============================================================================
# Constant pool
# =============================================================================
# Check status
CHECK_SUCCESS = 0
CHECK_FAILED = 1



# -----------------------------------------------------------------------------
# FUNCTION: sanityCheck(string)
# -----------------------------------------------------------------------------
def sanityCheck(inputStr) :
  """
  DESCRIPTION
  Checks the input string, makes sure it contains valid characters only.
  Valid characters:
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
  (See unit tests in <main>)
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
      utils.showInStr(inputStr, loc)
      print("[ERROR] This character is not supported by the parser.")
      return False

  return True



# -----------------------------------------------------------------------------
# FUNCTION: bracketBalanceCheck(string)
# -----------------------------------------------------------------------------
def bracketBalanceCheck(inputStr) :
  """
  DESCRIPTION
  Checks if the parenthesis are valid.
  This function allows "lazy parenthesis": matching closing parenthesis 
  are not required.

  Returns True if the check passed, False otherwise.

  EXAMPLES
  (See unit tests in <main>)
  """

  level = 0
  for (loc, char) in enumerate(inputStr) :
    if (char == "(") :
      level += 1
    elif (char == ")") :
      level -= 1

    if (level < 0) :
      utils.showInStr(inputStr, loc)
      print("[ERROR] Closing parenthesis in excess.")
      return CHECK_FAILED

  return CHECK_SUCCESS



# -----------------------------------------------------------------------------
# FUNCTION: firstOrderCheck(string)
# -----------------------------------------------------------------------------
def firstOrderCheck(inputStr) :
  """
  DESCRIPTION
  Takes the chars 2 by 2 and detect any invalid combination.
  Detailed list can be found in 'firstOrderCheck.xslx'.
  
  EXAMPLES
  (See unit tests in <main>)
  """

  for i in (range(len(inputStr)-1)) :
    
    charA = inputStr[i]; charB = inputStr[i+1]

    match (charA, charB) :
      case (".", ".") :
        utils.showInStr(inputStr, i+1)
        print("[ERROR] Cannot make sense of 2 consecutive dots. Is it a typo?")
        return CHECK_FAILED
      
      case (",", ",") :
        utils.showInStr(inputStr, i+1)
        print("[ERROR] Cannot make sense of 2 consecutive commas. Is it a typo?")
        return CHECK_FAILED

      case (",", ")") :
        utils.showInStr(inputStr, i+1)
        print("[ERROR] Possible missing argument?")
        return CHECK_FAILED

      # 
      # TODO: this section needs to be completed.
      # 

      case _:
        pass

  return CHECK_SUCCESS



# -----------------------------------------------------------------------------
# FUNCTION: reservedWordsCheck(string)
# -----------------------------------------------------------------------------
def reservedWordsCheck(inputStr) :
  """
  DESCRIPTION
  Check if reserved words (like function names, constants) are used incorrectly.
  
  EXAMPLES
  (See unit tests in <main>)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<reservedWordsCheck> expects a string as an input."

  print("TODO")

  return False



# -----------------------------------------------------------------------------
# FUNCTION: consumeConst(string)
# -----------------------------------------------------------------------------
def consumeConst(inputStr) :
  """
  DESCRIPTION
  Consumes the leading constant in a string.

  If <inputStr> is a string starting with the name of a constant, the tuple (c, rem) is 
  returned, where:
  - <c> is the matching constant name
  - <rem> is the rest of the string.
  
  so that inputStr = c || rem

  If <inputStr> does not start with a known constant or the constant is embedded 
  in a larger name, the tuple ("", input) is returned.
  Refer to rules [5.X] for more details about the parsing strategy.

  The list of available constants is fetched from 'grammar.CONSTANTS'.

  EXAMPLES
  (See unit tests in <main>)
  """

  # Input guard
  assert isinstance(inputStr, str), "<consumeConst> expects a string as an input."

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
  DESCRIPTION
  Consumes the leading number in a string.

  If <input> is a string starting with a number, the tuple (n, rem) is 
  returned, where:
  - <n> is the matching number
  - <rem> is the rest of the string.
  
  so that input = n || rem

  The function does a 'greedy' read: as many chars as possible are stacked
  to the output <n> as long as it makes sense as a number.

  The function accepts fractional numbers ("3.14", "0.2", etc.)
  Omitted leading zero is accepted: ".1", ".0001" etc.

  The function does not accept negative numbers.
  If <input> does not start with a digit or a dot, the tuple ("", inputStr) is returned.

  Notes: 
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
  (See unit tests in <main> for more)
  """

  # Input guard
  assert isinstance(inputStr, str), "<consumeNumber> expects a string as an input."
 
  # Test the first character.
  # A valid number can only start with a digit or a "."
  if not(inputStr[0].isdigit() or (inputStr[0] == ".")) :
    return ("", inputStr)

  # Start from the first character and consume the remaining chars as long as it makes sense as a number.
  # The longest string that passed the <isNumber> test becomes the candidate.
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
  DESCRIPTION
  Consumes the leading function in a string.

  If <inputStr> is a string starting with a function, the tuple (f, rem) is 
  returned, where:
  - <f> is the matching function name
  - <rem> is the rest of the string.
  
  The opening parenthesis is omitted in <rem>, so inputStr = f || "(" || rem

  If <inputStr> does not start with a known function, the tuple ("", inputStr) is 
  returned.

  The list of available functions is fetched from 'symbols.FUNCTIONS'.

  Notes:
  - The function name must be immediatly followed by an opening parenthesis "(".
  There is not point in accepting things like "cos (3x+1)" or "cos ax+1".
  It does not bring anything to the user experience, makes the expression
  harder to read and leads to ambiguity.
  - Opening parenthesis is omitted because later in the parsing engine, a function 
  or a single "(" triggers the same processing. 
  So for the rest of the processing, the "(" following the function is redundant.
  
  Known limitations:
  None.

  EXAMPLES
  > consumeFunc("sina") = ("", "sina")
  > consumeFunc("sinc(3x+12)") = ("sinc", "3x+12)")
  > consumeFunc("tan (x-pi)") = ("", "tan (x-pi)")
  (See unit tests in <main> for more)
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
  DESCRIPTION
  Consumes the leading variable name in a string.
  
  The parsing does not rely on prior variable declaration.
  It only detects and returns a name that is a legal variable name.

  If <inputStr> is a string starting with a variable, the tuple (v, rem) is 
  returned, where:
  - <v> is a legal variable name
  - <rem> is the rest of the string.
  
  so that inputStr = v || rem

  Several rules apply to the parsing strategy. 
  In short, the function tries to match the head of the input with what could be
  a plausible variable name based on the rest of the input string.
  
  The function filters out variables when their name matches with a function or a constant.
  In that case, the tuple ("", input) is returned.

  This function is usually followed by a call to <addVariable>, that adds 
  the variable found by <consumeVar> to the list of variables (<variables> attribute).

  The function itself does not alter the content of <variables>.
  So it can be safely used to test whether an unknown string starts with a potential variable.
  
  Refer to rules [5.X] for more details about the parsing strategy. 

  NOTES
  Future releases might affect this function so that it takes into account the variables 
  that have been declared for the detection.
  This could give some more flexibility in the syntax (especially on rule [5.9])

  EXAMPLES
  (See unit tests in <main> for more)
  """

  # Input guard
  assert isinstance(inputStr, str), "<consumeVar> expects a string as an input."

  OUTPUT_FAILURE = ("", inputStr)
  reservedNames = [x["name"] for x in symbols.CONSTANTS] + [x["name"] for x in symbols.FUNCTIONS]

  # Rule [R2]: a variable must start with a letter or an underscore
  if not(utils.isAlpha(inputStr[0]) or (inputStr[0] == "_")) :
    return ("", inputStr)

  output = (-1, "")
  for n in range(1, len(inputStr)+1) :
    (head, tail) = utils.split(inputStr, n)
    
    # End of string reached
    if (n == len(inputStr)) :
      output = (head, "")
      break
    
    # There are remaining characters to process
    else :
      nextChar = tail[0]

      # Coming next: letter or '_'
      if (utils.isAlpha(nextChar) or (nextChar == "_")) :
        pass

      # Coming next: digit
      elif utils.isDigit(nextChar) :
        (nbr, _) = consumeNumber(tail)
      
        # Number with decimal point: apply rule [R5.5]
        if ("." in nbr) :
          print("[WARNING] Odd syntax: variable prefixed with a fractional number. Please double check the interpretation.")
          output = (head, tail)
          break
          
        # Number without decimal point: apply rule [R5.3]
        else :
          pass

      # Coming next: anything else
      else :
        output = (head, tail)
        break

  (var, _) = output
  if not(var in reservedNames) :
    return output
  
  elif (var == -1) :
    print("[ERROR] Internal error.")

  else :
    return OUTPUT_FAILURE



# ---------------------------------------------------------------------------
# FUNCTION: consumeInfix(string)
# ---------------------------------------------------------------------------
def consumeInfix(inputStr) :
  """
  DESCRIPTION
  Consumes the leading infix operator in a string.

  If <inputStr> is a string starting with an infix operator, the tuple (op, rem) is 
  returned, where:
  - <op> is the matching infix operator name
  - <rem> is the rest of the string.
  
  so that inputStr = op || rem

  If <inputStr> does not start with a known infix operator, the tuple ("", inputStr) is returned.

  The list of available infix operators is fetched from 'symbols.INFIX'

  The list of infix operators can be extended with custom operators.
  Please refer to [R6] to see the rules that apply for that.

  EXAMPLES
  (See unit tests in <main>)
  """

  # Input guard
  assert isinstance(inputStr, str), "<consumeInfix> expects a string as an input."

  infixList = [op["name"] for op in symbols.INFIX]

  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = utils.split(inputStr, n)
    
    # Returns True only if the whole word matches
    if (head in infixList) :
      nMax = n
  
  return utils.split(inputStr, nMax)



# ---------------------------------------------------------------------------
# FUNCTION: tokenize(string)
# ---------------------------------------------------------------------------
def tokenize(inputStr) :
  """
  DESCRIPTION
  Converts the input expression to an ordered list of Token objects.

  The input characters are read, grouped and classified to abstract types
  (Token objects) while preserving their information.
  
  This function assumes that syntax checks have been run prior to the call.
  Otherwise it will not be able to catch errors.

  EXAMPLES
  todo
  """

  tokenList = []

  while(len(inputStr) > 0) :

    # White spaces do not contribute to the parsing (rule [R9])
    (_, inputStr) = utils.splitSpace(inputStr)
    if (len(inputStr) == 0) :
      break

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
      tokenList.append(symbols.Token(variable))
      inputStr = tailVariable
      
    elif (infix != "") :
      tokenList.append(symbols.Token(infix))
      inputStr = tailInfix

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

  return tokenList



# -----------------------------------------------------------------------------
# FUNCTION: secondOrderCheck(tokenList)
# -----------------------------------------------------------------------------
def secondOrderCheck(tokenList) :
  """
  DESCRIPTION
  Takes the tokens 2 by 2 and detect any invalid combination.
  Detailed list can be found in 'secondOrderCheck.xslx'.
  
  EXAMPLES
  (See unit tests in <main>)
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
  Detects the implicit multiplications in the list of tokens.
  Returns the same list with the multiplication tokens explicited at the right place.

  EXAMPLES
  TODO
  """
  
  nTokens = len(tokenList)

  # Hidden multiplication needs at least 2 tokens
  if (nTokens <= 1) :
    return tokenList

  else :
    output = []
    for n in range(nTokens-1) :
      tokA = tokenList[n]; tokB = tokenList[n+1]

      output.append(tokA)

      match (tokA.type, tokB.type) :
        
        # Example: "pi(x+4)"
        case ("CONSTANT", "BRKT_OPEN") :
          output.append(symbols.Token("*"))

        # Example: "R1(R2+R3)"
        case ("VAR", "BRKT_OPEN") :
          output.append(symbols.Token("*"))

        # Example: "x_2.1"
        case ("VAR", "NUMBER") :
          output.append(symbols.Token("*"))

        # Example: "(x+1)pi"
        case ("BRKT_CLOSE", "CONST") :
          output.append(symbols.Token("*"))

        # Example: "(x+1)cos(y)"
        case ("BRKT_CLOSE", "FUNCTION") :
          output.append(symbols.Token("*"))

        # Example: "(R2+R3)R1"
        case ("BRKT_CLOSE", "VAR") :
          output.append(symbols.Token("*"))

        # Example: "(x+y)(x-y)"
        case ("BRKT_CLOSE", "BRKT_OPEN") :
          output.append(symbols.Token("*"))

        # Example: "(x+y)100"
        case ("BRKT_CLOSE", "NUMBER") :
          output.append(symbols.Token("*"))

        # Example: "2pi"
        case ("NUMBER", "CONST") :
          output.append(symbols.Token("*"))

        # Example: "2exp(-3t)"
        case ("NUMBER", "FUNCTION") :
          output.append(symbols.Token("*"))

        # Example: "2x"
        case ("NUMBER", "VAR") :
          output.append(symbols.Token("*"))

        # Example: "2(x+y)"
        case ("NUMBER", "BRKT_OPEN") :
          output.append(symbols.Token("*"))

        case (_, _) :
          pass
    
    if (n == (nTokens-2)) :
      output.append(tokB)

  return output



# ---------------------------------------------------------------------------
# FUNCTION: eval
# ---------------------------------------------------------------------------
def eval(self, binary, point) :
  """
  DESCRIPTION
  Takes as input:
  - <binary> : a reduced Binary object
  - <point>  : a dictionary containing all variables and their value.
  
  Returns the evaluated expression.

  EXAMPLES
  todo
  """
  print("TODO")



# -----------------------------------------------------------------------------
# Main (unit tests)
# -----------------------------------------------------------------------------
if (__name__ == '__main__') :
  
  print("[INFO] Standalone call: running unit tests...")
  print()

  assert(sanityCheck("oni_giri*cos(2x+pi") == True)
  assert(sanityCheck("input Str") == True)
  assert(sanityCheck("input Str2.1(a+b)|x|") == False)
  assert(sanityCheck("$inputStr") == False)
  assert(sanityCheck("µinputStr") == False)
  assert(sanityCheck("in#putStr") == False)
  assert(sanityCheck("inputStr%") == False)
  assert(sanityCheck("inpuétStr") == False)
  assert(sanityCheck("inpuàtStr") == False)
  print("- Passed: <sanityCheck>")

  assert(bracketBalanceCheck("oni_giri*cos(2x+pi") == CHECK_SUCCESS)
  assert(bracketBalanceCheck("oni_giri*cos(2x+pi(") == CHECK_SUCCESS)
  assert(bracketBalanceCheck("oni_giri*cos(2x+pi()))") == CHECK_FAILED)
  assert(bracketBalanceCheck("|3x+6|.2x") == CHECK_SUCCESS)
  print("- Passed: <bracketBalanceCheck>")

  assert(firstOrderCheck("sin(2..1x)") == CHECK_FAILED)
  assert(firstOrderCheck("1+Q(2,)") == CHECK_FAILED)
  assert(firstOrderCheck("cos(3x+1)*Q(2,,1)") == CHECK_FAILED)
  print("- Passed: <firstOrderCheck>")

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
  print("- Passed: <consumeConst>")

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
  print("- Passed: <consumeNumber>")

  assert(consumeFunc("sina") == ("", "sina"))
  assert(consumeFunc("sinc(3x+12)") == ("sinc", "3x+12)"))
  assert(consumeFunc("tan (x-pi)") == ("", "tan (x-pi)"))
  assert(consumeFunc("floot(-2.4)") == ("", "floot(-2.4)"))
  assert(consumeFunc("floor(-2.4)") == ("floor", "-2.4)"))
  assert(consumeFunc("q(2.4, 0.1)") == ("", "q(2.4, 0.1)"))
  assert(consumeFunc("Q(2.4, 0.1)") == ("Q", "2.4, 0.1)"))
  print("- Passed: <consumeFunc>")

  assert(consumeVar("bonjour") == ("bonjour", ""))
  assert(consumeVar("3x") == ("", "3x"))
  assert(consumeVar("x_2*3") == ("x_2", "*3"))
  assert(consumeVar("x_23//4") == ("x_23", "//4"))
  assert(consumeVar("x2.3") == ("x", "2.3"))            # Raises a warning
  assert(consumeVar("x_23.0+ 1") == ("x_", "23.0+ 1"))  # Raises a warning (this input is seriously odd)
  # assert(consumeVar("x3y") == ("x3", "y"))              # Rule R5.6
  assert(consumeVar(".1") == ("", ".1"))
  assert(consumeVar("pi*12x") == ("", "pi*12x"))
  assert(consumeVar("sin(2pi*x)") == ("", "sin(2pi*x)"))
  assert(consumeVar("_a") == ("_a", ""))
  assert(consumeVar("_a") == ("_a", ""))
  print("- Passed: <consumeVar>")

  assert(consumeInfix("*3x") == ("*", "3x"))
  assert(consumeInfix("**2+1") == ("*", "*2+1"))
  assert(consumeInfix("//2+1") == ("//", "2+1"))
  assert(consumeInfix("x-y") == ("", "x-y"))
  assert(consumeInfix("-2x+y") == ("-", "2x+y"))
  assert(consumeInfix("^-3") == ("^", "-3"))
  print("- Passed: <consumeInfix>")
  print()

  testVect = [
    "-u^-3cos(2*pi*v + 1) + 2^0.1x",
    "2x*cos(3.1415t-1.)^3",
    "Q(-3t,0.1)+1",
    "-2x*cos(pi*t-1//R2)", 
    "-R3_2.0x*cos(3.1415t-1//R2)",
    "(x+y)(x-2y)",
    "(-3(x+4))",
    "-x^2"
  ]

  #testVect = ["-2.1+4(2-6)"]

  for expr in testVect :
    
    print(f"----- expression = '{expr}' -----")

    # STEP 1: rewrite the expression as a list of tokens
    tokenList = tokenize(expr)
    
    # STEP 2: detect and add the implicit multiplications
    tokenListFull = explicitMult(tokenList)
    
    # STEP 3: create a binary object from the list of tokens
    B = binary.Binary(tokenListFull)
  
    # STEP 4: nest away operators with higher precedence
    B.nest()
    
    # STEP 6: evaluate!
    B.eval()

    print(f"Tokens          : {tokenList}")
    print(f"Tokens with mult: {tokenListFull}")
    print(f"Binary          : {B}")
    print()


