# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : variable
# File name       : variable.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : 
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : June 1st, 2024
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# todo
#  


# =============================================================================
# External libs
# =============================================================================




# "Factory" functions for smooth call from outside the library
def rand(**kwargs) :
  return Variable(randType = "UNIFORM", **kwargs)


def randn(**kwargs) :
  return Variable(randType = "GAUSSIAN", **kwargs)





class Variable : 
  
  # -----------------------------------------------------------------------------
  # METHOD: Variable.__init__ (constructor)
  # -----------------------------------------------------------------------------
  def __init__(self, **kwargs) :
    if (("min" in kwargs) and ("max" in kwargs)) : 
      self.specType = "RANGE"
      self.min = kwargs["min"]
      self.max = kwargs["max"]
      
      
    elif

  # -----------------------------------------------------------------------------
  # METHOD: Variable.XXX
  # -----------------------------------------------------------------------------
  