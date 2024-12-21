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
  return Variable(randType = "SCALAR", **kwargs)


def rand(**kwargs) :
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
  