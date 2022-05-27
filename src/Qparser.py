# -*- coding: utf-8 -*-
# =============================================================================
# Module name     : Qparser
# File name       : Qparser.py
# Purpose         : parsing library for the Monte-Carlo calculator.
# Author          : Quentin Biache
# Creation date   : 02nd October, 2020
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Math expression parsing tool.
# It takes as input a string containing any math expression.
# As outputs, it... [TODO]
#
# Does not require any specific library so that it can be easily transcribed 
# to any other language, especially any embedded system.

# Known limitations:
# (L2) variables have to start with a letter.
# (L3) variables can NOT contain anything else than letters,
# numbers and "_".
# (L4) functions have to be followed directly with a "(".
# For instance, "cos (" is not allowed for the sake of clarity.
# (L5) infix operators cannot be alphanumeric, or contain parenthesis

# For the sake of clarity, the following is forbidden:
# - implicit post-multiplication: 
#   > "2x" -> treated as 2*x,
#   > "x2" -> always treated as "the variable named x2",
# - ambiguous operations:
#   > "a/b/c" -> error: is it "(a/b)/c" or "a/(b/c)"?
#   > "a^b^c" -> error: is it "(a^b)^c" or "a^(b^c)"?

# Todo:
# make sure constants and ops are compatible before doing anything

# =============================================================================
# Libraries declaration
# =============================================================================
# None.

# =============================================================================
# Classes
# =============================================================================
class parser :
  def __init__(self) :
    # Default operators
    self.constants  = ["e", "pi"]
    self.variables  = []
    self.functions  = ["sin", "cos", "tan", "exp", "ln", "log10", "sqrt", "Q"]
    self.infix_ops  = ["+", "-", "*", "/", "^", "//"]
    
    # Internal machinery
    self.expr           = ""
    self.stack          = []
    self.nesting_level  = 0

  # ---------------------------------------------------------------------------
  # Method REPORT [public]
  # ---------------------------------------------------------------------------  
  def report(self, report_type, string, index = 0, err_code = 0) :
    if (report_type.lower() == "note") :
      print("[NOTE] " + string)
    elif (report_type.lower() == "warning") :
      print("[WARNING] " + string)
    elif (report_type.lower() == "error") :
      if (err_code == 0) :
        print("[ERROR] " + string)
      else :
        print(f"[ERROR-{err_code}] " + string)
      
      dbg_str = [" "]*len(self.expr)
      dbg_str[index] = "^"
      print(self.expr)
      print("".join(dbg_str))
      quit()
    elif (report_type.lower() == "internal") :
      print("[INTERNAL ERROR] " + string)
      quit()
    else :
      print(f"[ERROR] In <report>: report_type \"{report_type}\" is unknown")

  # ---------------------------------------------------------------------------
  # Method IS_CONSTANT [public]
  # ---------------------------------------------------------------------------
  def is_constant(self, expr) :
    return (expr in self.constants)
  
  # ---------------------------------------------------------------------------
  # Method IS_VARIABLE [public]
  # ---------------------------------------------------------------------------
  def is_variable(self, expr) :
    return (expr in self.variables)

  # ---------------------------------------------------------------------------
  # Method IS_INFIX [public]
  # ---------------------------------------------------------------------------
  def is_infix(self, expr) :
    return (expr in self.infix_ops)

  def could_be_infix(self, char) :
    return (char in [s[0] for s in self.infix_ops])

  # ---------------------------------------------------------------------------
  # Method IS_FUNCTION [public]
  # ---------------------------------------------------------------------------
  def is_function(self, expr) :
    return (expr in self.functions)

  # ---------------------------------------------------------------------------
  # PUSH_TOKEN method
  # A token has been identified. Make a few checks before pushing it to the
  # stack.
  # ---------------------------------------------------------------------------
  def push_token(self, type, expr) :
    
    # Variable looking string -------------------------------------------------
    if (type.lower() == "unclassified_var") :
      if (self.is_variable(expr) or (self.is_constant(expr))) :
        self.stack_it(expr)
      else :
        self.report("note", f"implicit declaration of variable \"{expr}\".")
        self.variables.append(expr)
        self.stack_it(expr)
    
    # Litteral looking string -------------------------------------------------
    elif (type.lower() == "litteral") :
      # Is it really a float?
      try :
        float(expr)
      except :
        self.report("internal", f"\"{expr}\" is not a float.")

      self.stack_it(expr)

    # Infix looking string ----------------------------------------------------
    elif (type.lower() == "infix") :
      if self.is_infix(expr) :
        self.stack_it(expr)
      else :
        self.report("internal", f"\"{expr}\" is claimed to be an infix op but is not in the list.")
    
    # Function looking string -------------------------------------------------
    elif (type.lower() == "function") :
      if self.is_function(expr) :
        self.stack_it(expr)
      else :
        self.report("internal", f"\"{expr}\" is claimed to be a function but is not in the list.")
    
    # Unrecognized category ---------------------------------------------------
    else :
      self.report("internal", f"\"{expr}\" is not a valid type.")

  # ---------------------------------------------------------------------------
  # STACK_IT method
  # A token has been identified. Make a few checks before pushing it to the
  # stack.
  # ---------------------------------------------------------------------------
  def stack_it(self, expr) :
    self.stack.append((expr, self.nesting_level))

  # ---------------------------------------------------------------------------
  # INC_NESTING method
  # ---------------------------------------------------------------------------
  def inc_nesting(self) :
    self.nesting_level = self.nesting_level + 1

  # ---------------------------------------------------------------------------
  # DEC_NESTING method
  # ---------------------------------------------------------------------------
  def dec_nesting(self) :
    self.nesting_level = self.nesting_level - 1

  # ---------------------------------------------------------------------------
  # TOKENIZE method
  # Take an expression as an argument and then return is as a binary tree.
  # ---------------------------------------------------------------------------
  def tokenize(self, expr) :
    self.expr = expr
    accu      = ""
    state     = "explore"
    got_dot   = False

    # Loop on the terms of the expression
    for (index, c) in enumerate(expr) :
      
      # Is it the last char?
      is_last_char = (index == (len(expr)-1))

      # -----------------------------------------------------------------------
      # State "EXPLORE" / Progress in the expression and look for something 
      # relevant.
      # -----------------------------------------------------------------------
      if (state == "explore") :
        
        # An empty caracter ---------------------------------------------------
        # No information: skip it.
        if (c == " ") :
          state = "explore"
        
        # Opening parenthesis -------------------------------------------------
        # Increase the nesting level.
        elif (c == "(") :
          if is_last_char :
            self.report("error", "expression cannot terminate with an open parenthesis.", index, err_code = 1)
          else : 
            self.inc_nesting()
            state = "explore"

        # Closing parenthesis -------------------------------------------------
        # Decrease the nesting level.
        elif (c == ")") :
          if (self.nesting_level == 0) :
            self.report("error", "closing parenthesis in excess.", index, err_code = 2)
          else :
            self.dec_nesting()
            state = "explore"

        # A letter ------------------------------------------------------------
        # It can be the beginning of a function, a variable or a constant.
        # Because of (L5), it cannot be an infix op.
        # => jump to "string" state.
        elif c.isalpha() :
          # If it is the last char, this char by itself is a token (variable or const)
          if is_last_char :
            self.push_token("unclassified_var", c)
          else :
            accu   = c
            state  = "string"
        
        # A number ------------------------------------------------------------
        # If it starts with a number, it must be a litteral.
        # => jump to "number" state.
        elif c.isdigit() :
          if is_last_char :
            self.push_token("litteral", c)
          else :
            accu    = c
            got_dot = False
            state   = "number"

        # A dot ---------------------------------------------------------------
        # If it starts with a dot, it is a number with implicit zero (".577" for example)
        # => jump to "number" state.
        elif (c == ".") :
          if is_last_char :
            self.report("warning", "\".\" as last character will be ignored.")
          else :
            accu    = c
            got_dot = True
            state   = "number"

        # None of the above ---------------------------------------------------
        else :
          # Since it is not alphanumeric, empty, parenthesis etc. it could be
          # an infix operator (from (L5))
          # An infix operator can be more than one char long so for now
          # it is impossible to draw conclusions.

          # It is the beginning of an infix operator?
          if (self.could_be_infix(c) or self.is_infix(c)) :
            if is_last_char :
              self.report("error", "expression cannot terminate with an open infix operator.", index, err_code = 3)
            else :
              accu  = c
              state = "infix"
          
          # Really impossible to match it with anything known.
          else :
            self.report("error", f"unsupported character: \"{c}\"", index, err_code = 4)

      # -----------------------------------------------------------------------
      # State "STRING" / On-going variable, function or constant.
      # -----------------------------------------------------------------------
      elif (state == "string") :
        
        # A character, a number or an underscore ------------------------------
        # We are still within a variable, a constant or a function.
        # We stay in this state.
        if (c.isalpha() or c.isdigit() or (c == "_")) :
          accu = accu + c
          if is_last_char :
            self.push_token("unclassified_var", accu)
          else :
            state  = "string"
        
        # Opening parenthesis -------------------------------------------------
        # The string terminates here, its content can be analysed now.
        # It can be:
        # - a function and the parenthesis is part of it,
        # - a variable, and the parenthesis makes an implicit product.
        elif (c == "(") :
          if is_last_char :
            self.report("error", "expression cannot terminate with an open parenthesis.", index, err_code = 1)

          # Is it a function?
          elif self.is_function(accu) :
            self.push_token("function", accu)
            self.inc_nesting()
            accu  = ""
            state = "explore"
            # NOTE: something must be done here to allow a "," from now on
          
          # Otherwise, it can only be a variable or a constant
          # It cannot be anything else really, because the rest of the checks done 
          # in "string" mode enforce the conditions of a proper variable and reject
          # anything else.
          else :
            self.push_token("unclassified_var", accu)
            self.push_token("infix", "*")
            self.inc_nesting()
            accu  = ""
            state = "explore"

        # Closing parenthesis -------------------------------------------------
        # TODO!!
        elif (c == ")") :
          
          if self.is_function(accu) :
            self.report("error", f"unexpected closing parenthesis after function \"{accu}\".", index, err_code = 60)
          else :
            self.push_token("unclassified_var", accu)
            self.dec_nesting()
            accu  = ""
            state = "explore"


        # Empty character -----------------------------------------------------
        # the string has been terminated. Now analyse its content.
        # If the extracted string is:
        # - a function: error case (L4)
        # - a variable, go back to EXPLORE state.
        elif (c == " ") :
          if self.is_function(accu) :
            self.report("error", f"missing parenthesis after function \"{accu}\".", index, err_code = 61)
          else :
            self.push_token("unclassified_var", accu)
            accu  = ""
            state = "explore"
          
        # An infix operator ---------------------------------------------------
        # That terminates the string.
        # If the extracted string is...
        # - an operator, that's an error case (L3),
        # - a variable, go to INFIX state.
        elif (self.could_be_infix(c) or self.is_infix(c)) :
          if is_last_char :
            self.report("error", "expression cannot terminate with an open infix operator.", index, err_code = 3)
          
          # Was is a function before that? => illegal
          elif self.is_function(accu) :
            self.report("error", f"missing parenthesis after function \"{accu}\".", index, err_code = 6)
          
          # Otherwise, it was a variable
          else :
            self.push_token("unclassified_var", accu)
            accu  = c
            state = "infix"

        # Anything else -------------------------------------------------------
        # Raise an exception.
        else :
          self.report("error", f"current parsing state was string decoding, but got \"{c}\", which is not allowed in this context.", index, err_code = 50)

      # -----------------------------------------------------------------------
      # State "NUMBER" / On-going number.
      # -----------------------------------------------------------------------
      elif (state == "number") :
        
        # A digit -------------------------------------------------------------
        # Keep stacking.
        if c.isdigit() :
          if is_last_char :
            self.push_token("litteral", accu + c)
          else :
            accu   = accu + c
            state  = "number"

        # A dot ---------------------------------------------------------------
        # Allowed only once.
        elif (c == ".") :
          if (got_dot) :
            self.report("error", "too many dots for one single number.", index, err_code = 7)
          else :
            accu    = accu + c
            got_dot = True
            state   = "number"

        # A character ---------------------------------------------------------
        # Assume implicit product.
        elif c.isalpha() :
          if is_last_char :
            # Add the char to the stack with implicit product
            self.push_token("litteral", accu)
            self.push_token("infix", "*")
            self.push_token("unclassified_var", c)
          else :
            self.push_token("litteral", accu)
            self.push_token("infix", "*")
            accu    = c
            got_dot = False
            state   = "string"

        # Opening parenthesis -------------------------------------------------
        # Nesting level increments + implicit multiply
        elif (c == "(") :
          if is_last_char :
            self.report("error", "expression cannot terminate with an open parenthesis.", index, err_code = 1)
          else :
            self.push_token("litteral", accu)
            self.push_token("infix", "*")
            self.inc_nesting()
            accu    = ""
            got_dot = False
            state   = "explore"
        
        # Closing parenthesis -------------------------------------------------
        # The number has been terminated. 
        # Go back to EXPLORE state.
        elif (c == ")") :
          self.push_token("litteral", accu)
          self.dec_nesting()
          accu    = ""
          got_dot = False
          state   = "explore"

        # Empty character -----------------------------------------------------
        # The number has been terminated. 
        # Go back to EXPLORE state.
        elif (c == " ") :
          self.push_token("litteral", accu)
          accu    = ""
          got_dot = False
          state   = "explore"

        # An infix operator ---------------------------------------------------
        elif (self.could_be_infix(c) or self.is_infix(c)) :
          self.push_token("litteral", accu)
          accu    = c
          got_dot = False
          state   = "infix"

        # Anything else -------------------------------------------------------
        # Raise an exception.
        else :
          self.report("error", f"current parsing state was litteral decoding, but got \"{c}\", which is not allowed in this context.", index, err_code = 51)

      # -----------------------------------------------------------------------
      # State "INFIX" / On-going infix operator.
      # -----------------------------------------------------------------------
      elif (state == "infix") :
        
        # An empty caracter ---------------------------------------------------
        if (c in [" ", "(", ")"]) :
          if self.is_infix(accu) :
            self.push_token("infix", accu)
            if (c == "(") :
              self.inc_nesting()
            elif (c == ")") :
              self.dec_nesting()
            accu  = ""
            state = "explore"            
          else :
            self.report("error", f"\"{accu}\" is not a valid infix operator.", index, err_code = 8)

        # A letter ------------------------------------------------------------
        elif c.isalpha() :
          if self.is_infix(accu) :
            self.push_token("infix", accu)
          
            if is_last_char :
              self.push_token("unclassified_var", c)
            else :
              accu    = c
              got_dot = False
              state   = "string"

          else :
            self.report("error", f"\"{accu}\" is not a valid infix operator.", index, err_code = 8)
        
        # A number ------------------------------------------------------------
        elif c.isdigit() :
          if self.is_infix(accu) :
            self.push_token("infix", accu)
            accu  = c
            state = "number"
          else :
            self.report("error", f"\"{accu}\" is not a valid infix operator.", index, err_code = 8)

        # A dot ---------------------------------------------------------------
        # Legit. Example: "-.2"
        elif (c == ".") :
          if self.is_infix(accu) :
            self.push_token("infix", accu)            
            accu    = c
            got_dot = True
            state   = "number"
          else :
            self.report("error", f"\"{accu}\" is not a valid infix operator.", index, err_code = 8)

        # None of the above ---------------------------------------------------
        else :
          
          # Keep stacking as long as it looks like an infix operator
          if (self.could_be_infix(c) or self.is_infix(c)) :
            accu  = accu + c
            state = "infix"
          else :
            self.report("error", f"current parsing state was infix op decoding, but got \"{c}\", which is not allowed in this context.", index, err_code = 52)

      # -----------------------------------------------------------------------
      # Default state (error case)
      # -----------------------------------------------------------------------
      else :
        self.report("internal", "attempted access to an unrecognized state.", index, err_code = 8)

    # End of parsing
    if (self.nesting_level != 0) :
      self.report("error", f"incorrect number of parenthesis.", index, err_code = 9)

    print(self.stack)

