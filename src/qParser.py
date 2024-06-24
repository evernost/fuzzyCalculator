# -*- coding: utf-8 -*-
# =============================================================================
# Module name     : qParser
# File name       : qParser.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : mathematic expression parser, with Monte-Carlo analysis
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Parser/evaluator for math expression.
#
# This parser is designed for:
# - converting a mathematical expression to an evaluation tree
# - running statistics from an evaluation tree
#  
# It supports "natural" inputs (e.g. implicit multiplications) and lazy 
# parenthesis.
#
# It does not require any specific library or obscure functions:
# - no call to regex engine
# - no complex string manipulation
#
#
#
# -----
# Rules
# -----
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
# It makes the parsing trickier, and does not add any value.
# "exp(-2t)" -> OK
# "cos (3x)" -> rejected
#
# [R4] VOID ARGUMENTS
# Function cannot be called with empty arguments.
#
# [R5] IMPLICIT MULTIPLICATIONS RULES
# The following priorities have been defined based on what feels the most "natural"
# interpretation. In case of ambiguity, a warning is raised.
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
#
#
# -----
# Notes
# -----
#  - pipe chars "|" cannot be used for abs value as they lead to ambiguity.
#    Solution needs to be found for that.
#    Example: |a + b|cos(x)|c + d|
#  - constants cannot contain an underscore (see [R5.9])
#
#
#
# ----
# TODO
# ----
# - add support for scientific notation
# - add support for thousands delimitation using "_"
# - add support for complex numbers
# - add support for special characters (pi?)
# - add interactive mode where: 
#   > the tree is built as the user types in the expression
#   > pipes "|" are automatically translated to "abs("
#   > implicit multiplications are automatically expanded
#
#
#
# ----
# Misc
# ---- 
# Python 3.10 is required for the pattern matching features.
#



# =============================================================================
# External libs
# =============================================================================
#import logging




#logger = logging.getLogger(__name__)


# class Tree :

#   self.operator = Token("id")
#   self.leaf = Tree("")



# =============================================================================
# TOKEN class
# =============================================================================
class Token :

  # Warning: 
  #  - underscores in the constants are not allowed
  CONSTANTS = [
    {"name": "pi" , "value": 3.14159265358979},
    {"name": "i",   "value": 0.0},
    {"name": "eps", "value": 0.0},
    {"name": "inf", "value": 0.0}
  ]
  
  FUNCTIONS = [
    {"name": "id",    "nArgs": 1},
    {"name": "sin",   "nArgs": 1},
    {"name": "cos",   "nArgs": 1},
    {"name": "tan",   "nArgs": 1},
    {"name": "exp",   "nArgs": 1},
    {"name": "ln",    "nArgs": 1},
    {"name": "log10", "nArgs": 1},
    {"name": "logN",  "nArgs": 2},
    {"name": "abs",   "nArgs": 1},
    {"name": "sqrt",  "nArgs": 1},
    {"name": "floor", "nArgs": 1},
    {"name": "ceil",  "nArgs": 1},
    {"name": "round", "nArgs": 1},
    {"name": "Q",     "nArgs": 2},
    {"name": "sinc",  "nArgs": 1}
  ]

  INFIX_OPS = [
    {"name": "+",  "priority": 1},
    {"name": "-",  "priority": 1},
    {"name": "*",  "priority": 2},
    {"name": "/",  "priority": 2},
    {"name": "//", "priority": 2},
    {"name": "^",  "priority": 3}
  ]

  # Default constructor
  def __init__(self, name, value = 0) :
    
    self.constantsList = [x["name"] for x in Token.CONSTANTS]
    self.functionsList = [x["name"] for x in Token.FUNCTIONS]
    self.infixOpsList  = [x["name"] for x in Token.INFIX_OPS]
    
    if (name in self.constantsList) :
      self._type = "CONSTANT"
      self._name = name




    # self.name = name
    # self.value = value
    # self.priority = 0
    # self.nArgs = 0

    # @name.setter
    # def name(self, val)



    @property
    def type(self) :
      return self._type
    






  def __str__(self):
    
    if (self.type == "CONSTANT") :
      return f"Token:{self.type}, value = {self.value}"
  





# =============================================================================
# QParser class
# =============================================================================
# Attributes:
# - <input>     : string containing the expression to be parsed
# - <variables> : list of variables identified while parsing
class QParser :
  
  # Default constructor
  def __init__(self, input = "") :
    self.input     = input
    self.variables = []



  # -----------------------------------------------------------------------------
  # METHOD: sanityCheck
  # -----------------------------------------------------------------------------
  def sanityCheck(self, input = "") :
    """
    Description:
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

    Examples:
    (See unit tests below)
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input

    infixOpsExt = []
    for t in Token.INFIX_OPS :
      infixOpsExt += list(t["name"])

    for (loc, char) in enumerate(inputStr) :
      alphaTest   = ((ord(char) >= ord("a")) and (ord(char) <= ord("z"))) or ((ord(char) >= ord("A")) and (ord(char) <= ord("Z")))
      digitTest   =  (ord(char) >= ord("0")) and (ord(char) <= ord("9"))      
      infixTest   = (char in infixOpsExt)
      othersTest  = (char in [" ", ".", ",", "_", "(", ")"])
      
      if not(alphaTest or digitTest or infixTest or othersTest) :
        showInStr(inputStr, loc)
        print("[ERROR] this character is not supported by the parser.")
        return False

    return True



  # -----------------------------------------------------------------------------
  # METHOD: bracketBalanceCheck
  # -----------------------------------------------------------------------------
  def bracketBalanceCheck(self, input = "") :
    """
    Description:
    Checks if the parenthesis are valid.
    This function allows "lazy parenthesis": closing parenthesis are not required.

    Returns True if the check passed, False otherwise.

    Examples:
    (See unit tests)
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input

    level = 0
    for (loc, char) in enumerate(inputStr) :
      if (char == "(") :
        level += 1
      elif (char == ")") :
        level -= 1

      if (level < 0) :
        showInStr(inputStr, loc)
        print("[ERROR] closing parenthesis in excess.")
        return False

    return True



  # -----------------------------------------------------------------------------
  # METHOD: firstOrderCheck
  # -----------------------------------------------------------------------------
  def firstOrderCheck(self, input = "") :
    """
    Description:
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

        case _:
          pass



    return True



  # -----------------------------------------------------------------------------
  # METHOD: reservedWordsCheck
  # -----------------------------------------------------------------------------
  def reservedWordsCheck(self, input = "") :
    """
    Description:
    Check if reserved words (like function names, constants) are used incorrectly.
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input

    print("TODO")

    return False



  # -----------------------------------------------------------------------------
  # METHOD: consumeConst(<string>)
  # -----------------------------------------------------------------------------
  def consumeConst(self, input = "") :
    """
    Description:
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

    Examples:
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
  # METHOD: consumeNumber(<string>)
  # -----------------------------------------------------------------------------
  def consumeNumber(self, input = "") :
    """
    Description:
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

    Examples:
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
  # METHOD: consumeFunc(<string>)
  # -----------------------------------------------------------------------------
  def consumeFunc(self, input = "") :
    """
    Description:
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

    Examples:
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
  # METHOD: consumeVar(<string>)
  # ---------------------------------------------------------------------------
  def consumeVar(self, input = "") :
    """
    Description:
    Consume the leading variable in a string.

    If <input> is a string starting with a variable, the tuple (v, rem) is 
    returned, where:
      - <v> is the matching variable name
      - <rem> is the rest of the string.
    
    so that input = v || rem

    Several rules apply to the parsing strategy. 
    In short, the function tries to match it with known or declared variables.
    If it fails, it adds it to the variable list.

    Refer to rules [5.X] for more details about the parsing strategy. 

    Examples:
    (See unit tests)
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input

    # Input guard
    assert isinstance(inputStr, str), "<consumeVar> expects a string as an input."

    # Test the first character.
    # If it is not a letter, don't bother (R2)
    if not(isAlpha(inputStr)) :
      return ("", inputStr)

    for n in range(1, len(inputStr)+1) :
      (head, tail) = split(inputStr, n)
      
      if (n == len(inputStr)) :
        return (head, "")
      
      else :
        nextChar = tail[0]

        if (isAlpha(nextChar) or (nextChar == "_")) :
          pass

        elif isDigit(nextChar) :
          (nbr, _) = self.consumeNumber(tail)
        
          if ("." in nbr) :
            return (head, tail)
          
          else :
            pass

        else :
          return (head, tail)

        # Detect anything that could stop treating it as a variable
        # - a number with decimal point: rule [R5.5]
        # - a decimal point
        # ?

        







  # ---------------------------------------------------------------------------
  # METHOD: consumeInfix(<string>)
  # ---------------------------------------------------------------------------
  def consumeInfix(self, input = "") :
    """
    Description:
    Consume the leading infix operator in a string.

    If <input> is a string starting with an infix operator, the tuple (op, rem) is 
    returned, where:
      - <op> is the matching infix operator name
      - <rem> is the rest of the string.
    
    so that input = op || rem

    If <input> does not start with a known infix operator, the tuple ("", input) is returned.
 
    The list of available infix operators is fetched from Token.INFIX_OPS.

    Examples:
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
          return (head, tail)
        
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

    #   Notes:
    #   TODO: comment distinguer le "-" pour l'opposé et le "-" opérateur infixe ?
    #   Mais au pire, est-ce vraiment grave de voir un infixe alors que c'est une 
    #   négation ?
    #   C'est juste que le premier argument de l'infixe peut être omis dans certains cas.


    #   Known limitations:
    #   None.

    #   Examples:
    #   > infixOps  = ["+", "-", "*", "/", "^", "//", ":="]
    #   > parseInfix("+3x") = ("+", "3x")
    #   > parseInfix("//(12cos(pi))") = ("//", "(12cos(pi))")
    #   > parseInfix("-3.14*cos(12)") = ("", "-3.14*cos(12)") # Piège : ça ce n'est pas un infixe ou si ?
    #   (See unit tests for more examples)
    #   """
      
    #   # Input guard
    #   assert isinstance(inputStr, str), "<parseInfix> expects a string as an input."

    #   # Start with the first character, then gradually take more characters from 
    #   # the input string, until eventually taking all of it.
    #   # The longest string that passed the <isFunction> test becomes the candidate
    #   # (if the test passed at all)
    #   # TODO: optimisation possible = s'arrêter dès que isFunction devient faux (aucune chance que ça redevienne vrai)
    #   lastValid = 0
    #   for n in range(1,len(inputStr)+1) :
    #     (head,_) = split(inputStr,n)
    #     if (head in infixOps) :
    #       lastValid = n
      
    #   return split(inputStr,lastValid)






  # ---------------------------------------------------------------------------
  # METHOD: tokenize(<string>)
  # ---------------------------------------------------------------------------
  def tokenize(self, input = "") :
    """
    Description:
    Convert a valid expression to an ordered list of Token objects.

    The input characters are read, grouped and classified as abstracted types
    (Token objects) while preserving their information.

    
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input

    tokenList = []

    while(len(inputStr) > 0):


      # Try all possibilities
      # Only 1 test must pass!
      (number, number_t) = self.consumeNumber(inputStr)
      (constant, constant_t) = self.consumeConst(inputStr)
      (function, function_t) = self.consumeFunction(inputStr)
      (variable, variable_t) = self.consumeVariable(inputStr)


      # Si l'un d'eux est différent de 0 :

      # if ((len(number)*len(constant)*len(function)*len(variable)) == 0) :
      #   error("internal_error")

      # else : 
      #   if testNumber :
      #     (number, tail) = self.consumeNumber(inputStr)



      # Sinon, ça peut être une parenthèse, une virgule, etc:
      



  # ---------------------------------------------------------------------------
  # METHOD: expandMult
  # ---------------------------------------------------------------------------
  def expandMult(self, input = "") :
    """
    Description:
    input = liste de tokens
    output = liste de tokens, avec les multiplications cachées explicitées
    
    """
    print("TODO")



# -----------------------------------------------------------------------------
# pop(<string>)
# -----------------------------------------------------------------------------
def pop(inputStr) :
  """
  Description:
  Return a tuple containing the first character of <inputStr> and its tail.

  Known limitations: 
  None.
  
  Examples:
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
# split(<string>)
# -----------------------------------------------------------------------------
def split(inputStr, n) :
  """
  Description:
  Split a string <inputStr> in two at the breakpoint index <n>.

  Known limitations:
  None.

  Examples:
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
# isNumber(<string>)
# -----------------------------------------------------------------------------
def isNumber(inputStr) :
  """
  Description:
  Test if the input string is a valid number.
  
  Notes: 
  - spaces before, in-between or after are not supported.

  Upcoming features: 
  - support for scientific notation
  - underscores as thousands separator "123_456"
  
  
  Examples:
  > isNumber("4.2") = True
  > isNumber("42") = True
  > isNumber("41209.00000000000") = True
  > isNumber(".41209") = True
  > isNumber("4.2.") = False
  > isNumber(" 12") = False
  > isNumber("2 ") = False
  > isNumber("120 302") = False
  (See unit tests for more examples)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<isNumber> expects a string as an input."

  gotDigit = False
  gotSign = False

  # None of these are valid numbers
  if (inputStr in [".", "-", "-."]) :
    return False

  for (loc, char) in enumerate(inputStr) :
    
    # Handle dot
    if (char == ".") :
      
      # Dot already seen: exit
      if gotDigit :
        return False
      else :
        gotDigit = True
    
    # Anything else than a dot or a digit is invalid
    elif not(char.isdigit()) :
      return False
  
  # If we made it up to here, it's a valid number.
  return True



def isAlpha(inputStr) :
  """
  Description:
  Returns True if the first char of inputStr is a letter.
  Capitalisation is ignored.
  """
  char = inputStr[0]

  testAlpha = False
  testAlpha = testAlpha or ((ord(char) >= ord("A")) and (ord(char) <= ord("Z")))
  testAlpha = testAlpha or ((ord(char) >= ord("a")) and (ord(char) <= ord("z")))

  return testAlpha



def isDigit(inputStr) :
  """
  Description:
  Returns True if the first char of inputStr is a digit.
  """
  char = inputStr[0]

  return (ord(char) >= ord("0")) and (ord(char) <= ord("9"))







def showInStr(inputStr, loc) :
  """
  Description:
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
# Main
# -----------------------------------------------------------------------------
if (__name__ == '__main__') :
  
  print("[INFO] Standalone call: running unit tests...")

  qParser = QParser()

  assert(qParser.sanityCheck("pro_ut*cos(2x+pi") == True)
  assert(qParser.sanityCheck("input Str") == True)
  assert(qParser.sanityCheck("input Str2.1(a+b)|x|") == False)
  assert(qParser.sanityCheck("$inputStr") == False)
  assert(qParser.sanityCheck("µinputStr") == False)
  assert(qParser.sanityCheck("in#putStr") == False)
  assert(qParser.sanityCheck("inputStr%") == False)
  assert(qParser.sanityCheck("inpuétStr") == False)
  assert(qParser.sanityCheck("inpuàtStr") == False)
  print("- Passed: <sanityCheck>")

  assert(qParser.bracketBalanceCheck("pro_ut*cos(2x+pi") == True)
  assert(qParser.bracketBalanceCheck("pro_ut*cos(2x+pi(") == True)
  assert(qParser.bracketBalanceCheck("pro_ut*cos(2x+pi()))") == False)
  assert(qParser.bracketBalanceCheck("|3x+6|.2x") == True)
  print("- Passed: <bracketBalanceCheck>")

  assert(qParser.firstOrderCheck("sin(2..1x)") == False)
  assert(qParser.firstOrderCheck("1+Q(2,)") == False)
  assert(qParser.firstOrderCheck("cos(3x+1)*Q(2,,1)") == False)
  print("- Passed: <firstOrderCheck>")

  assert(qParser.consumeConst("pi") == ("pi", ""))
  assert(qParser.consumeConst("inf") == ("inf", ""))
  assert(qParser.consumeConst("eps*4") == ("eps", "*4"))
  assert(qParser.consumeConst("pi3") == ("pi", "3"))
  assert(qParser.consumeConst("pi_3") == ("", "pi_3"))
  assert(qParser.consumeConst("pir") == ("", "pir"))
  assert(qParser.consumeConst("api") == ("", "api"))
  assert(qParser.consumeConst("pi*12") == ("pi", "*12"))
  assert(qParser.consumeConst("pi 12") == ("pi", " 12"))
  assert(qParser.consumeConst("pi(12+3") == ("pi", "(12+3"))
  assert(qParser.consumeConst("pir*12") == ("", "pir*12"))
  assert(qParser.consumeConst("pi*r*12") == ("pi", "*r*12"))
  assert(qParser.consumeConst("i*pi*r*12") == ("i", "*pi*r*12"))
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

  assert(qParser.consumeVar("3x") == ("", "3x"))
  assert(qParser.consumeVar("x_2*3") == ("x_2", "*3"))          # "x_2" is now a variable
  assert(qParser.consumeVar("x_23//4") == ("x_23", "//4"))      # "x_23" is now a variable
  assert(qParser.consumeVar("x2.3") == ("x", "2.3"))            # Raises a warning
  assert(qParser.consumeVar("x_23.0+1") == ("x_", "23.0+1"))    # Raises a warning (this input is seriously odd)
  assert(qParser.consumeVar(".1") == ("", ".1"))
  print("- Passed: <consumeVar>")

  