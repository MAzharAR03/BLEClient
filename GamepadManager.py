import json

import vgamepad as vg

from ReadFile import read_file
from Mapper import apply_control

class GamepadManager:
    def __init__(self, config_path = "config.json"):
        self.gamepad = vg.VX360Gamepad()
        self.mapping = json.loads(read_file(config_path))

    def update_state(self, input_json):
        try:
            state = json.loads(input_json)
        except json.decoder.JSONDecodeError:
            return

        #Make a flat dictionary for easy lookup, State dictionary has buttons in an array, looping through an array every time is inefficient
        inputs = {}
        for button in state.get("buttons", []):
            inputs[f"toggle:{button['name']}"] = button["pressed"]
        inputs["toggle:stepping"] = True if state.get("stepping") else False
        inputs["float:pitch"] = state.get("pitch",0.0)

        #Search for left and right joysticks in mapping configuration
        #Get value of x and y through user-defined or from sensor data
        for side in ("left","right"):
            joystick_cfg = self.mapping.get(f"{side}_joystick")
            if not joystick_cfg:
                continue
            x = self.resolve_input(joystick_cfg.get("x"), inputs) or 0.0
            y = self.resolve_input(joystick_cfg.get("y"), inputs) or 0.0
            apply_control(self.gamepad, f"{side}_joystick", x=x, y=y)

        #Search for left and right trigger joysticks in mapping configuration
        #Get value of press through user-defined value.
        for side in ("left", "right"):
            trigger_cfg = self.mapping.get(f"{side}_trigger")
            if not trigger_cfg:
                continue
            value = self.resolve_input(trigger_cfg,inputs) or 0.0
            apply_control(self.gamepad,f"{side}_trigger", value = value)

        #Remaining buttons, get button state and apply gamepad control
        for action_name, button_cfg in self.mapping.items():
            if action_name.endswith("_joystick") or action_name.endswith("_trigger"):
                continue
            if not button_cfg:
                continue
            if isinstance(button_cfg, list):
                pressed = any(inputs.get(cfg["input"]) for cfg in button_cfg)
            else:
                input_key = button_cfg["input"]
                pressed = bool(inputs.get(input_key))
            if pressed is not None:
                apply_control(self.gamepad, action_name, pressed=bool(pressed))
        self.gamepad.update()

    def resolve_input(self, mapping, inputs):
        if isinstance(mapping, list):
            return sum(self.resolve_input(m, inputs) or 0.0 for m in
                       mapping)  # loop through all inputs in the mapped action and sum up

        if mapping is None:
            return None

        raw = inputs.get(mapping["input"])
        if raw is None:
            return None

        if mapping["input"].startswith("toggle:"):
            return mapping.get("value", 1.0) if raw else 0.0
        else:
            scale = mapping.get("scale", 1.0)
            return -float(raw) / scale