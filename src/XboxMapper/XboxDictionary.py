XBOX_CONTROLS = [
    # (config_key, display_label, slot_type, group)
    ("A",               "A",        "button",  "Face Buttons"),
    ("B",               "B",        "button",  "Face Buttons"),
    ("X",               "X",        "button",  "Face Buttons"),
    ("Y",               "Y",        "button",  "Face Buttons"),
    ("left_shoulder",   "LB",       "button",  "Shoulder & Trigger"),
    ("right_shoulder",  "RB",       "button",  "Shoulder & Trigger"),
    ("left_trigger",    "LT",       "trigger", "Shoulder & Trigger"),
    ("right_trigger",   "RT",       "trigger", "Shoulder & Trigger"),
    ("dpad_up",         "↑",        "button",  "D-Pad"),
    ("dpad_down",       "↓",        "button",  "D-Pad"),
    ("dpad_left",       "←",        "button",  "D-Pad"),
    ("dpad_right",      "→",        "button",  "D-Pad"),
    ("left_joystick_x", "Left X",   "axis",    "Left Joystick"),
    ("left_joystick_y", "Left Y",   "axis",    "Left Joystick"),
    ("right_joystick_x","Right X",  "axis",    "Right Joystick"),
    ("right_joystick_y","Right Y",  "axis",    "Right Joystick"),
    ("start",           "Start",    "button",  "System"),
    ("back",            "Back",     "button",  "System"),
]

JOYSTICK_KEYS = {"left_joystick_x", "left_joystick_y",
                 "right_joystick_x", "right_joystick_y"}

FLOAT_INPUTS = ["float:pitch"]
ALWAYS_AVAILABLE = ["toggle:stepping","toggle:pause"]