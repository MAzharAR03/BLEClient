from XboxDictionary import XBOX_CONTROLS, JOYSTICK_KEYS, ALWAYS_AVAILABLE, FLOAT_INPUTS


def get_android_inputs(layout: dict) -> list[str]:
    inputs = list(ALWAYS_AVAILABLE)
    for btn in layout.get("buttons", []):
        name = btn.get("text", "").strip()
        if name and btn.get("type") not in ("pause", "screenshot"):
            key = f"toggle:{name}"
            if key not in inputs:
                inputs.append(key)
    # float inputs always available
    for fi in FLOAT_INPUTS:
        if fi not in inputs:
            inputs.append(fi)
    return inputs


def config_to_rows(config: dict) -> dict:
    rows = {}
    for key, _label, _slot_type, _group in XBOX_CONTROLS:
        rows[key] = []

    def parse_entry(entry) -> dict:
        if entry is None:
            return None
        inp = entry.get("input", "")
        return {
            "input": inp,
            "scale": entry.get("scale", None),
            "value": entry.get("value", None),
        }

    for key, _label, _slot_type, _group in XBOX_CONTROLS:
        if key in JOYSTICK_KEYS:
            continue  # handled separately

        raw = config.get(key)
        if raw is None:
            continue
        if isinstance(raw, list):
            rows[key] = [parse_entry(e) for e in raw if e]
        else:
            rows[key] = [parse_entry(raw)]

    # Joystick axes stored under left_joystick / right_joystick
    for side in ("left", "right"):
        cfg = config.get(f"{side}_joystick")
        if not cfg:
            continue
        for axis in ("x", "y"):
            raw = cfg.get(axis)
            if not raw:
                continue
            key = f"{side}_joystick_{axis}"
            if isinstance(raw, list):
                rows[key] = [parse_entry(e) for e in raw if e]
            else:
                rows[key] = [parse_entry(raw)]

    return rows


def rows_to_config(rows: dict) -> dict:
    config = {}

    def serialize_chip(chip):
        d = {"input": chip["input"]}
        if chip.get("scale") is not None:
            d["scale"] = chip["scale"]
        if chip.get("value") is not None:
            d["value"] = chip["value"]
        return d

    def serialize_chips(chips):
        if not chips:
            return None
        serialized = [serialize_chip(c) for c in chips]
        if len(serialized) == 1:
            return serialized[0]
        return serialized

    for key, _label, slot_type, _group in XBOX_CONTROLS:
        if key in JOYSTICK_KEYS:
            continue
        config[key] = serialize_chips(rows.get(key, []))

    # Rebuild joystick entries
    for side in ("left", "right"):
        jcfg = {}
        for axis in ("x", "y"):
            k = f"{side}_joystick_{axis}"
            jcfg[axis] = serialize_chips(rows.get(k, []))
        config[f"{side}_joystick"] = jcfg

    return config