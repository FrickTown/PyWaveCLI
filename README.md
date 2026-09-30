# PyWaveCLI

<img width="940" height="658" alt="pwdemo" src="https://github.com/user-attachments/assets/96292a96-2558-40d2-a244-9fb8e68bc53f" />

PyWaveCLI is a Python-based CLI application that allows for mathematical plotting in the terminal. The application can draw curves for any function in the x/y plane. 
Predefine functions in a file, or add your own functions and variables on the fly using the built in [TUI](https://en.wikipedia.org/wiki/Text-based_user_interface). 

## Requirements
- Python
- PyWaveCLI depends on [**Blessed**](https://pypi.org/project/blessed/), which you can install with the command

      pip install blessed

- The terminal emulator [**Alacritty**](https://alacritty.org/) is highly recommended due to its formidable speed.

## Running
Clone this repo with:

    git clone https://github.com/FrickTown/PyWaveCLI/ && cd PyWaveCLI
After this you can run the program with

    python main.py

To edit the example waves, take a look at the `example.py` module.
A wave can be added by copying one of the lines preceeding with `term.graphspaces[0].addWave` and modifying it.
If you wish to understand further, I've documented the code a little bit to help you.

## Usage
### Adding a new function during runtime
Open the menu **[M]** and either create a new wave **[N]**, or use the arrow keys **[Up/Down]** to select and duplicate an existing wave **[D]** to edit **[E]** later. Set its (RGB) color with **[C]**.

### Adding variables
If you want your function to contain custom variables, you need to define the variables before you can refer to them in the function.

Create a new temporary function with **[N]** (you can leave it as x), select it with the arrow keys **[Up/Down]** and press **[Enter]**. This will show you the *custom variables* submenu. Here, you can define any variables you would like by pressing **[N]**. After you have defined a variable and it is selected in the *custom variables* submenu, press **[Enter]** to open the variable's submenu. Here, you can set a fixed value, or an amount with which to increase the variable's value every rendered frame. 

<img width="1690" height="434" alt="image" src="https://github.com/user-attachments/assets/17c9208e-1b39-497e-bc0e-b8e2fa2ee7f8" />

### Using math methods and constants
This program uses python's eval function, with python's standard math library imported. This means that any constant or function from the standard math library is supported. The example waves demonstrates this by making use of `math.pi` and `math.sin()`. 

### Modifying the viewport
At the top of the window, there are instructions for how to "zoom" in or out in the X or the Y direction by using **[+/-]** for the x-axis, and **[?/_]** for the y-axis. (The key bindings are based on the Nordic keyboard layout).

Additionally, you can adjust the *PPC* or the *points per cell* value, essentially the resolution of the curve. Decrease the value with **[K]**, increase the value with **[L]**. Use **[Shift]** to adjust it in smaller steps. 

##  Troubleshooting
### IndexError: list assignment index out of range
If you see this error when trying to run the program, **widen your terminal window**.
The application needs a minimum of **85** columns to start, and **152** columns to render the user interface properly. Handling this without crashing is a future addition.

## Special thanks:
- Blessed
- Alacritty
- StackOverflow user ***Ohan*** for his answer on [how to speed up the eval function](https://stackoverflow.com/questions/12467570/python-way-to-speed-up-a-repeatedly-executed-eval-statement#answers)
