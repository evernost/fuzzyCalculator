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
# [EXAMPLE 1] A basic scalar operation
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()
fcalc.input("12*34-56")
fcalc.compile()
fcalc.print()
print("")


# -----------------------------------------------------------------------------
# [EXAMPLE 2] Another basic scalar operation
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()
fcalc.input("-2cos(1.5pi)")
fcalc.compile()
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 3] Your first syntax error
# -----------------------------------------------------------------------------
# fcalc = fuzzyCalculator.Calc()
# fcalc.input("x-3*y+z1/")
# fcalc.compile()
# fcalc.print()
# print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 4] Adding lengths with uncertainties
# -----------------------------------------------------------------------------
var_a = variable.rand(name = "a", val = 1.0, abs = 0.1)  # a = 1.0 +/- 0.1 (uniform)
var_b = variable.rand(name = "b", val = 1.0, abs = 0.1)  # b = 1.0 +/- 0.1 (uniform)

fcalc = fuzzyCalculator.Calc()
fcalc.declare(var_a)
fcalc.declare(var_b)
fcalc.input("a+b")
fcalc.compile()
fcalc.sim(nPts = 1000, mode = "MAX_RANGE")
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 5] Pythagoras' theorem with uncertainties
# -----------------------------------------------------------------------------
var_a = variable.rand(name = "a", val = 3.0, abs = 0.1)  # a = 3.0 +/- 0.1 (uniform)
var_b = variable.rand(name = "b", val = 4.0, abs = 0.1)  # b = 4.0 +/- 0.1 (uniform)

fcalc = fuzzyCalculator.Calc()
fcalc.declare([var_a, var_b])
fcalc.compile("sqrt(a^2+b^2)")
fcalc.sim(nPts = 1000, mode = "MAX_RANGE")
fcalc.print()



# -----------------------------------------------------------------------------
# [EXAMPLE 6] Fuzzy calculation: period of a pendulum
# -----------------------------------------------------------------------------
var_l = variable.rand(name = "l", val = 1.0, abs = 0.05)
var_g = variable.rand(name = "g", val = 9.81, abs = 0.05)

fcalc = fuzzyCalculator.Calc()
fcalc.declare([var_l, var_g])
fcalc.compile("2pi*sqrt(l/g)")
fcalc.setMode("MAX_RANGE")
fcalc.sim(nPts = 1000)
fcalc.print()



# -----------------------------------------------------------------------------
# [EXAMPLE 7] Fuzzy calculation: resistors in parallel
# -----------------------------------------------------------------------------

# 10 Ohms resistance with 5% tolerance (uniform)
R1 = variable.rand(val = 10, tol = 0.05)
R2 = variable.rand(val = 10, tol = 0.05)

fcalc = fuzzyCalculator.Calc()
fcalc.declare(R1)
fcalc.declare(R2)
fcalc.compile("R1//R2 + 100")
fcalc.setMode("MAX_RANGE")
fcalc.sim(nPts = 1000)
fcalc.print()



# -----------------------------------------------------------------------------
# [EXAMPLE 8] Fuzzy calculation
# -----------------------------------------------------------------------------

# Variable with center value and uncertainty: x = 1.0 +/- 0.1
x = variable.rand(center = 1.0, err = 0.1)

# Variable in range: y = [-1.0, 1.0]
y = variable.rand(min = -1.0, max = 1.0)

# You may also declare your variables using a list:
fcalc = fuzzyCalculator.Calc()
fcalc.declare([x, y])
fcalc.compile("sin(2*pi*x + cos(y)")
fcalc.setMode("DIST_95")
fcalc.sim(nPts = 1000)
fcalc.print()



# -----------------------------------------------------------------------------
# EXAMPLE 6
# -----------------------------------------------------------------------------

# Gaussian variable
z1 = variable.randn(mean = 2.0, std = 0.5)
z2 = variable.randn(val = 10, tol95 = 0.5)
z3 = variable.randn(val = 10, tol98 = 0.5)

fcalc = fuzzyCalculator.Calc()
fcalc.declare([z1, z2, z3])
fcalc.compile("(z1^2)-(z2^2) + z3^2")
fcalc.setMode("DIST_99")
fcalc.sim(nPts = 1000)
fcalc.print()



# -----------------------------------------------------------------------------
# EXAMPLE 7 (syntax error)
# -----------------------------------------------------------------------------

z = variable.scalar(1.2)
fcalc.declare(z)
ret = fcalc.compile("-z^+2")

