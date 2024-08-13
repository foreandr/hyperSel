import builtins
import inspect

colors = {
    "reset": "\033[0m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    "black": "\033[30m",
    "bright_black": "\033[90m",
    "grey": "\033[90m",
    "dark_grey": "\033[90m",
    "light_red": "\033[91m",
    "light_green": "\033[92m",
    "light_yellow": "\033[93m",
    "light_blue": "\033[94m",
    "light_magenta": "\033[95m",
    "light_cyan": "\033[96m",
    "light_white": "\033[97m",
    "background_black": "\033[40m",
    "background_red": "\033[41m",
    "background_green": "\033[42m",
    "background_yellow": "\033[43m",
    "background_blue": "\033[44m",
    "background_magenta": "\033[45m",
    "background_cyan": "\033[46m",
    "background_white": "\033[47m",
    "background_bright_black": "\033[100m",
    "background_bright_red": "\033[101m",
    "background_bright_green": "\033[102m",
    "background_bright_yellow": "\033[103m",
    "background_bright_blue": "\033[104m",
    "background_bright_magenta": "\033[105m",
    "background_bright_cyan": "\033[106m",
    "background_bright_white": "\033[107m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "reverse": "\033[7m",
    "hidden": "\033[8m",
    "strikethrough": "\033[9m",
    "reset_bold": "\033[21m",
    "reset_dim": "\033[22m",
    "reset_underline": "\033[24m",
    "reset_blink": "\033[25m",
    "reset_reverse": "\033[27m",
    "reset_hidden": "\033[28m",
    "reset_strikethrough": "\033[29m",
}

def c_print(text, color="white"):
    text = str(text)
    # Get the name of the calling function
    caller_function_name = inspect.stack()[1].function
    
    if isinstance(text, list):
        if isinstance(color, list):
            if len(color) != len(text):
                raise ValueError("Length of color list must match length of text list.")
            for t, c in zip(text, color):
                color_code = colors.get(c, colors["white"])
                builtins.print(f"{color_code}{caller_function_name}: {t}{colors['white']}", end="")
            builtins.print()  # Print a newline after all items
        else:
            color_code = colors.get(color, colors["white"])
            for t in text:
                builtins.print(f"{color_code}{caller_function_name}: {t}{colors['white']}", end="")
            builtins.print()  # Print a newline after all items
    else:
        color_code = colors.get(color, colors["white"])
        builtins.print(f"{color_code}{caller_function_name}: {text}{colors['white']}")