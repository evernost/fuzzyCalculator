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
fcalc.compile("12*34-567")
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 2] Another basic scalar operation
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()
fcalc.compile("-2cos(1.5pi)")
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 3] Adding lengths with uncertainties
# -----------------------------------------------------------------------------
var_a = variable.rand(name = "a", val = 1.0, abs = 0.1)  # a = 1.0 +/- 0.1 (uniform)
var_b = variable.rand(name = "b", val = 2.0, abs = 0.5)  # b = 2.0 +/- 0.5 (uniform)

fcalc = fuzzyCalculator.Calc()
fcalc.declare(var_a)
fcalc.declare(var_b)
fcalc.compile("a+b")
#fcalc.sim(nPts = 1000)
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 4] Pythagoras' theorem with uncertainties
# -----------------------------------------------------------------------------
var_a = variable.rand(name = "a", val = 3.0, abs = 0.1)  # a = 3.0 +/- 0.1 (uniform)
var_b = variable.rand(name = "b", val = 4.0, abs = 0.2)  # b = 4.0 +/- 0.2 (uniform)

fcalc = fuzzyCalculator.Calc()
fcalc.declare([var_a, var_b])
fcalc.compile("sqrt(a^2+b^2)")
fcalc.sim(runs = 10000)
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 5] Fuzzy calculation: period of a pendulum
# -----------------------------------------------------------------------------
var_l = variable.rand(name = "l", val = 1.0, abs = 0.005)   # l = 1m +/- 5mm
var_g = variable.rand(name = "g", val = 9.81, abs = 0.05)   # g = 9.81 m/s2 +/- 0.05 m/s2 

fcalc = fuzzyCalculator.Calc()
fcalc.declare([var_l, var_g])
fcalc.compile("2pi*sqrt(l/g)")
fcalc.sim(runs = 10000)
fcalc.print()
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 6] Fuzzy calculation: resistors in parallel
# -----------------------------------------------------------------------------
# Resistances with 1% tolerance
var_R1 = variable.rand(name = "R1", val = 10, rel = 0.01, unit = "kohm")
var_R2 = variable.rand(name = "R2", val = 15, rel = 0.01, unit = "kohm")
var_R3 = variable.rand(name = "R3", val = 12, rel = 0.01, unit = "kohm")
var_R4 = variable.rand(name = "R4", val = 22, rel = 0.01, unit = "kohm")

fcalc = fuzzyCalculator.Calc()
fcalc.declare([var_R1, var_R2, var_R3, var_R4])
fcalc.compile("(R1+R2)//(R3+R4)")
fcalc.sim(runs = 10000)
fcalc.plot(bins = 100)
fcalc.percentileRange(p = 0.95) 
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 7] Fuzzy calculation: more possibilities
# -----------------------------------------------------------------------------
var_x = variable.rand(name = "x", val = 1.0, rel = 0.1)   # x = 1.0 +/- 0.1
var_y = variable.rand(name = "y", min = -1.0, max = 1.0)  # y = [-1.0, 1.0]

fcalc = fuzzyCalculator.Calc()
fcalc.declare([var_x, var_y])
fcalc.compile("sin(2*pi*x + cos(y)")
fcalc.sim(runs = 1000)
fcalc.print()



# -----------------------------------------------------------------------------
# [EXAMPLE 8] Fuzzy calculation: fun with gaussian variables
# -----------------------------------------------------------------------------
# z1 = variable.randn(mean = 2.0, std = 0.5)
# z2 = variable.randn(val = 10, tol95 = 0.5)
# z3 = variable.randn(val = 10, tol98 = 0.5)

# fcalc = fuzzyCalculator.Calc()
# fcalc.declare([z1, z2, z3])
# fcalc.compile("(z1^2)-(z2^2) + z3^2")
# fcalc.sim(runs = 1000, mode = "QUANTILE_99")
# fcalc.print()



# -----------------------------------------------------------------------------
# [EXAMPLE 9] Fuzzy calculation: composing expressions
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()

var_Rc = variable.rand(name = "Rc", val = 1000, rel = 0.01, unit = "ohm")
var_Re = variable.rand(name = "Re", val = 220, rel = 0.01, unit = "ohm")
var_Ic = variable.rand(name = "Ic", val = 0.005, rel = 0.1, unit = "A")
var_Vt = variable.rand(name = "Vt", val = 0.026, rel = 0.1, unit = "V")
fcalc.declare([var_Rc, var_Re, var_Ic, var_Vt])

var_gm = fcalc.compileToVar("Ic/Vt", name = "gm")
fcalc.compile("-gm*Rc/(1+gm*Re")
fcalc.sim(runs = 10000)
fcalc.plot(bins = 100)
print("")



# -----------------------------------------------------------------------------
# [EXAMPLE 10] Your first syntax error
# -----------------------------------------------------------------------------
fcalc = fuzzyCalculator.Calc()
fcalc.compile("x-3*y+z1/")
fcalc.print()
print("")


