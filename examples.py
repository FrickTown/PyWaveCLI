from main import TerminalSpace, Wave, Graphspace
import math

def addWaves(term: TerminalSpace):
    # Create a new graphspace in terminalspace "term", 
    # with width and height of the terminal (height -1 to avoid terminal having to scroll for), 
    # with an xRange of -10 to 10 and an yRange of -10 to 10, 
    # and with a resolution of 32 points per cell (Should always be power of twos i.e. (1/2^n) )
    term.addGraphspace(Graphspace(term, term.width, term.height, 10, 10, 1/32))

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
        "shift": {"value": math.pi, "incr": math.pi/30}, 
        "amp": {"value": 7, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/100}
        }))
    term.graphspaces[0].addWave(Wave("math.sin(x + shift) * (amp * math.sin(aMod))", term.bright_red, {
        "shift": {"value": math.pi, "incr": math.pi/45}, 
        "amp": {"value": 2, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/25}
        }))