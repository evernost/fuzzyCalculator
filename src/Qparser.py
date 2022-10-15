# -*- coding: utf-8 -*-
# =============================================================================
# Module name     : Qparser
# File name       : Qparser.py
# Purpose         : parsing library for the Monte-Carlo calculator (recursive version)
# Author          : Quentin Biache
# Creation date   : 11th September, 2022
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Arithmetic expression parsing tool.
# Does not require any specific library so that it can be easily transcribed 
# to any other language, especially any embedded system.
#
# The global policy is to be permissive (it won't complain for missing closing
# bracket) as long as it leads to no ambiguity.
#
# Known limitations:
# L1: functions name have to start with a letter.
# L2: parenthèse doit suivre immédiatement le nom de la fonction. Pas d'espace ou je ne sais quoi.
# L3: (TBC) functions can't have void argument ("myFun()"). 
# Pour l'instant c'est plus une crainte qu'une limitation avérée.
# L4: variables name can only start with a letter.
# L5: concatenation of variables/constants/functions names as implicit product is not allowed
#
# TODO:
# - add support for scientific notation
# - add support for thousands delimitation using "_"


# =============================================================================
# Libraries declaration
# =============================================================================
# None.

# Settings for the parser
constants = ["e", "pi"]
functions = ["sin", "cos", "tan", "exp", "ln", "log10", "sqrt", "Q", "floor", "ceil", "round", "sinc"]
infixOps  = ["+", "-", "*", "/", "^", "//", ":="]
variables = []

# -----------------------------------------------------------------------------
# pop(<string>)
# -----------------------------------------------------------------------------
def pop(inputStr) :
  """
  Returns a tuple containing the first character of <inputStr> and its tail.

  Known limitations: 
  None.
  
  Examples:
  - pop("abcde") = ("a", "bcde")
  - pop("a") = ("a", "")
  - pop("") = ("", "")
  """

  # Input guard
  assert isinstance(inputStr, str), "<pop> expects a string as an input."

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
  Splits a string <inputStr> in two, at the breakpoint <n>.

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
  Detect if a given string is a number.
  Known limitations: 
  - scientific notation is not supported
  - spaces before, in-between or after are not supported.
  
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
    
    # Handle minus sign
    elif (char == "-") :
      
      # Minus sign already seen: invalid, exit.
      if gotSign :
        return False
      else :
        # Minus sign not at position "0": invalid, exit.
        if (loc > 0) :
          return False
        else :
          gotSign = True
    
    # Anything other than a dot, minus sign or digit is invalid
    elif not(char.isdigit()) :
      return False
  
  # If we made it up to here, it's a valid number.
  return True



# -----------------------------------------------------------------------------
# isVariable(<string>)
# -----------------------------------------------------------------------------
def isVariable(inputStr) :
  """
  Detect if a given string is a legal variable name.
  Known limitations: 
  None.
  
  Examples:
  > isVariable("Martine") = True
  > isVariable("x2") = True
  > isVariable("_karen") = False
  (See unit tests for more examples)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<isVariable> expects a string as an input."

  # A variable must start with a letter (L4)
  if not(inputStr[0].isalpha()) :
    return False

  for char in inputStr :
    if not((char.isalpha()) or (char.isnumeric()) or (char == "_")) :
      return False

  return True

# -----------------------------------------------------------------------------
# parseNumber(<string>)
# -----------------------------------------------------------------------------
def parseNumber(inputStr) :
  """
  Description:
  If <inputStr> is a string starting with a number, the function returns a tuple
  with 2 elements:
  - the extracted number
  - the rest of the string
  The function will try to consume the input string as much as possible as long
  as it is a valid number (that includes integrating useless trailing zeroes)
  If <inputStr> does not start with a valid number-looking string, a tuple with 
  an empty string will be returned (this can also be a test to know whether 
  <inputStr> starts with a number or not)
  If the parsing fails at some point (see examples), the function also returns
  an empty string.
  
  Notes: 
  - the number is returned "as is" without interpretation. So "-.0" will 
  return a "-.0" string even though it is simply "0".
  - "-." is not considered as a valid number.

  Known limitations:
  - scientific notation is not supported.

  Examples:
  > parseNumber("42") = ("42", "")
  > parseNumber("4.2") = ("4.2", "")
  > parseNumber("4.2.") = ("4.2", ".")
  (See unit tests for more examples)
  """

  # Input guard
  assert isinstance(inputStr, str), "<parseNumber> expects a string as an input."

  # Test the first character.
  # If it is not a number, a minus sign or a dot, don't bother.
  if not(inputStr[0].isdigit() or (inputStr[0] == "-") or (inputStr[0] == ".")) :
    return ("", inputStr)

  # Start with the first character, then gradually take more characters from 
  # the input string, until eventually taking all of it.
  # The longest string that passed the <isNumber> test becomes the candidate
  # (if the test passed at all)
  # TODO: optimisation possible = s'arrêter dès que isNumber devient faux (aucune chance que ça redevienne vrai)
  lastValid = 0
  for n in range(1,len(inputStr)+1) :
    (head,_) = split(inputStr,n)
    if isNumber(head) :
      lastValid = n
  
  return split(inputStr,lastValid)



# -----------------------------------------------------------------------------
# parseFunc(<string>)
# -----------------------------------------------------------------------------
def parseFunc(inputStr) :
  """
  Description:
  If <inputStr> is a string starting with a function, the function returns a tuple
  with 2 elements:
  - the extracted function
  - the rest of the string
  If <inputStr> does not start with a good candidate function, the first 
  element of the tuple is an empty string; this can be a test to know whether 
  <inputStr> starts with a function or not.
  If the parsing fails at some point (see examples), the first 
  element of the tuple is also an empty string.

  Notes:
  - Function are considered as a bracketing "()", with the function acting
  as a processing. In that matter, the following rules apply; the function
  name must be:
  - followed by a parenthesis
  - that parenthesis must come immediatly after the name of the function.
  There is not point to accept things like "cos (3x+1)". It make things
  more complicated for expressions that aren't even readable.
  Not even talking about "cos 3x -5". How am I supposed to parse that?
  Parcimony principle: don't accept things that lead to more complexity.
  - It is up to the user to ensure that syntax errors like "cos (12x)" are
  handled properly (e.g. reject a variable name that is actually a function)

  Known limitations:
  None.

  Examples:
  > functions = ["sin", "cos", "tan", "exp", "ln", "log10", "sqrt", "sinc"]
  > parseFunc("sina") = ("", "sina")
  > parseFunc("sinc(3x+12)") = ("sinc", "3x+12)")
  > parseFunc("tan (x-pi)") = ("", "tan (x-pi)")
  (See unit tests for more examples)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<parseFunc> expects a string as an input."

  functionsExt = [(f + "(") for f in functions]

  # Start with the first character, then gradually take more characters from 
  # the input string, until eventually taking all of it.
  # The longest string that passed the <isFunction> test becomes the candidate
  # (if the test passed at all)
  # TODO: optimisation possible = s'arrêter dès que isFunction devient faux (aucune chance que ça redevienne vrai)
  lastValid = 0
  for n in range(1,len(inputStr)+1) :
    (head,_) = split(inputStr,n)
    if (head in functionsExt) :
      lastValid = n
  
  # Return the function without opening bracket 
  (tmpHead, tmpTail) = split(inputStr,lastValid)
  return (tmpHead[0:-1], tmpTail)



# -----------------------------------------------------------------------------
# parseInfix(<string>)
# -----------------------------------------------------------------------------
def parseInfix(inputStr) :
  """
  Description:
  If <inputStr> is a string starting with an infix operator, the function returns 
  a tuple with 2 elements:
  - the extracted infix operator
  - the rest of the string
  If <inputStr> does not start with a good candidate infix operator, the first 
  element of the tuple is an empty string; this can be a test to know whether 
  <inputStr> starts with an infix operator or not.
  If the parsing fails at some point (see examples), the first 
  element of the tuple is also an empty string.

  Notes:
  TODO: comment distinguer le "-" pour l'opposé et le "-" opérateur infixe ?
  Mais au pire, est-ce vraiment grave de voir un infixe alors que c'est une 
  négation ?
  C'est juste que le premier argument de l'infixe peut être omis dans certains cas.


  Known limitations:
  None.

  Examples:
  > infixOps  = ["+", "-", "*", "/", "^", "//", ":="]
  > parseInfix("+3x") = ("+", "3x")
  > parseInfix("//(12cos(pi))") = ("//", "(12cos(pi))")
  > parseInfix("-3.14*cos(12)") = ("", "-3.14*cos(12)") # Piège : ça ce n'est pas un infixe ou si ?
  (See unit tests for more examples)
  """
  
  # Input guard
  assert isinstance(inputStr, str), "<parseInfix> expects a string as an input."

  # Start with the first character, then gradually take more characters from 
  # the input string, until eventually taking all of it.
  # The longest string that passed the <isFunction> test becomes the candidate
  # (if the test passed at all)
  # TODO: optimisation possible = s'arrêter dès que isFunction devient faux (aucune chance que ça redevienne vrai)
  lastValid = 0
  for n in range(1,len(inputStr)+1) :
    (head,_) = split(inputStr,n)
    if (head in infixOps) :
      lastValid = n
  
  return split(inputStr,lastValid)



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
# parseParenthesis(<string>)
# -----------------------------------------------------------------------------
def parseParenthesis(inputStr) :
  """
  Description:
  Splits <inputStr> into 2 components:
  - the content of the first level parenthesis
  - the remainder (if any)
  Function looks for opening/closing parenthesis only. It does not care about 
  anything else (checking the validity of the content is up to the parser)
  This function is an assistant to the parser; it helps the parser analyse
  the content of a parenthesis.

  Notes: 
  - <inputStr> must start with an opening parenthesis (helps detecting erroneous
  calls to the function), namely the parenthesis the content of which we want 
  to retrieve.
  - Omitting the closing parenthesis is OK.

  Known limitations:
  None.

  Examples:
  > parseParenthesis("(2x+(3y-12z))-12") = ("2x+(3y-12z)", "-12")
  > parseParenthesis("(1+cos(2x") = ("1+cos(2x", "")                            # Closing parenthesis can be omitted.
  > parseParenthesis("(nonsense$$jn(zbjb')ç!)") = ("nonsense$$jn(zbjb')ç!", "") # Content does not matter, only parenthesis do.
  > parseParenthesis("()(eg)zf") = ("", "(eg)zf")                               # Empty parenthesis (same return value as an error, because it is an error!)
  > parseParenthesis("(a)(ab)") = ("a", "(ab)")
  > parseParenthesis("(1+x))") = ("(1+x)", ")")                                 # Unbalanced, but the first is correct. Next call will fail though
  > parseParenthesis(")(1+x)") = ("", ")(1+x)")                                 # Error: does not start with "("
  > parseParenthesis("tan(alpha)-3x(1+z)") = ("", "tan(alpha)-3x(1+z)")         # Error: does not start with "("
  (See unit tests for more examples)
  """

  # Input guard
  assert isinstance(inputStr, str), "<parseParenthesis> expects a string as an input."

  # Test the first character.
  # If it is not an opening parenthesis, don't bother.
  if (inputStr[0] != "(") :
    # print("[WARNING] Incorrect call to <parseParenthesis>")
    return ("", inputStr)

  (_, tail) = pop(inputStr)
  
  # A few basic tests
  if (tail[0] == ")") :
    print("ERROR: unexpected parenthesis")

  triggered = False
  # print("Entry point: " + tail)
  nestLevel = 1
  for (loc, char) in enumerate(tail) :
    if (char == "(") :
      nestLevel = nestLevel + 1

    if (char == ")") :
      if (nestLevel == 0) :
        print("Incorrect balance")
      else :
        nestLevel = nestLevel - 1

    # Went back to ground level: done!
    if ((nestLevel == 0) and (triggered == False)) :
      (a,b) = split(tail, loc) 
      return (a,b[1:])
      # triggered = True
      # (a,b) = split(tail,loc)
      # print(f"End: {a}")

  return (tail, "")



  # if (nestLevel > 0) :
  #   print("Terminated (omitted parenthesis)")
  # elif (nestLevel == 0) :
  #   print("Terminated (complete parenthesis)")
  # else :
  #   print("Terminated with errors.")

  # print(f"Final nest level: {nestLevel}")
  # print("\n")

# -----------------------------------------------------------------------------
# parseConstant(<string>)
# -----------------------------------------------------------------------------
def parseConstant(inputStr) :
  print("TODO")

  # Parsing MUST carry on as long as letters/underscore keep coming in
  # (L5: concatenation of variables/functions is not allowed)

# -----------------------------------------------------------------------------
# parseInterval(<string>)
# -----------------------------------------------------------------------------
def parseInterval(inputStr) :
  print("TODO")



# -----------------------------------------------------------------------------
# parseMultiarg(<string>)
# -----------------------------------------------------------------------------
# The characters in <inputStr> are expected to be a sequence of arguments of a 
# function with multiple arguments
# ex: parseMultiarg("4x+1, 2y, 3)+cos(2x)")
def parseMultiarg(inputStr) :
  print("TODO")



# -----------------------------------------------------------------------------
# parse(<string>)
# -----------------------------------------------------------------------------
def parse(inputStr, stack = []) :

  (head, tail) = pop(inputStr)

  # Void input (terminal case) ------------------------------------------------
  if (inputStr == "") :
    return stack

  # Blank ---------------------------------------------------------------------
  if (head == " ") :
    return parse(tail, stack)

  # Number --------------------------------------------------------------------
  (tmpNumber, tmpRem) = parseNumber(inputStr)
  if (tmpNumber != "") :
    newStack = stack + [tmpNumber]
    # stack.append(tmpNumber)
    return parse(tmpRem, newStack)

  # Function ------------------------------------------------------------------
  (tmpFunc, tmpRem) = parseFunc(inputStr)
  if (tmpFunc != "") :
    newStack = stack + [tmpFunc]
    (p,q) = parseParenthesis("(" + tmpRem)
    newStack.append(parse(p,[]))
    return parse(q, newStack)

  # Infix ---------------------------------------------------------------------
  (tmpInfix, tmpRem) = parseInfix(inputStr)
  if (tmpInfix != "") :
    newStack = stack + [tmpInfix]
    return parse(tmpRem, newStack)
  
  # Variable (done at the end because it is the most permissive) --------------
  (tmpVar, tmpRem) = parseVar(inputStr)
  if (tmpVar != "") :
    newStack = stack + [tmpVar]
    return parse(tmpRem, newStack)

  # Round brackets ------------------------------------------------------------
  if (head == "(") :
    
    # Analyse parenthesis content
    (parenthesisContent, rem) = parseParenthesis(inputStr)
    newStack = stack + [parse(parenthesisContent,[])]
    return parse(rem, newStack)

  if (head == ")") :
    print("Unexpected closing parenthesis!")
    return stack

  print("Not supposed to land here")

  # # Square brackets -----------------------------------------------------------
  # elif (head == "[") :
  #   (interval, tail) = parseInterval(inputStr)
  #   return([interval, parse(tail)])

  # elif (head == "]") :
  #   print("Error: unexpected closing square parenthesis")
  #   # TODO: return something

  # # Errors --------------------------------------------------------------------
  # elif (inputStr[0] == "_") :
  #   print("Error: unexpected underscore")

  # else :
  #   print("Error: unexpected.")




# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

# If run as a function: call the unit tests
if (__name__ == '__main__') :
  
  print("Running unit tests...")

  # Unit test: function <pop>
  assert(pop("abcde") == ("a", "bcde"))
  assert(pop("a") == ("a", ""))
  assert(pop("") == ("", ""))
  print("- Passed: <pop>")

  # Unit test: function <split>
  assert(split("pouet",-1)   == ("", "pouet"))
  assert(split("pouet",0)    == ("", "pouet"))
  assert(split("pouet",1)    == ("p", "ouet"))
  assert(split("pouet",2)    == ("po", "uet"))
  assert(split("pouet",5)    == ("pouet", ""))
  assert(split("pouet",6)    == ("pouet", ""))
  assert(split("pouet",100)  == ("pouet", ""))
  print("- Passed: <split>")

  # Unit test: function <isNumber>
  assert(isNumber("4.2") == True)
  assert(isNumber("42") == True)
  assert(isNumber("41209.00000000000") == True)
  assert(isNumber(".41209") == True)
  assert(isNumber(".0") == True)
  assert(isNumber(".00000000000") == True)
  assert(isNumber("-.0") == True)
  assert(isNumber("-.2") == True)
  assert(isNumber("-1.2") == True)
  assert(isNumber(" 12") == False)
  assert(isNumber("2 ") == False)
  assert(isNumber("120 302") == False)
  assert(isNumber("120a302") == False)
  assert(isNumber("1-.2") == False)
  assert(isNumber("- 12") == False)
  assert(isNumber(" -12") == False)
  assert(isNumber("4.2.") == False)
  assert(isNumber("-.") == False)
  assert(isNumber("-") == False)
  assert(isNumber(".") == False)
  print("- Passed: <isNumber>")
  
  # Unit test: function <isVariable>
  assert(isVariable("Martine") == True)
  assert(isVariable("x2") == True)
  assert(isVariable("myVar12") == True)
  assert(isVariable("myVar_") == True)
  assert(isVariable(" myVar12") == False)
  assert(isVariable("myVar_ ") == False)
  assert(isVariable("myVar Plougastel") == False)
  assert(isVariable("2x") == False)
  assert(isVariable("my*Var") == False)
  assert(isVariable("_karen") == False)
  print("- Passed: <isVariable>")

  # Unit test: function <parseNumber>
  assert(parseNumber("42") == ("42", ""))
  assert(parseNumber("4.2") == ("4.2", ""))
  assert(parseNumber("4.2.") == ("4.2", "."))
  assert(parseNumber("4.2_") == ("4.2", "_"))
  assert(parseNumber("-64caca") == ("-64", "caca"))
  assert(parseNumber(".4var3") == (".4", "var3"))
  assert(parseNumber("-.0ma_super_Variable") == ("-.0", "ma_super_Variable"))
  assert(parseNumber("-5.00000") == ("-5.00000", ""))
  assert(parseNumber("garb42age") == ("", "garb42age"))
  assert(parseNumber("0.0") == ("0.0", ""))
  assert(parseNumber("-.0") == ("-.0", ""))
  assert(parseNumber("-.") == ("", "-."))
  assert(parseNumber("-12.a01") == ("-12.", "a01"))
  assert(parseNumber("7.q.-541") == ("7.", "q.-541"))
  assert(parseNumber("[5.41,12cos(x)]") == ("", "[5.41,12cos(x)]"))
  print("- Passed: <parseNumber>")

  # Function <parseFunc>
  assert(parseFunc("prout") == ("", "prout"))
  assert(parseFunc("ex()") == ("", "ex()"))
  assert(parseFunc("exp()") == ("exp", ")"))
  assert(parseFunc("Q(2x)") == ("Q", "2x)"))
  assert(parseFunc("log10(some_arg)") == ("log10", "some_arg)"))
  assert(parseFunc("tan") == ("", "tan"))   # il manque la parenthèse
  assert(parseFunc("cos(4x-7sin(2pi*x^2)") == ("cos", "4x-7sin(2pi*x^2)"))
  assert(parseFunc("4x-7sin(2pi*x^2)") == ("", "4x-7sin(2pi*x^2)"))
  print("- Passed: <parseFunc>")

  # Function <parseInfix>
  assert(parseInfix("+3x") == ("+", "3x"))
  assert(parseInfix("//(12cos(pi))") == ("//", "(12cos(pi))"))
  assert(parseInfix("-3.14*cos(12)") == ("-", "3.14*cos(12)")) # omitted first argument for the infix op
  assert(parseInfix("3.14*cos(12)") == ("", "3.14*cos(12)"))
  print("- Passed: <parseInfix>")

  # Function <parseVar>
  assert(parseVar("a*b") == ("a", "*b"))
  assert(parseVar("a42 * 3cos(2pi*x)") == ("a42", " * 3cos(2pi*x)"))
  assert(parseVar(" myVar") == ("", " myVar"))
  assert(parseVar("zinzin_64_32-12") == ("zinzin_64_32", "-12"))
  print("- Passed: <parseVar>")

  # Function <parseParenthesis>
  assert(parseParenthesis("(2x+(3y-12z))-12") == ("2x+(3y-12z)", "-12"))
  assert(parseParenthesis("(1+cos(2x") == ("1+cos(2x", ""))                             # Closing parenthesis can be omitted.
  assert(parseParenthesis("(nonsense$$jn(zbjb')ç!)") == ("nonsense$$jn(zbjb')ç!", ""))  # Content does not matter, only parenthesis do.
  assert(parseParenthesis("()(eg)zf") == ("", "(eg)zf"))                                # Empty parenthesis
  assert(parseParenthesis("(a)(ab)") == ("a", "(ab)"))
  assert(parseParenthesis("(1+x))") == ("1+x", ")"))                                    # Unbalanced, but the first is correct. Next call will fail though
  assert(parseParenthesis(")(1+x)") == ("", ")(1+x)"))                                  # Error: does not start with "("
  assert(parseParenthesis("tan(alpha)-3x(1+z)") == ("", "tan(alpha)-3x(1+z)"))          # Error: does not start with "("
  print("- Passed: <parseParenthesis>")

  print("Unit tests done.")

  # print(parse(" 3.14x+  12cos(pi)/4y"))
  # print(parse(" 3.14x+  12cos(pi/24)/4y"))
  # print(parse("((x^2)+(y^2))/((x+y)^2"))
  print(parse("cos((2*x)+y^2"))
