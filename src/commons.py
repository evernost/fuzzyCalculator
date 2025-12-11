# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : -
# File name       : commons.py
# File type       : Python script (Python 3.10 or greater)
# Purpose         : objects common to the processing
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : Thursday, 11 December 2025
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# EXTERNALS
# =============================================================================
# Project libraries
# None.

# Standard libraries
from enum import Enum



# =============================================================================
# CONSTANTS
# =============================================================================
class Status(Enum):
  NOT_RUN = -1
  OK      = 0
  WARNING = 1 
  FAIL    = 2

