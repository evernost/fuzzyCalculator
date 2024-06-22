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
# Rules:
# [R1] Constant/function/variable naming
# The name of a function/variable/constant cannot start with a number.
# It would be impossible to tell if it's a variable or an implicit
# product between a number and a variable.
#
# [R2] Function call syntax
# No space is accepted between the function name and the parenthesis.
# It makes the parsing trickier, and does not add any value to it.
#
# [R3] Void Arguments
# Function cannot be called with empty arguments
#
# Notes: 
#  - pipe chars "|" cannot be used for abs value as they lead to ambiguity.
#    Solution needs to be found for that.
#    Example: |a + b|cos(x)|c + d|
#
# TODO:
# - add support for scientific notation
# - add support for thousands delimitation using "_"
# - add interactive mode where: 
#   > the tree is built as the user types in the expression
#   > pipes "|" are automatically translated to abs(
#   > implicit multiplications are automatically expanded
#
# Misc: 
# Python 3.10 is required for the pattern matching features.
#



# =============================================================================
# External libs
# =============================================================================
import logging




#logger = logging.getLogger(__name__)


# class Tree :

#   self.operator = Token("id")
#   self.leaf = Tree("")



# =============================================================================
# TOKEN class
# =============================================================================
class Token :

  CONSTANTS = [
    {"name": "pi" , "value": 3.14159265358979},
    {"name": "inf", "value": 0.0},
    {"name": "eps", "value": 0.0},
    {"name": "i"  , "value": 0.0},
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
  # consumeConst(<string>)
  # -----------------------------------------------------------------------------
  def consumeConst(self, input = "") :
    """
    Description:
    Consume the leading constant name in a string.

    If <input> is a string starting with the name of a constant, the tuple (c, rem) is 
    returned, where:
      - <c> is the matching constant name
      - <rem> is the rest of the string.
    
    so that input = c || rem

    If <input> does not start with a known constant or the constant is embedded 
    in a larger name, the tuple ("", input) is returned.
 
    The list of available constants is fetched from Token.CONSTANTS.
    
    """
    print("TODO!")
    # if (len(input) > 0) :
    #   inputStr = input
    # else :
    #   inputStr = self.input

    # # Input guard
    # assert isinstance(inputStr, str), "<parseConst> expects a string as an input."

    # functionsExt = [(f + "(") for f in functions]

    # # Start with the first character, then gradually take more characters from 
    # # the input string, until eventually taking all of it.
    # # The longest string that passed the <isFunction> test becomes the candidate
    # # (if the test passed at all)
    # # TODO: optimisation possible = s'arrêter dès que isFunction devient faux (aucune chance que ça redevienne vrai)
    # lastValid = 0
    # for n in range(1,len(inputStr)+1) :
    #   (head,_) = split(inputStr,n)
    #   if (head in functionsExt) :
    #     lastValid = n
    
    # # Return the function without opening bracket 
    # (tmpHead, tmpTail) = split(inputStr,lastValid)
    # return (tmpHead[0:-1], tmpTail)





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
    # The longest string that passed the <isNumber> test becomes the candidate
    lastValid = 0
    for n in range(1,len(inputStr)+1) :
      (head,_) = split(inputStr,n)
      if isNumber(head) :
        lastValid = n
    
    return split(inputStr, lastValid)



  # -----------------------------------------------------------------------------
  # METHOD: consumeFunc(<string>)
  # -----------------------------------------------------------------------------
  def consumeFunc(self, input = "") :
    """
    Description:
    Consume the leading function name in a string.

    If <input> is a string starting with a function, the tuple (f, rem) is 
    returned, where:
      - <f> is the matching function name
      - <rem> is the rest of the string.
    
    The opening parenthesis is omitted in <rem>, so input = f || "(" || rem

    If <input> does not start with a known function, the tuple ("", input) is 
    returned.
 
    The list of available functions is fetched from Token.FUNCTIONS.

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

    functionsExt = [(f + "(") for f in Token.FUNCTIONS]

    # TODO: optimisation possible = s'arrêter dès que isFunction devient faux (aucune chance que ça redevienne vrai)
    lastValid = 0
    for n in range(1, len(inputStr)+1) :
      (head, _) = split(inputStr,n)
      if (head in functionsExt) :
        lastValid = n
    
    # Return the function without opening bracket 
    (tmpHead, tmpTail) = split(inputStr, lastValid)
    return (tmpHead[0:-1], tmpTail)



# -----------------------------------------------------------------------------
# parseVar(<string>)
# -----------------------------------------------------------------------------
def parseVar(inputStr) :
  """
  Description:
  If <inputStr> is a string starting with a plausible variable name, the 
  function returns a tuple with 2 elements:
  - the extracted variable
  - the rest of the string
  The function will try to consume the input string as much as possible as long
  as it is a valid variable name (see restrictions on variables name)
  If <inputStr> does not start with a valid variable-looking string, a tuple with 
  an empty string will be returned (this can also be a test to know whether 
  <inputStr> starts with a number or not)
  If the parsing fails at some point (see examples), the function also returns
  an empty string.
  <parseVar> will try to match a legal variable with existing ones. If it does 
  not find anything, it will add it to the list of variables.
  Illegal variable names make <parseVar> fail and nothing is added to the list
  of variables.
  
  Notes: 
  None.

  Known limitations:
  None.

  Examples:
  > parseVar("a*b") = ("a", "*b")
  > parseVar("a42") = ("a42", "")
  > parseVar(" myVar") = ("", "myVar")
  > parseVar("zinzin_64_32-12") = ("zinzin_64_32", "-12")
  (See unit tests for more examples)
  """

  # Input guard
  assert isinstance(inputStr, str), "<parseVar> expects a string as an input."

  # Test the first character.
  # If it is not a letter, don't bother (L4)
  if not(inputStr[0].isalpha()) :
    return ("", inputStr)

  # Start with the first character, then gradually take more characters from 
  # the input string, until eventually taking all of it.
  # The longest string that passed the <isVariable> test becomes the candidate
  # (if the test passed at all)
  # TODO: optimisation possible = s'arrêter dès que isFunction devient faux (aucune chance que ça redevienne vrai)
  lastValid = 0
  for n in range(1,len(inputStr)+1) :
    (head,_) = split(inputStr,n)
    if isVariable(head) :
      lastValid = n
  
  (tmpVar, tail) = split(inputStr,lastValid)
  if not(tmpVar in variables) :
    variables.append(tmpVar)

  if tmpVar in functions :
    print("ERROR: bad function call.")

  return (tmpVar, tail)
















  # -----------------------------------------------------------------------------
  # METHOD: tokenize(<string>)
  # -----------------------------------------------------------------------------
  def tokenize(self, input = "") :
    """
    Description:
    Convert a valid expression to an ordered list of Token objects.

    The input characters are read, grouped and classified as abstracted types
    (Token objects) while preserving their information.

    
 
    The list of available functions is fetched from Token.FUNCTIONS.

    Notes:
    - The following tests must have passed before calling this function: 
      - TBD
      - TBD
    - Opening parenthesis is omitted because later in the parsing engine, a function 
    or a single "(" triggers the same processing. 
    So for the rest of the processing, the "(" following the function is redundant.
    
    Known limitations:
    None.

    Examples:
    > parseFunc("sina") = ("", "sina")
    
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
      (constant, constant_t) = self.consumeConstant(inputStr)
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



# # -----------------------------------------------------------------------------
# # isVariable(<string>)
# # -----------------------------------------------------------------------------
# def isVariable(inputStr) :
#   """
#   Description:
#   Detect if a given string is a legal variable name.
  
#   Known limitations: 
#   None.
  
#   Examples:
#   > isVariable("Martine") = True
#   > isVariable("x2") = True
#   > isVariable("_karen") = False
#   (See unit tests for more examples)
#   """
  
#   # Input guard
#   assert isinstance(inputStr, str), "<isVariable> expects a string as an input."

#   # A variable must start with a letter (L4)
#   if not(inputStr[0].isalpha()) :
#     return False

#   for char in inputStr :
#     if not((char.isalpha()) or (char.isnumeric()) or (char == "_")) :
#       return False

#   return True









# # -----------------------------------------------------------------------------
# # parseInfix(<string>)
# # -----------------------------------------------------------------------------
# def parseInfix(inputStr) :
#   """
#   Description:
#   If <inputStr> is a string starting with an infix operator, the function returns 
#   a tuple with 2 elements:
#   - the extracted infix operator
#   - the rest of the string
#   If <inputStr> does not start with a good candidate infix operator, the first 
#   element of the tuple is an empty string; this can be a test to know whether 
#   <inputStr> starts with an infix operator or not.
#   If the parsing fails at some point (see examples), the first 
#   element of the tuple is also an empty string.

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
  Prints <inputStr> with a "^" char right below at a location
  defined by <loc>.
  It helps to point out a specific char in the string.
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