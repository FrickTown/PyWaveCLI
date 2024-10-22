# PyWaveCLI

![image](https://github.com/user-attachments/assets/17feb435-fa80-4fff-9181-1e25e11e4dcb)


PyWaveCLI is a python-based CLI application that allows for mathematical plotting in the terminal.
It is stable and functional but currently under very heavy development. All one-variable continuous functions seem to be working.

## Requirements
- PyWaveCLI depends on [**Blessed**](https://pypi.org/project/blessed/), which you can install with the command

      pip install blessed

- The terminal emulator [**Alacritty**](https://alacritty.org/) is highly recommended due to its formidable speed.

- Additionally, I do also recommend that you set your **terminal's cursor color to be the same as the background color**. This is in order to avoid a lot of flickering that comes with rendering across the cells so rapidly. I've achieved this in Alacritty by modifying the config file `~/.alacritty.toml` as follows:
```toml
[colors]
cursor = { text = "CellBackground", cursor = "CellBackground" }
```

## Usage
Clone this repo with:

    git clone https://github.com/FrickTown/PyWaveCLI/ && cd PyWaveCLI
After this you can run the program with

    python main.py

To edit the example waves, take a look at the `example.py` module.
A wave can be added by copying one of the lines preceeding with `term.graphspaces[0].addWave` and modifying it.
If you wish to understand further, I've documented the code a little bit to help you.
### TODO: Add more detailed information

## Special thanks:
- Blessed
- Alacritty
- StackOverflow user ***Ohan*** for his answer on [how to speed up the eval function](https://stackoverflow.com/questions/12467570/python-way-to-speed-up-a-repeatedly-executed-eval-statement#answers)
