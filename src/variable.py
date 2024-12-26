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
    print("[ERROR] Variable.rand(): a variable must be declared with a name.")
    exit()
  else :
    varName = kwargs["name"]

  if not("val" in kwargs) :
    print("[ERROR] Variable.rand(): a variable must be given a center value 'val'.")
    exit()

  if ("abs" in kwargs) :
    if (kwargs["abs"] < 0) :
      print("[ERROR] Variable.rand(): the absolute uncertainty cannot be negative.")
      exit()

    if ("rel" in kwargs) :
      print("[ERROR] Variable.rand(): cannot specify both an absolute and a relative margin.")
      exit()
  
    varMin = kwargs["val"] - kwargs["abs"]
    varMax = kwargs["val"] + kwargs["abs"]
    print(f"[INFO] Creating a uniform random variable for '{kwargs['name']}' (min = {varMin}, max = {varMax})")
  
  if ("unit" in kwargs) :
    varUnit = kwargs["unit"]
  else :
    varUnit = ""

  return Variable(randType = "UNIFORM", min = varMin, max = varMax, unit = varUnit, name = varName)







def randn(**kwargs) :
  """
  Creates a gaussian random variable.

  The function returns a 'Variable' object. 
  It can be stored under any name you like, it does not really matter.
  
  Example: var_height = variable.rand(name = "height")

  Only the 'name' field matters because it declares the actual 
  name under which the variable appears in the math expression.
  
  Arguments: 
  

  """
  
  varMean = 0
  varStd = 0
  
  
  return Variable(randType = "GAUSSIAN", mean = varMean, std = varStd)





class Variable : 
  
  # ---------------------------------------------------------------------------
  # METHOD: Variable.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, **kwargs) :
    
    if (kwargs["randType"] == "UNIFORM") :
      self.type = kwargs["randType"]
      self.name = kwargs["name"]
      self.min = kwargs["min"]
      self.max = kwargs["max"]
      
    elif (kwargs["randType"] == "GAUSSIAN") :
      self.type = kwargs["randType"]
      self.mean = kwargs["mean"]
      self.std = kwargs["std"]
    
    else :
      print("[ERROR] Variable.__init__(): unknown randType.")
      exit()
      
    # print("[WARNING] Variable.__init__() is TODO!")



  # ---------------------------------------------------------------------------
  # METHOD: Variable.draw()
  # ---------------------------------------------------------------------------
  def draw(self) :
    """
    Draws one value according to the variable's law.
    """

    print("[WARNING] Variable.draw() is TODO!")