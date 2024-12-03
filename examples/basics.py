# -*- coding: utf-8 -*-
# =============================================================================
# Project         : Fuzzy Calculator
# Module name     : basics
# File name       : basics.py
# File type       : Python script (Python 3.10 or higher)
# Purpose         : demo of the Fuzzy Calculator: basics
# Author          : QuBi (nitrogenium@outlook.fr)
# Creation date   : Thursday, 10 October 2024
# -----------------------------------------------------------------------------
# Best viewed with space indentation (2 spaces)
# =============================================================================

# =============================================================================
# Description
# =============================================================================
# The following script illustrates how to call the Fuzzy Calculator in typical 
# use cases.
# First example: basics.



# =============================================================================
# External libs
# =============================================================================
import src.fuzzyCalculator as fuzzyCalculator
import src.variable as variable



# =============================================================================
# Main script
# =============================================================================



# -----------------------------------------------------------------------------
# EXAMPLE 1: basic scalar operations
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()
fcalc.input("1234*5678-9876")
fcalc.compile()







# -----------------------------------------------------------------------------
# EXAMPLE 2: your first syntax error
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()
fcalc.input("x-3*")
fcalc.compile()






a = variable.scalar(3.14)
fcalc.declare(a)

fcalc.compile("a + cos(pi/2 + 0.01)")

ret = fcalc.eval()

# -----------------------------------------------------------------------------
# EXAMPLE 2: resistors in parallel 
# -----------------------------------------------------------------------------

# 10 Ohms resistance with 5% tolerance (uniform)
R1 = variable.rand(val = 10, tol = 0.05)
R2 = variable.rand(val = 10, tol = 0.05)

fcalc.declare(R1)
fcalc.declare(R2)
fcalc.compile("R1//R2 + 100")
fcalc.sim(nPts = 1000)

# -----------------------------------------------------------------------------
# EXAMPLE 2
# -----------------------------------------------------------------------------

# Variable with center value and uncertainty: x = 1.0 +/- 0.1
x = variable.rand(center = 1.0, err = 0.1)

# Variable in range: y = [-1.0, 1.0]
y = variable.rand(min = -1.0, max = 1.0)

fcalc.declare(x)
fcalc.declare(y)
fcalc.compile("sin(2*pi*x + cos(y)")
fcalc.sim(nPts = 1000)

# -----------------------------------------------------------------------------
# EXAMPLE 3
# -----------------------------------------------------------------------------

# Gaussian variable
z1 = variable.randn(mean = 2.0, std = 0.5)
z2 = variable.randn(val = 10, tol95 = 0.5)
z3 = variable.randn(val = 10, tol98 = 0.5)

fcalc.declare(z1)
fcalc.declare(z2)
fcalc.declare(z3)
fcalc.compile("(z1^2)-(z2^2) + z3^2")
fcalc.sim(nPts = 1000)

# -----------------------------------------------------------------------------
# EXAMPLE 4 (syntax error)
# -----------------------------------------------------------------------------

z = variable.scalar(1.2)
fcalc.declare(z)
ret = fcalc.compile("-z^+2")

