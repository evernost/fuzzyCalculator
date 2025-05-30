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
# TODO



# =============================================================================
# External libs
# =============================================================================
import random



# -----------------------------------------------------------------------------
# Scalar variable factory function
# -----------------------------------------------------------------------------
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



# -----------------------------------------------------------------------------
# Uniform random variable factory function
# -----------------------------------------------------------------------------
def rand(**kwargs) :
  """
  Creates a uniform random variable.

  The function returns a 'Variable' object. 
  The object can be stored under any name you like, it does not really matter.
  
  Example: var_height = variable.rand(name = "height")

  Only the 'name' field matters because it declares the actual 
  name under which the variable appears in the math expression.
  
  Arguments: 
  - 'name': declares under what name the variable appears in the 
  math expression of the fuzzyCalculator.  
  - 'unit' (OPTIONAL): add a unit to the variable, useful for consistency
  checking and/or showing the calculation results with the proper unit.

  
  Possible calls:
  
  height = 181cm +/- 1.0cm (absolute uncertainty)
  > var_height = variable.rand(name = "height", val = 181.0, abs = 1.0, unit = "cm")

  R1 = 10.0k +/- 5% (relative uncertainty)
  > var_R1 = variable.rand(name = "R1", val = 10.0, rel = 0.05, unit = "kohm")

  z = [-1, 1] (simple range)
  > var_z = variable.rand(name = "z", min = -1.0, max = 1.0)

  """
  
  if not("name" in kwargs) :
    print("[ERROR] Variable.rand(): a variable must be declared with a name.")
    exit()
  else :
    varName = kwargs["name"]



  # min/max specifier
  if ("min" in kwargs) or ("max" in kwargs) :
    if not("max" in kwargs) :
      print("[ERROR] Variable.rand(): when a 'min' is specified, a 'max' is expected.")
      exit()

    if not("min" in kwargs) :
      print("[ERROR] Variable.rand(): when a 'max' is specified, a 'min' is expected.")
      exit()

    varMin = kwargs["min"]
    varMax = kwargs["max"]
    print(f"[INFO] Creating a uniform random variable for '{kwargs['name']}' (range = [{varMin}, {varMax}])")



  # val/abs specifier
  elif (("val" in kwargs) or ("rel" in kwargs) or ("abs" in kwargs)) :
    if ("abs" in kwargs) :
      if (kwargs["abs"] < 0) :
        print("[ERROR] Variable.rand(): the absolute uncertainty cannot be negative.")
        exit()

      if ("rel" in kwargs) :
        print("[ERROR] Variable.rand(): cannot specify both an absolute and a relative uncertainty.")
        exit()
    
      varMin = kwargs["val"] - kwargs["abs"]
      varMax = kwargs["val"] + kwargs["abs"]
      print(f"[INFO] Creating a uniform random variable for '{kwargs['name']}' (range = [{varMin}, {varMax}])")
    
    if ("rel" in kwargs) :
      if (kwargs["rel"] < 0) :
        print("[ERROR] Variable.rand(): the relative uncertainty cannot be negative.")
        exit()

      if ("abs" in kwargs) :
        print("[ERROR] Variable.rand(): cannot specify both an absolute and a relative uncertainty.")
        exit()
    
      varMin = kwargs["val"]*(1.0 - kwargs["rel"])
      varMax = kwargs["val"]*(1.0 + kwargs["rel"])
      print(f"[INFO] Creating a uniform random variable for '{kwargs['name']}' (range = [{varMin}, {varMax}])")

  else :
    print("[ERROR] Variable.rand(): please provide a 'min/max' or 'val/abs' or 'val/rel' specification.")
    exit()



  if ("unit" in kwargs) :
    varUnit = kwargs["unit"]

    # Run some checks on the units
    # if not(varUnit in ["kg", "s", "m", "A", "V"]) :
    # ...


  else :
    varUnit = ""

  return Variable(randType = "UNIFORM", min = varMin, max = varMax, unit = varUnit, name = varName)



# -----------------------------------------------------------------------------
# Gaussian random variable factory function
# -----------------------------------------------------------------------------
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


# Change Variable to:
# - Variable (pure class) with only 'self.hasCache' and 'self.outputCache'
# Then derive:
# - continuousVar
# - discreteVar






class Variable : 
  
  # ---------------------------------------------------------------------------
  # METHOD: Variable.__init__ (constructor)
  # ---------------------------------------------------------------------------
  def __init__(self, **kwargs) :
    
    self.hasCache = False
    self.outputCache = 0.0

    if (kwargs["randType"] == "UNIFORM") :
      self.type = kwargs["randType"]
      self.name = kwargs["name"]
      self.min  = kwargs["min"]
      self.max  = kwargs["max"]
      
    elif (kwargs["randType"] == "GAUSSIAN") :
      self.type = kwargs["randType"]
      self.mean = kwargs["mean"]
      self.std  = kwargs["std"]
    
    else :
      print("[ERROR] Variable.__init__(): unknown randType.")
      exit()
      


  # ---------------------------------------------------------------------------
  # METHOD: Variable.eval()
  # ---------------------------------------------------------------------------
  def eval(self) :
    """
    Draws one value according to the variable's law.
    A new value is drawn at first call to 'Variable.eval()', then it is 
    cached and eval() will always return the same value.

    For a new value, cache must be cleared using 'Variable.clearCache()'.
    """

    if self.hasCache :
      return self.outputCache
    
    else :
      val = random.uniform(self.min, self.max)
      self.hasCache = True
      self.outputCache = val
      return val
    


  # ---------------------------------------------------------------------------
  # METHOD: Variable.clearCache()
  # ---------------------------------------------------------------------------
  def clearCache(self) :
    """
    TODO
    """

    self.hasCache = False
    self.outputCache = 0.0
    






class ContinuousVariable(Variable) :
  
  def __init__(self, **kwargs) :

    self.type = kwargs["randType"]
    self.name = kwargs["name"]

    self.hasCache = False
    self.outputCache = 0.0

    if (kwargs["randType"] == "UNIFORM") :
      self.min  = kwargs["min"]
      self.max  = kwargs["max"]
      
    elif (kwargs["randType"] == "GAUSSIAN") :
      self.mean = kwargs["mean"]
      self.std  = kwargs["std"]
    
    else :
      print("[ERROR] Variable.__init__(): unknown randType.")
      exit()






class DiscreteVariable(Variable) :
  
  def __init__(self, **kwargs) :
    
    self.type = "DISCRETE"
    self.name = kwargs["name"]

    self.hasCache = False
    self.outputCache = 0.0

    print("DiscreteVariable: todo!")




class CompiledVariable :
  
  def __init__(self, name, binaryObj) :
    
    self.type = "COMPILED"
    self.name = name

    self.binary = binaryObj

    self.hasCache = False
    self.outputCache = 0.0
    
    

      

  # ---------------------------------------------------------------------------
  # METHOD: CompiledVariable.eval()
  # ---------------------------------------------------------------------------
  def eval(self) :
    """

    For a new value, cache must be cleared using 'Variable.clearCache()'.
    """

    if self.hasCache :
      return self.outputCache
    
    else :
      val = self.binary.eval()
      self.hasCache = True
      self.outputCache = val
      return val
    


  # ---------------------------------------------------------------------------
  # METHOD: CompiledVariable.clearCache()
  # ---------------------------------------------------------------------------
  def clearCache(self) :
    """
    TODO
    """

    self.hasCache = False
    self.outputCache = 0.0
    


