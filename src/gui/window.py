import PySimpleGUI as sg


class Switches:
    TITLE = 'Switches'
    TARGER = 'Target'
    LOOT = 'Loot'
    COMBO = 'Combo'


class Say:
    TITLE = 'Say'
    INPUT_KEY = '-SAY-'
    BUTTON = 'Submit text'


class Logs:
    TITLE = 'Logs'
    OUTPUT_KEY = '-LOG-'


switches_column = [
    [sg.Text(Switches.TITLE)],
    [sg.Button(Switches.TARGER, size=(6, 1))],
    [sg.Button(Switches.LOOT, size=(6, 1))],
    [sg.Button(Switches.COMBO, size=(6, 1))],
]

say_column = [
    [sg.Text(Say.TITLE), sg.Input(size=(24, 1), key=Say.INPUT_KEY)],
    # [sg.Input(size=(20, 1), key=Say.INPUT_KEY)],
    [sg.Button(Say.BUTTON, visible=False, bind_return_key=True)],
    # [sg.HSeparator],
    [sg.Text(Logs.TITLE)],
    [sg.Multiline(size=(30, 4), key=Logs.OUTPUT_KEY, no_scrollbar=True)],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(switches_column),
        sg.VSeperator(),
        sg.Column(say_column),
    ]
]

# Create the window
window = sg.Window("RBot", layout, keep_on_top=True)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break
    if event == Say.BUTTON:
        inp = values[Say.INPUT_KEY]
        print(inp)
        window[Say.INPUT_KEY].update('')
        window[Logs.OUTPUT_KEY].update(inp)

window.close()
