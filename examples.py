from main import TerminalSpace, Wave, Graphspace
import math

def addWaves(term: TerminalSpace):
    term.addGraphspace(Graphspace(term, term.width, term.height-1, 10, 10, 1/16))

    term.graphspaces[0].addWave(Wave("math.sin(x - shift) * (amp * math.sin(aMod))", term.aqua, {
        "shift": {"value": 0.5 * math.pi, "incr": math.pi/30}, 
        "amp": {"value": 5, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/100}
        }))
    term.graphspaces[0].addWave(Wave("math.sin(x + shift) * (amp * math.sin(aMod))", term.bright_yellow, {
        "shift": {"value": math.pi, "incr": math.pi/30}, 
        "amp": {"value": 7, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/100}
        }))
    term.graphspaces[0].addWave(Wave("math.sin(x + shift) * (amp * math.sin(aMod))", term.bright_red, {
        "shift": {"value": math.pi, "incr": math.pi/45}, 
        "amp": {"value": 2, "incr": 0},
        "aMod": {"value": 0, "incr": math.pi/100}
        }))