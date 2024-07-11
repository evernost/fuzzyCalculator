# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : parser
# File name       : parser.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : built-in parser for the Fuzzy Calculator
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Parser/evaluator for math expression.
#  
# It supports "natural" inputs (e.g. implicit multiplications) and lazy 
# parenthesis.
# Expressions like "(a+b)(c-d)" or "sin(x+cox(y" are legal.
#
# It is based on native Python and does not require any specific library.
# - no need for regex
# - no complex string manipulation
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
# [R5.4]  "X_2"    -> var("X_2")                 Same as R5.2
# [R5.5]  "X2.0    -> var("X")*2.0               A bit odd, but the most plausible meaning.
# [R5.6]  "X3Y"    -> var("X3")*var("Y")         Not natural, raises a warning.
# [R5.7]  "pi4.0X" -> const("pi")*4.0*var("X")   Acceptable.
# [R5.8]  "pi4X"   -> const("pi")*4*var("X")     Acceptable, but raises a warning.
# [R5.9]  "pixel"  -> var("pixel")               The variable as a whole is more likely than a const/variables product.
#                                                Otherwise, why not even "p*i*x*e*l"?
# [R5.10] "pi_5"   -> var("pi_5")                Underscore serves as disembiguation/indexing and overrides the constant
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
# - a^b^c^d -> a^(b^(c^d))    
# In doubt: check the output interpretation, add parenthesis.
#
# [R11] OPERATORS PRECEDENCE
# It is not recommended to change the relative priorities of basic infix
# operators ('+', '-', '*' , '/', '^').
# - there is no useful case 
# - side effect will emerge due to the parsing strategy 
#   (e.g. rule [R7.2]: '^' is assumed to have the highest precedence for proper operation)
# Also, be careful when defining priority of custom infix and
# think twice about how it interacts with other infix.
#




# =============================================================================
# External libs
# =============================================================================
import token
import binary
import macroleaf
import utils



# -----------------------------------------------------------------------------
# FUNCTION: sanityCheck
# -----------------------------------------------------------------------------
def sanityCheck(inputStr) :
  """
  DESCRIPTION
  Check the input string: make sure it contains valid characters only.
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

  EXAMPLES
  (See unit tests below)
  """

  infixOpsExt = []
  for t in token.INFIX_OPS :
    infixOpsExt += list(t["name"])

  for (loc, char) in enumerate(inputStr) :
    alphaTest   = utils.isAlpha(char)
    digitTest   = utils.isDigit
    infixTest   = (char in infixOpsExt)
    othersTest  = (char in [" ", ".", ",", "_", "(", ")"])
    
    if not(alphaTest or digitTest or infixTest or othersTest) :
      utils.showInStr(inputStr, loc)
      print("[ERROR] this character is not supported by the parser.")
      return False

  return True



# -----------------------------------------------------------------------------
# FUNCTION: bracketBalanceCheck
# -----------------------------------------------------------------------------
def bracketBalanceCheck(inputStr) :
  """
  DESCRIPTION
  Checks if the parenthesis are valid.
  This function allows "lazy parenthesis": closing parenthesis are not required.

  Returns True if the check passed, False otherwise.

  EXAMPLES
  (See unit tests)
  """

  level = 0
  for (loc, char) in enumerate(inputStr) :
    if (char == "(") :
      level += 1
    elif (char == ")") :
      level -= 1

    if (level < 0) :
      utils.showInStr(inputStr, loc)
      print("[ERROR] closing parenthesis in excess.")
      return False

  return True



# -----------------------------------------------------------------------------
# FUNCTION: QParser.firstOrderCheck
# -----------------------------------------------------------------------------
def firstOrderCheck(self, input = "") :
  """
  DESCRIPTION
  Take the chars 2 by 2 and detect any invalid combination.
  Detailed list can be found in 'firstOrderCheck.xslx'.
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input


  for i in (range(len(inputStr)-1)) :
    
    charA = inputStr[i]; charB = inputStr[i+1]

    match (charA, charB) :
      case (".", ".") :
        showInStr(inputStr, i+1)
        print("[ERROR] cannot make sense of 2 consecutive dots. Is it a typo?")
        return False
      
      case (",", ",") :
        showInStr(inputStr, i+1)
        print("[ERROR] cannot make sense of 2 consecutive commas. Is it a typo?")
        return False

      case (",", ")") :
        showInStr(inputStr, i+1)
        print("[ERROR] possible missing argument?")
        return False

      # 
      # TODO: this section needs to be completed.
      # 

      case _:
        pass

  return True



# -----------------------------------------------------------------------------
# METHOD: QParser.reservedWordsCheck
# -----------------------------------------------------------------------------
def reservedWordsCheck(self, input = "") :
  """
  DESCRIPTION
  Check if reserved words (like function names, constants) are used incorrectly.
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  print("TODO")

  return False



# -----------------------------------------------------------------------------
# METHOD: QParser.consumeSpace(<string>)
# -----------------------------------------------------------------------------
def consumeSpace(input = "") :
  """
  DESCRIPTION
  Consume the leading whitespaces contained in the input string.

  EXAMPLES
  (See unit tests)
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  # Input guard
  assert isinstance(inputStr, str), "<consumeConst> expects a string as an input."

  for n in range(len(inputStr)) :
    if (inputStr[n] != " ") :
      return split(inputStr, n)
      
  

# -----------------------------------------------------------------------------
# METHOD: QParser.consumeConst(<string>)
# -----------------------------------------------------------------------------
def consumeConst(self, input = "") :
  """
  DESCRIPTION
  Consume the leading constant in a string.

  If <input> is a string starting with the name of a constant, the tuple (c, rem) is 
  returned, where:
  - <c> is the matching constant name
  - <rem> is the rest of the string.
  
  so that input = c || rem

  If <input> does not start with a known constant or the constant is embedded 
  in a larger name, the tuple ("", input) is returned.
  Refer to rules [5.X] for more details about the parsing strategy.

  The list of available constants is fetched from 'Token.CONSTANTS'.

  EXAMPLES
  (See unit tests)
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  # Input guard
  assert isinstance(inputStr, str), "<consumeConst> expects a string as an input."

  constList = [c["name"] for c in Token.CONSTANTS]

  for n in range(1, len(inputStr)+1) :
    (head, tail) = split(inputStr, n)
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
        elif isAlpha(nextChar) :  
          pass

        else :
          return (head, tail)

  # Case 3: never matched
  return ("", inputStr)



# -----------------------------------------------------------------------------
# METHOD: QParser.consumeNumber(<string>)
# -----------------------------------------------------------------------------
def consumeNumber(self, input = "") :
  """
  DESCRIPTION
  Consume the leading number in a string.

  If <input> is a string starting with a number, the tuple (n, rem) is 
  returned, where:
  - <n> is the matching number
  - <rem> is the rest of the string.
  
  so that input = n || rem

  The function does a 'greedy' read: as many chars as possible are stacked
  to the number as long as it makes sense as a number.

  If <input> does not start with a digit or a dot, the tuple ("", input) is returned.

  The function does not accept negative numbers.

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
  (See unit tests for more examples)
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  # Test the first character.
  # A valid number can only start with a digit or a "."
  if not(inputStr[0].isdigit() or (inputStr[0] == ".")) :
    return ("", inputStr)

  # Start from the first character and consume the remaining chars as long as it makes sense as a number.
  # The longest string that passed the <isNumber> test becomes the candidate.
  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = split(inputStr, n)
    if isNumber(head) :
      nMax = n

    else:
      break
  
  return split(inputStr, nMax)



# -----------------------------------------------------------------------------
# METHOD: QParser.consumeFunc(<string>)
# -----------------------------------------------------------------------------
def consumeFunc(self, input = "") :
  """
  DESCRIPTION
  Consume the leading function in a string.

  If <input> is a string starting with a function, the tuple (f, rem) is 
  returned, where:
  - <f> is the matching function name
  - <rem> is the rest of the string.
  
  The opening parenthesis is omitted in <rem>, so input = f || "(" || rem

  If <input> does not start with a known function, the tuple ("", input) is 
  returned.

  The list of available functions is fetched from 'Token.FUNCTIONS'.

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
  (See unit tests for more examples)
  """
  
  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  functionsExt = [(f["name"] + "(") for f in Token.FUNCTIONS]

  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = split(inputStr, n)
    if (head in functionsExt) :
      nMax = n
  
  # Return the function without opening bracket 
  (tmpHead, tmpTail) = split(inputStr, nMax)
  return (tmpHead[0:-1], tmpTail)



# ---------------------------------------------------------------------------
# METHOD: QParser.consumeVar(<string>)
# ---------------------------------------------------------------------------
def consumeVar(self, input = "") :
  """
  DESCRIPTION
  Consume the leading variable in a string.

  If <input> is a string starting with a variable, the tuple (v, rem) is 
  returned, where:
  - <v> is a potential variable name
  - <rem> is the rest of the string.
  
  so that input = v || rem

  Several rules apply to the parsing strategy. 
  In short, the function tries to match the leading input with what could be
  a plausible variable name based on the rest of the input string.
  
  The function filters out variables when their name matches with a function or a constant.
  In that case, the tuple ("", input) is returned.

  This function is usually followed by a call to <addVariable>, that adds 
  the variable found by <consumeVar> to the list of variables (<variables> attribute).

  The function itself does not alter the content of <variables>.
  So it can be safely used to test whether an unknown string starts with a potential variable.
  
  Refer to rules [5.X] for more details about the parsing strategy. 

  EXAMPLES
  (See unit tests)
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  # Input guard
  assert isinstance(inputStr, str), "<consumeVar> expects a string as an input."

  OUTPUT_FAILURE = ("", inputStr)
  reservedNames = [x["name"] for x in Token.CONSTANTS] + [x["name"] for x in Token.FUNCTIONS]

  # Rule [R2]: a variable must start with a letter or an underscore
  if not(isAlpha(inputStr[0]) or (inputStr[0] == "_")) :
    return ("", inputStr)

  output = (-1, "")
  for n in range(1, len(inputStr)+1) :
    (head, tail) = split(inputStr, n)
    
    # End of string reached
    if (n == len(inputStr)) :
      output = (head, "")
      break
    
    # There are remaining characters to process
    else :
      nextChar = tail[0]

      # Coming next: letter or '_'
      if (isAlpha(nextChar) or (nextChar == "_")) :
        pass

      # Coming next: digit
      elif isDigit(nextChar) :
        (nbr, _) = self.consumeNumber(tail)
      
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
# METHOD: QParser.addVariable(<string>)
# ---------------------------------------------------------------------------
def addVariable(self, input = "") :
  """
  DESCRIPTION
  TODO

  EXAMPLES
  (See unit tests)
  """
  
  if (len(input) > 0) :
    if not(input in self.variables) :
      print(f"[NOTE] New variable added: '{input}'")
      self.variables.append(input)




# ---------------------------------------------------------------------------
# METHOD: QParser.consumeInfix(<string>)
# ---------------------------------------------------------------------------
def consumeInfix(self, input = "") :
  """
  DESCRIPTION
  Consume the leading infix operator in a string.

  If <input> is a string starting with an infix operator, the tuple (op, rem) is 
  returned, where:
  - <op> is the matching infix operator name
  - <rem> is the rest of the string.
  
  so that input = op || rem

  If <input> does not start with a known infix operator, the tuple ("", input) is returned.

  The list of available infix operators is fetched from Token.INFIX_OPS.

  The list of infix operators can be extended with custom operators.
  Please refer to [R6] to see the rules that apply for that.

  EXAMPLES
  (See unit tests)
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  # Input guard
  assert isinstance(inputStr, str), "<consumeInfix> expects a string as an input."

  infixOpsList = [op["name"] for op in Token.INFIX_OPS]

  nMax = 0
  for n in range(1, len(inputStr)+1) :
    (head, _) = split(inputStr, n)
    
    # Returns True only if the whole word matches
    if (head in infixOpsList) :
      nMax = n
  
  return split(inputStr, nMax)



# ---------------------------------------------------------------------------
# METHOD: QParser.tokenize(<string>)
# ---------------------------------------------------------------------------
def tokenize(self, input = "") :
  """
  DESCRIPTION
  Converts the input expression to an ordered list of Token objects.

  The input characters are read, grouped and classified to abstracted types
  (Token objects) while preserving their information.

  EXAMPLES
  TODO
  """

  if (len(input) > 0) :
    inputStr = input
  else :
    inputStr = self.input

  tokenList = []

  while(len(inputStr) > 0) :

    # White spaces do not contribute to the parsing (rule [R9])
    (_, inputStr) = self.consumeSpace(inputStr)
    if (len(inputStr) == 0) :
      break

    (number, tailNumber)      = self.consumeNumber(inputStr)
    (constant, tailConstant)  = self.consumeConst(inputStr)
    (function, tailFunction)  = self.consumeFunc(inputStr)
    (variable, tailVariable)  = self.consumeVar(inputStr)
    (infix, tailInfix)        = self.consumeInfix(inputStr)

    if (number != "") :
      tokenList.append(Token(number))
      inputStr = tailNumber

    elif (constant != "") :
      tokenList.append(Token(constant))
      inputStr = tailConstant
    
    elif (function != "") :
      tokenList.append(Token(function))
      tokenList.append(Token("("))
      inputStr = tailFunction

    elif (variable != "") :
      tokenList.append(Token(variable))
      inputStr = tailVariable
      
    elif (infix != "") :
      tokenList.append(Token(infix))
      inputStr = tailInfix

    else :
      (head, tail) = pop(inputStr)

      if (head == "(") :
        tokenList.append(Token(head))
        inputStr = tail

      elif (head == ")") :
        tokenList.append(Token(head))
        inputStr = tail

      elif (head == ",") :
        tokenList.append(Token(head))
        inputStr = tail

  return tokenList



# ---------------------------------------------------------------------------
# METHOD: QParser.explicitMult
# ---------------------------------------------------------------------------
def explicitMult(self, input = "") :
  """
  DESCRIPTION
  Detects the implicit multiplications in the list of tokens.
  Returns the same list with the multiplication tokens explicited at the right place.

  EXAMPLES
  TODO
  """
  
  nTokens = len(input)

  # Hidden multiplication needs at least 2 tokens
  if (nTokens <= 1) :
    return input

  else :
    output = []
    for n in range(nTokens-1) :
      tokA = input[n]; tokB = input[n+1]

      output.append(tokA)

      match (tokA.type, tokB.type) :
        
        # Example: "pi(x+4)"
        case ("CONSTANT", "BRKT_OPEN") :
          output.append(Token("*"))

        # Example: "R1(R2+R3)"
        case ("VAR", "BRKT_OPEN") :
          output.append(Token("*"))

        # Example: "x_2.1"
        case ("VAR", "NUMBER") :
          output.append(Token("*"))

        # Example: "(x+1)pi"
        case ("BRKT_CLOSE", "CONST") :
          output.append(Token("*"))

        # Example: "(x+1)cos(y)"
        case ("BRKT_CLOSE", "FUNCTION") :
          output.append(Token("*"))

        # Example: "(R2+R3)R1"
        case ("BRKT_CLOSE", "VAR") :
          output.append(Token("*"))

        # Example: "(x+y)(x-y)"
        case ("BRKT_CLOSE", "BRKT_OPEN") :
          output.append(Token("*"))

        # Example: "(x+y)100"
        case ("BRKT_CLOSE", "NUMBER") :
          output.append(Token("*"))

        # Example: "2pi"
        case ("NUMBER", "CONST") :
          output.append(Token("*"))

        # Example: "2exp(-3t)"
        case ("NUMBER", "FUNCTION") :
          output.append(Token("*"))

        # Example: "2x"
        case ("NUMBER", "VAR") :
          output.append(Token("*"))

        # Example: "2(x+y)"
        case ("NUMBER", "BRKT_OPEN") :
          output.append(Token("*"))

        case (_, _) :
          pass
    
    if (n == (nTokens-2)) :
      output.append(tokB)

  return output



# ---------------------------------------------------------------------------
# METHOD: QParser.binarize
# ---------------------------------------------------------------------------
def binarize(self, tokenList) :
  """
  DESCRIPTION
  Takes a list of tokens as input, returns a Binary object.
  
  The Binary object stores the tokens as a hierarchical list (the 'stack')
  looking like:
  
  [L, op, L, op, L, op, ...]
  
  where <op> is an infix and <L> is a constant/variable/number or a Macroleaf.
  Please refer to the Binary object/Macroleaf object documentation for more information.
  
  Building this structure is the first step towards elaborating the full 
  evaluation tree.
  
  Note: the implicit multiplications must be explicited prior to calling the function.
  Refer to the <explicitMult> function for that purpose.

  EXAMPLES
  todo
  """

  if (len(tokenList) >= 1) :
    B = Binary()
    B.process(tokenList)
    return B

  else :
    B = Binary()
    return B




  
  
# ---------------------------------------------------------------------------
# METHOD: QParser.reduce
# ---------------------------------------------------------------------------
def reduce(self, binary) :
  """
  DESCRIPTION
  Takes as input any Binary object, returns a Binary object containing a single
  Macroleaf.

  This function reduces the binary expression by grouping the operators based 
  on their relative priority.
  
  It does not assume commutativity of the infix operators.

  Associativity strategy are detailed in [R10].
  
  Note: minus signs '-' must have been balanced prior to calling this function.

  EXAMPLES
  todo
  """
  
  # Note: maybe there is a better name for the elements in binary.stack than <token>
  
  # 'Reduce' is required for 2 or more infix operators
  print("TODO")
  #if (len(binary.stack) >= 5)
  

  # 1. Chercher la plus haute priorité dans [L op L op L ...]
  
  # 2. Iloter les opérateurs les plus hauts : [L op L op], [L op L], [op L op L op L op L]

  # 3. Créer des macros pour les îlots : [L op L op], M, [op L op L op L op L]
  
  # 4. Fusionner : [L op L op M op L op L op L op L]
  
  # 5. Recommencer jusqu'à ce que tous les opérateurs soient au même niveau
  
  # A la fin il ne reste plus que [L op L op L], tous de même priorité.



# ---------------------------------------------------------------------------
# METHOD: QParser.eval
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

  assert(sanityCheck("pro_ut*cos(2x+pi") == True)
  assert(sanityCheck("input Str") == True)
  assert(sanityCheck("input Str2.1(a+b)|x|") == False)
  assert(sanityCheck("$inputStr") == False)
  assert(sanityCheck("µinputStr") == False)
  assert(sanityCheck("in#putStr") == False)
  assert(sanityCheck("inputStr%") == False)
  assert(sanityCheck("inpuétStr") == False)
  assert(sanityCheck("inpuàtStr") == False)
  print("- Passed: <sanityCheck>")

  assert(bracketBalanceCheck("pro_ut*cos(2x+pi") == True)
  assert(bracketBalanceCheck("pro_ut*cos(2x+pi(") == True)
  assert(bracketBalanceCheck("pro_ut*cos(2x+pi()))") == False)
  assert(bracketBalanceCheck("|3x+6|.2x") == True)
  print("- Passed: <bracketBalanceCheck>")

  assert(firstOrderCheck("sin(2..1x)") == False)
  assert(firstOrderCheck("1+Q(2,)") == False)
  assert(firstOrderCheck("cos(3x+1)*Q(2,,1)") == False)
  print("- Passed: <firstOrderCheck>")

  assert(consumeSpace("pi") == ("", "pi"))
  assert(consumeSpace(" pi") == (" ", "pi"))
  assert(consumeSpace("   pi") == ("   ", "pi"))
  print("- Passed: <consumeSpace>")

  assert(consumeConst("pi") == ("pi", ""))
  assert(consumeConst("inf") == ("inf", ""))
  assert(consumeConst("eps*4") == ("eps", "*4"))
  assert(consumeConst("pi3") == ("pi", "3"))
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

  assert(qParser.consumeNumber("42") == ("42", ""))
  assert(qParser.consumeNumber("4.2") == ("4.2", ""))
  assert(qParser.consumeNumber("4.2.") == ("4.2", "."))
  assert(qParser.consumeNumber(".") == ("", "."))
  assert(qParser.consumeNumber("-.") == ("", "-."))
  assert(qParser.consumeNumber("-12a") == ("", "-12a"))
  assert(qParser.consumeNumber("-33.1") == ("", "-33.1"))
  assert(qParser.consumeNumber("3.14cos(x)") == ("3.14", "cos(x)"))
  assert(qParser.consumeNumber("6.280 sin(y") == ("6.280", " sin(y"))
  assert(qParser.consumeNumber(" 64") == ("", " 64"))
  assert(qParser.consumeNumber("x86") == ("", "x86"))
  print("- Passed: <consumeNumber>")

  assert(qParser.consumeFunc("sina") == ("", "sina"))
  assert(qParser.consumeFunc("sinc(3x+12)") == ("sinc", "3x+12)"))
  assert(qParser.consumeFunc("tan (x-pi)") == ("", "tan (x-pi)"))
  assert(qParser.consumeFunc("floot(-2.4)") == ("", "floot(-2.4)"))
  assert(qParser.consumeFunc("floor(-2.4)") == ("floor", "-2.4)"))
  assert(qParser.consumeFunc("q(2.4, 0.1)") == ("", "q(2.4, 0.1)"))
  assert(qParser.consumeFunc("Q(2.4, 0.1)") == ("Q", "2.4, 0.1)"))
  print("- Passed: <consumeFunc>")

  assert(qParser.consumeVar("bonjour") == ("bonjour", ""))
  assert(qParser.consumeVar("3x") == ("", "3x"))
  assert(qParser.consumeVar("x_2*3") == ("x_2", "*3"))
  assert(qParser.consumeVar("x_23//4") == ("x_23", "//4"))
  assert(qParser.consumeVar("x2.3") == ("x", "2.3"))            # Raises a warning
  assert(qParser.consumeVar("x_23.0+ 1") == ("x_", "23.0+ 1"))  # Raises a warning (this input is seriously odd)
  assert(qParser.consumeVar(".1") == ("", ".1"))
  assert(qParser.consumeVar("pi*12x") == ("", "pi*12x"))
  assert(qParser.consumeVar("sin(2pi*x)") == ("", "sin(2pi*x)"))
  assert(qParser.consumeVar("_a") == ("_a", ""))
  print("- Passed: <consumeVar>")

  assert(qParser.consumeInfix("*3x") == ("*", "3x"))
  assert(qParser.consumeInfix("**2+1") == ("*", "*2+1"))
  assert(qParser.consumeInfix("//2+1") == ("//", "2+1"))
  assert(qParser.consumeInfix("x-y") == ("", "x-y"))
  assert(qParser.consumeInfix("-2x+y") == ("-", "2x+y"))
  assert(qParser.consumeInfix("^-3") == ("^", "-3"))
  print("- Passed: <consumeInfix>")
  
  # B = Binary()
  # B.stack = [Token("-"), Token("4")]
  # print(B)
  # qParser.balanceMinus(B)
  # print(B)
  # print("- Passed: <balanceMinus>")

  print()

  expr = [
    "a^-3cos(x+1)",
    "2x*cos(3.1415t-1.)^3",
    "Q(-3t,0.1)+1",
    "-2x*cos(pi*t-1//R2)", 
    "-R3_2.0x*cos(3.1415t-1//R2)",
    "(x+y)(x-2y)"
  ]

  for e in expr :
    out = qParser.tokenize(e)
    
    print(f"- expression: '{e}'")
    print(out)
    print(qParser.explicitMult(out))
    print()

    out = qParser.explicitMult(out)
    B = qParser.binarize(out)
    B = qParser.balanceMinus(B)
  
