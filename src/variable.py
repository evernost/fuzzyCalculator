# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : variable
# File name       : variable.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : 'Variable' object definition
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# todo
#  


# =============================================================================
# External libs
# =============================================================================
# None.


# -----------------------------------------------------------------------------
# "Factory" functions
# -----------------------------------------------------------------------------
# The following create shortcuts to create the appropriate Variable object.

def scalar(**kwargs) :
  """
  Creates a static variable (scalar).

  The function returns a 'Variable' object. 
  It can be stored under any name you like. The name does not matter.
  
  Example: var_height = variable.rand(name = "height")

  Only the 'name' field really matters because it declares the actual 
  name under which the variable appears in the math expression.
  
  Arguments: 
  - 'name': declares under what name the variable appears in the expression. 
  - 'unit' (OPTIONAL): add a unit to the variable, useful for consistency
  checking and/or showing the calculation results with the proper unit.


  Example calls:
  TODO
  """
  
  print("[ERROR] variable.scalar is TODO!")
  exit()

  return Variable(randType = "SCALAR", **kwargs)




def rand(**kwargs) :
  """
  Creates a uniform random variable.

  The function returns a 'Variable' object. 
  It can be stored under any name you like, it does not really matter.
  
  Example: var_height = variable.rand(name = "height")

  Only the 'name' field matters because it declares the actual 
  name under which the variable appears in the math expression.
  
  Arguments: 
  - 'name': declares under what name the variable appears in the 
  math expression of the fuzzyCalculator.  
  - 'unit' (OPTIONAL): add a unit to the variable, useful for consistency
  checking and/or showing the calculation results with the proper unit.

  
  Possible calls:
  
  height = 181cm +/- 1.0 (absolute uncertainty)
  > var_height = variable.rand(name = "height", val = 181.0, abs = 0.1, unit = "cm")

  R1 = 10.0k +/- 5% (relative uncertainty)
  > var_R1 = variable.rand(name = "R1", val = 10.0, rel = 0.05, unit = "kohm")

  z = [-1, 1]
  > var_z = variable.rand(name = "z", min = -1.0, max = 1.0)

  """
  
  if not("name" in kwargs) :
    print("[ERROR] A variable must be declared with a name.")
    exit()

  if (("center" in kwargs) and ("err" in kwargs)) :
    print(f"[INFO] Creating a uniform variable for '{kwargs['name']}'")
  





  return Variable(randType = "UNIFORM", **kwargs)


def randn(**kwargs) :
  return Variable(randType = "GAUSSIAN", **kwargs)





class Variable : 
  
  # ---------------------------------------------------------------------------
  # METHOD: Variable.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, **kwargs) :
    
    if not("name" in kwargs) :
      print("[ERROR] A variable must be declared with a name.")
      exit()
    else :
      self.name = kwargs["name"]
    
    
    
    if (("min" in kwargs) and ("max" in kwargs)) : 
      self.specType = "RANGE"
      self.min = kwargs["min"]
      self.max = kwargs["max"]
      
      
    print("[WARNING] Variable.__init__() is TODO!")




  # ---------------------------------------------------------------------------
  # METHOD: Variable.XXX
  # ---------------------------------------------------------------------------
  