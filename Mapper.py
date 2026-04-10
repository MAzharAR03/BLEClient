import vgamepad as vg

gamepadActions = {
    "left_joystick": lambda gamepad, x, y: gamepad.left_joystick_float(x_value_float=x, y_value_float=y),
    "right_joystick": lambda gamepad, x, y: gamepad.right(x_value_float=x, y_value_float=y),
    "right_trigger": lambda gamepad, value: gamepad.right_trigger(value),
    "left_trigger": lambda gamepad, value: gamepad.left_trigger(value),
    "dpad_up": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
    "dpad_down": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
    "dpad_left": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
    "dpad_right": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
    "X": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_X),
    "Y":lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_Y),
    "B": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_B),
    "A": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_A),
    "start": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_START),
    "back": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK),
    "left_thumb": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB),
    "right_thumb": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB),
    "left_shoulder": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER),
    "right_shoulder": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER),
    "guide": lambda gamepad: gamepad.press_button(button = vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE),
}

#Need the lambda to have same amount of parameters other wise conflict, (joystick and buttons)
#If remove the x,y values, then cant control the joystick using pitch.