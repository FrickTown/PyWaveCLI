"""
[PyWaveCLI Module]
examples.py -- A few lines of code demonstrating the uppermost layer of interfacing with the core.
Author: FrickTown (https://github.com/FrickTown/)
"""
from main import TerminalSpace, Wave, Graphspace
import math

def addWaves(term: TerminalSpace):
    # Create a new graphspace in terminalspace "term", 
    # with width and height of the terminal (height -1 to avoid terminal scrolling when printing the last line), 
    # with an xRange of -10 to 10 and an yRange of -10 to 10, 
    # and with a resolution of (2^5 = 32) points per cell. 
    term.addGraphspace(Graphspace(term, term.width, term.height-1, 15, 10, 5))

    # Create a new wave in the TerminalSpace term's first GraphSpace,
    # with the function "math.sin(x - shift) * (amp * math.sin(aMod))",
    # with the color "aqua",
    # supplying the three custom variable that are referenced in the function string as a dictionary
    term.graphspaces[0].addWave(Wave("math.sin(x - shift) * (amp * math.sin(aMod))", term.aqua, {
        "shift": {"value": 0.5 * math.pi, "incr": math.pi/30}, 
        "amp": {"value": 5, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/50}
        }))
    term.graphspaces[0].addWave(Wave("math.sin(x + shift) * (amp * math.sin(aMod))", term.bright_yellow, {
        "shift": {"value": math.pi, "incr": math.pi/15}, 
        "amp": {"value": 7, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/100}
        }))
    # Very cool wave form that incrases in amplitude from x, but also is also dependent on a sine function.
    term.graphspaces[0].addWave(Wave("math.sin(x + (math.sin(shift))) * (amp * math.sin(aMod + x) * x)", term.bright_red, {
        "shift": {"value": math.pi, "incr": math.pi/45}, 
        "amp": {"value": 1, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/30}
        }))
    
    # Previous wave but shifted one period
    term.graphspaces[0].addWave(Wave("math.sin(x + (math.sin(shift)) + math.pi) * (amp * math.sin(aMod + x) * x)", term.slateblue, {
        "shift": {"value": math.pi, "incr": math.pi/45}, 
        "amp": {"value": 1, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/30}
        }, visible=False))
    
    # Tan wave demo
    term.graphspaces[0].addWave(Wave("math.tan(x + shift)", term.bright_magenta, {
        "shift": {"value": math.pi, "incr": math.pi/45},
        }, visible=False))

    # Constant function demo
    term.graphspaces[0].addWave(Wave("x * x", term.bright_green, {
        "radius": {"value": 5, "incr": 0},
        }, visible=False))