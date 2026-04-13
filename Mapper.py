import vgamepad as vg
from enum import Enum


#Gamepad controls are split into 3, as these options all take different parameters to control
class ActionType(Enum):
    BUTTON = "button"
    TRIGGER = "trigger"
    JOYSTICK = "joystick"

#Dictionary containing all possible gamepad controls
GAMEPAD_ACTIONS = {
    "A" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_A),
    "B" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_B),
    "X" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_X),
    "Y" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_Y),
    "start" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_START),
    "back"  : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK),
    "dpad_up" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
    "dpad_left" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
    "dpad_down" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
    "dpad_right" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
    "left_shoulder" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER),
    "right_shoulder" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER),
    "left_thumb" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB),
    "right_thumb" : (ActionType.BUTTON, vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB),

    "left_trigger" : (ActionType.TRIGGER, "left"),
    "right_trigger" : (ActionType.TRIGGER, "right"),

    "left_joystick" : (ActionType.JOYSTICK, "left"),
    "right_joystick" : (ActionType.JOYSTICK, "right"),

}

def resolve_input(self, mapping, inputs):
    if mapping is None:
        return None

    raw = inputs.get(mapping["input"])
    if raw is None:
        return None


# Future, allow for control of which x or y float to add to
def apply_control(gamepad,
                  action_name: str,
                  pressed: bool = False,
                  value: float = 0,
                  x: float = 0,
                  y: float = 0,):
    control = GAMEPAD_ACTIONS.get(action_name)
    if not control: return

    action_type, target = control

    if action_type == ActionType.BUTTON:
        if pressed:
            gamepad.press_button(button = target)
        else:
            gamepad.release_button(button = target)

    elif action_type == ActionType.TRIGGER:
        if target == "left":
            gamepad.left_trigger_float(value_float = value)
        else:
            gamepad.right_trigger_float(value_float = value)

    elif action_type == ActionType.JOYSTICK:
        if target == "left":
            gamepad.left_joystick_float(x_value_float = x, y_value_float = y)
        else:
            gamepad.right_joystick_float(x_value_float = x, y_value_float= y)
