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
# - special characters already give some flexibility
# - exotic infix operators are not that common. It is not worth the engineering.
# - infix operators are 2 variables functions in disguise.
#   Multiargs functions are already supported and should be the reasonable choice here.
#
# [R7] OMITTED TOKEN RULES
# The infix operator "-" (minus sign) is the only operator that allows an implicit left operand.
# In other words, expressions like "(-3x+..." are accepted.
# That being said: 
# [R7.1] "(-5..." is valid
# [R7.2] "...^-5" is valid (e.g. for '10^-4')
# [R7.3] "a^-3u" will be treated as "(a^(-3))*u"
# [R7.4] "*-4" is not accepted: use parenthesis
# [R7.5] "--4" is not accepted (chaining more than 1 minus sign)
# [R7.6] "(+4" is not accepted (implicit left operand is for minus sign only)
# [R7.7] "-*4" is not accepted
#
# [R8] VARIABLE NAMING
# Variable cannot start with a number.
#
# [R9] WHITE SPACES
# White spaces are not part of the syntax and are simply ignored.
#
# [R10] OPERATORS ASSOCIATIVITY
# Consecutive operators of the same priority are treated differently.
# [R10.1] a/b/c   -> a/(b/c)
# [R10.2] a//b//c -> a//(b//c)      (though it does not matter as it is associative)
# [R10.3] a^b^c^d -> a^(b^(c^d))    (no one will agree on the convention anyway)
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
# ------------
# TODO / IDEAS
# ------------
# Sorted by increasing relative effort: 
# - add support for scientific notation
# - add support for thousands delimitation using "_": "3_141_592" vs "3141592"
# - add support for special characters (pi?)
# - add support for infix like '.+'?
# - add support for complex numbers
# - add an interactive mode where: 
#   > a command prompt appears
#   > variables and their statistics can be typed in the CLI
#   > the tree is built as the user types in the expression for immediate feedback
#   > pipes "|" are automatically translated to "abs("
#   > implicit multiplications are automatically expanded
#   > possible warnings (ambiguities, ...), errors are shown as the user types
#   > ...
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
# None.



# =============================================================================
# TOKEN class
# =============================================================================
class Token :

  # Warning: underscores in the constant's name is not allowed (rule [R5.10])
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



  # ---------------------------------------------------------------------------
  # Default constructor: Token()
  # ---------------------------------------------------------------------------
  def __init__(self, name, value = 0) :
    """
    DESCRIPTION
    Takes an expression as argument, returns a Token object whose type matches
    with the expression.

    Tokens can be of type: 
    - CONSTANT
    - FUNCTION
    - TODO

    EXAMPLES
    Token("4.5")  -> creates a Token of type "NUMBER"
    Token("pi")   -> creates a Token of type "CONSTANT"
    Token("exp")  -> creates a Token of type "FUNCTION"
    Etc.
    """
    self.constantsList = [x["name"] for x in Token.CONSTANTS]
    self.functionsList = [x["name"] for x in Token.FUNCTIONS]
    self.infixOpsList  = [x["name"] for x in Token.INFIX_OPS]
    
    if (name in self.constantsList) :
      self.type = "CONSTANT"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"CONST:'{name}'"

    elif (name in self.functionsList) :
      self.type = "FUNCTION"
      self.name = name
      self.dispStr = f"FCT:'{name}'"
      
      for f in Token.FUNCTIONS :
        if (name == f["name"]) :
          self.nArgs = f["nArgs"]

    elif (name in self.infixOpsList) :
      self.type = "INFIX"
      self.name = name
      self.nArgs = 2
      self.dispStr = f"OP:'{name}'"

    elif (checkVariableSyntax(name)) :
      self.type = "VAR"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"VAR:'{name}'"

    elif (name == "(") :
      self.type = "BRKT_OPEN"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"BRKT:'('"

    elif (name == ")") :
      self.type = "BRKT_CLOSE"
      self.name = name
      self.nArgs = 0
      self.dispStr = f"BRKT:')'"

    elif (name == ",") :
      self.type = "COMMA"
      self.name = name
      self.dispStr = f"SEP:','"

    elif (isNumber(name)) :
      self.type = "NUMBER"
      self.name = name
      self.dispStr = f"NUM:'{name}'"

    elif (isBlank(name)) :
      self.type = "SPACE"
      self.name = name
      self.dispStr = f"BLK:'{name}'"

    else :
      print("[ERROR] Invalid token!")

  # Define the behaviour of print(tokenObj)
  def __str__(self) :
    return self.dispStr
  
  def __repr__(self):
    return self.dispStr



# =============================================================================
# Binary class
# =============================================================================
class Binary:
  """
  DESCRIPTION
  A 'Binary' object is an ordered list of infix operators and (Macro)leaves
  arranged in the following pattern: 

  [L1, op1, L2, op2, ... Ln]
  
  where 
  - <L1> ... <Ln> are leaves or Macroleaves
  - <op1> ... <opn> are infix operators.

  'Leaves' are meant here in a binary tree context and represent the last stage 
  of an evaluation stack. 
  In the context of this parser, a 'leaf' is a constant, a variable or a number.

  A 'Macroleaf' is essentially a leaf on which a function is applied.
  Since a Binary object reduces to a leaf, the leaf of the Macroleaf 
  structure can even be generalized to a Binary object.
  Hence the recursive nature.

  Any valid list of tokens can be associated with a unique Binary Object.
  When the expression does not contain any function or parenthesis, 
  the Binary Object simplifies to a list of leaves and infix operators.
  
  A Binary object comes with an <eval> method whose purpose is to reduce 
  the list of (macro)leaves and infix to a single leaf.

  For that, the <eval> method:
  - reduces all the macroleaves to leaves by calling their own <eval> method
  - builds an ordered evaluation tree based on the relative priorities of each infix
  operators

  'Binary' objects and 'Macroleaf' objects are tightly coupled:
  please refer to the 'Macroleaf' definition for more information.
  """
  
  # ---------------------------------------------------------------------------
  # Default constructor
  # ---------------------------------------------------------------------------
  def __init__(self) :
    """
    DESCRIPTION
    Creates an initialize a Binary object.
    This constructor does not take any arguments.

    EXAMPLE

    """
    self.stack     = []
    self.remainder = []



  # ---------------------------------------------------------------------------
  # METHOD: Binary.process
  # ---------------------------------------------------------------------------
  def process(self, tokenList) :
    """
    DESCRIPTION
    Takes a list of tokens as input and builds the Binary representation of it.
    The list is available in the <stack> attribute. 
    
    Returns: None.
    Only the internal attributes are affected.

    The function expects the list of token to be valid. 
    Refer to functions:
    - TBD 
    - TBD 
    for the common checks to be done prior to calling this method.
    Only the syntax errors associated with this processing will be caught here.
    
    EXAMPLES
    todo
    """
    
    if (len(tokenList) >= 2) :
      (currToken, tail) = (tokenList[0], tokenList[1:])
      
      # Leaves/infix are simply pushed to the stack.
      if (currToken.type in ["CONSTANT", "VAR", "NUMBER", "INFIX"]) :
        self.stack.append(currToken)
        self.process(tail)
      
      # Function creates a Macroleaf and requires another call to <process> on its argument(s).
      elif (currToken.type == "FUNCTION") :
        M = Macroleaf(function = currToken.name, nArgs = currToken.nArgs)
        
        tailNoParenthesis = tail[1:]
        M.process(tailNoParenthesis)
        
        self.stack.append(M)
        self.process(M.remainder)

      # "(" creates a Macroleaf and requires another call to <process>.
      elif (currToken.type == "BRKT_OPEN") :
        M = Macroleaf(function = "id", nArgs = 1)
        
        M.process(tail)
        
        self.stack.append(M)
        self.process(M.remainder)

      # A comma stops the binarisation, the Macroleaf must call <process> on the next argument.
      elif (currToken.type == "COMMA") :
        self.remainder = tail
        return None

      # "(" stops the binarisation, the Macroleaf must call <process> on the next argument.
      elif (currToken.type == "BRKT_CLOSE") :
        self.remainder = tail
        return None
      
      # Anything else is invalid.
      else :
        print(f"[ERROR] Unexpected token: <{currToken}>")



    # Terminal case: 1 token left
    elif (len(tokenList) == 1) :
      currToken = tokenList[0]

      if (currToken.type in ["CONSTANT", "VAR", "NUMBER"]) :
        self.stack.append(currToken)
        self.remainder = []
        return None
      
      elif (currToken.type == "BRKT_CLOSE") :
        self.remainder = []
        return None

      elif (currToken.type == "COMMA") :
        print("[ERROR] The list of tokens cannot end with a comma.")
        return None

      if (currToken.type == "INFIX") :
        print("[ERROR] The list of tokens cannot end with an infix operator.")
        return None

      else :
        print("[ERROR] Unexpected token.")
        return None



    # Terminal case: no token left
    else :
      return None



  def eval(self) :
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """
    print("TODO")



# =============================================================================
# Macroleaf class
# =============================================================================
class Macroleaf:

  def __init__(self, function, nArgs) :
    """
    Description
    A Macroleaf <M> is a recursive structure represented as follows:
    
    M = {F, [B1, B2, ..., Bn]]}
    
    where:
    - <F> is a function
    - <B1>, ..., <Bn> are Binary objects.

    There are as many Binary objects <B1>, ..., <Bn> as arguments taken by the function.
    
    A 'Macroleaf' is essentially a function <F> applied to objects (Binary objects)
    that reduce to a leaf.
    
    The structure being recursive, it needs a terminal case.
    The terminal case is usually a Macroleaf:

    M = {Id, [L]}
    
    where <Id> is the Identity function and <L> is a 'leaf': a constant, a variable or a number.

    
    Claim: any valid expression can be associated to a Macroleaf representation.


    Advantage: once the representation is built, the evaluation is straighforward.
    - Evaluate (recursively) each binary object
    - Apply the top function to the result.

    Priority between operators is decided when the list of Tokens is evaluated.
    Token list evaluation is beyond the scope of this class.

    Examples:
    - cos(2x) -> {F:cos, [NUM:2, OP:*, VAR:x]}


    """
    self.function = function
    self.nArgs = nArgs
    self.args = [Binary() for _ in range(nArgs)]
    self.remainder = []



  def process(self, tokenList) :
    """
    DESCRIPTION
    The parenthesis token must be removed before calling this function.


    EXAMPLES
    todo
    """
    if (len(tokenList) >= 1) :
      
      stack = tokenList
      for n in range(self.nArgs) :
        self.args[n].process(stack)
        stack = self.args[n].remainder
      
      self.remainder = stack
      
    # Terminal case: no token left
    else :
      print("TODO")
      return None



  # -----------------------------------------------------------------------------
  # METHOD: sanityCheck
  # -----------------------------------------------------------------------------
  def sanityCheck(self, input = "") :
    """
    DESCRIPTION
    
    EXAMPLES
    
    """

    if (len(input) > 0) :
      inputStr = input
    else :
      inputStr = self.input



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
  # METHOD: QParser.sanityCheck
  # -----------------------------------------------------------------------------
  def sanityCheck(self, input = "") :
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
  # METHOD: QParser.bracketBalanceCheck
  # -----------------------------------------------------------------------------
  def bracketBalanceCheck(self, input = "") :
    """
    DESCRIPTION
    Checks if the parenthesis are valid.
    This function allows "lazy parenthesis": closing parenthesis are not required.

    Returns True if the check passed, False otherwise.

    EXAMPLES
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
  # METHOD: QParser.firstOrderCheck
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
  def consumeSpace(self, input = "") :
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
    Convert the input expression to an ordered list of Token objects.

    The input characters are read, grouped and classified as abstracted types
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
    Takes a list of tokens as input, returns a recursive structure made of 
    Binary Objects and/or Macroleaf.
    
    The implicit multiplications must be expanded prior to calling the function.
    Refer to the <expandMult> function for that purpose.

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
  # METHOD: QParser.balanceMinus
  # ---------------------------------------------------------------------------
  def explicitZeros(self, input = "") :
    """
    DESCRIPTION
    Detects the minus signs used as a shortcut for the 'opposite' function.
    Takes as input a binarized expression, returns a new binarized expression
    with the minus infix replaced with a macroleaf calling the opposite function.

    The shortcut can be used in very specific context only. Please refer to rules [R7.X]

    EXAMPLES
    "-3..."  -> "(0-3)..."
    "...^-2" -> "...^(0-2)
    """
    
    print("TODO")



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

    EXAMPLES
    todo
    """



  # ---------------------------------------------------------------------------
  # METHOD: QParser.makeEvalTree
  # ---------------------------------------------------------------------------
  def makeEvalTree(self) :  
    """
    DESCRIPTION
    todo

    EXAMPLES
    todo
    """
    print("TODO")



# =============================================================================
# Utilities
# =============================================================================

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



def isDigit(inputStr) :
  """
  DESCRIPTION
  Returns True if the first char of inputStr is a digit.
  """
  char = inputStr[0]

  return (ord(char) >= ord("0")) and (ord(char) <= ord("9"))



def isBlank(inputStr) :
  """
  DESCRIPTION
  Returns True if the input string only contains whitespaces.
  """
  print("TODO")



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



def checkVariableSyntax(inputStr) :
  """
  DESCRIPTION
  Test if the input string is a valid variable name.
  
  This test only checks the syntax. It does not indicate if this variable
  has been declared.

  EXAMPLES
  (See unit tests)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<isNumber> expects a string as an input."

  # Filter out reserved names
  if (inputStr in ([x["name"] for x in Token.CONSTANTS] + [x["name"] for x in Token.FUNCTIONS])) :
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
# Main
# -----------------------------------------------------------------------------
if (__name__ == '__main__') :
  
  print("[INFO] Standalone call: running unit tests...")

  qParser = QParser()

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

  assert(qParser.consumeSpace("pi") == ("", "pi"))
  assert(qParser.consumeSpace(" pi") == (" ", "pi"))
  assert(qParser.consumeSpace("   pi") == ("   ", "pi"))
  print("- Passed: <consumeSpace>")

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
    b = qParser.binarize(out)
  
