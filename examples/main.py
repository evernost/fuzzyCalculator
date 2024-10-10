# -*- coding: utf-8 -*-
# =============================================================================
# Module name     : main
# File name       : main.py
# Purpose         : calling script for the Monte-Carlo calculator.
# Author          : Quentin Biache
# Creation date   : October 10th, 2021
# =============================================================================

# =============================================================================
# Description
# =============================================================================

# =============================================================================
# Libraries declaration
# =============================================================================
import fuzzyCalculator


# Test cases:
# expr = "1.2+ exp(1.6x /1.2)" => OK
# expr = "cos(3x+pi)" => OK
# expr = "-1.4pi + 12.78" => OK
# expr = "-1.4pi + 12.78(" => error
# expr = "cos(x+2" => OK
# expr = "4.1-2+sin(x+2."
# expr = "4.1-2+sin(x+2.1"
# expr = "u + (z-1)*a"
# expr = "var1*var7 + 12var3"
# expr = "var1*var7+var4*1.5var24 + 12.1var3"         <- this is OK-ish
# expr = "var1 + 3*var3- var5log(2)"   <---- this kind of ambiguity must be raised

parser_0 = Qparser.parser()

# Build solver object
# parser_0.tokenize("2-1.4pi + (-12.78)")
# parser_0.tokenize("-1.4pi + 12.78(cos(pi*zboub*tan()))(1.0)")
# parser_0.tokenize("u + (z-1)*a")

# A corriger :
# expr = "R1*-Re"
# expr = "(1)3"

parser_0.tokenize("2cos(3x+1)")
