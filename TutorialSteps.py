def get_main_window_steps(ui):
    return [
        (ui.scan_button,         "Scan for Devices",    "Click to discover nearby BLE devices. Make sure Bluetooth is on."),
        (ui.device_list,         "Device List",         "Found devices appear here."),
        (ui.connect_button,      "Connect",             "Connects to the selected device."),
        (ui.send_file_button,    "Send Layout File",    "Sends a JSON button-layout file to the connected phone. Layout files can be created in the UI builder"),
        (ui.builder_button,      "UI Builder",          "Opens the drag-and-drop layout editor to design phone button layouts."),
        (ui.trail_group, "GPX Generation", "This section is used for random trail generation for apps such as Strava. "),
        (ui.map_view,            "Trail Map",           "Click on the map to drop a destination pin before starting a trail."),
        (ui.start_trail_button,  "Start Trail",         "Begins recording a GPX trail from the pinned start point."),
        (ui.stop_trail_button,   "Stop & Save Trail",   "Ends recording and prompts you to save the trail as a .gpx file."),
        (ui.emulation_toggle,    "Xbox Emulation",      "Toggle virtual Xbox controller emulation on or off. If playing a game that is using the API, it is recommended not to use this settings as the two inputs may conflict with each other."),
        (ui.config_mapper_button,"Config Mapper",       "Configure the mapping of android inputs to Xbox controller inputs. "),
        (ui.monitor_dropdown,    "Monitor Select",      "Choose which monitor is captured for screenshot actions."),
    ]