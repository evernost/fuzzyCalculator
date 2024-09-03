# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : commons
# File name       : commons.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : definition of global variables
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : August 23rd, 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# Definition of the constants, functions, etc. used accross all the 
# source files.
#
# NOTE
# Be cautious when declaring anything here as it will be exposed everywhere 
# in the rest of the source code without prefix ("from commons import *")
#



# =============================================================================
# External libs
# =============================================================================
# None.



# =============================================================================
# Constant pool
# =============================================================================
CHECK_SUCCESS = 0
CHECK_FAILED = 1

# Applies the second option in rule [R5.9]
# "X3Y" -> var("X3")*var("Y")       | PARSING_RULE_NUMBER_STOPS_VAR_PARSING = False
# "X3Y" -> var("X3Y")               | PARSING_RULE_NUMBER_STOPS_VAR_PARSING = True
# See "qParser.py" for more details.
PARSING_RULE_NUMBER_STOPS_VAR_PARSING = True


# =============================================================================
# Main (unit tests)
# =============================================================================
if (__name__ == '__main__') :
  print("[INFO] There are no unit tests available for the package 'commons.py'")

