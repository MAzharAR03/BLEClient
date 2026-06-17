def get_main_window_steps(ui):
    return [
        (ui.scan_button,         "Scan for Devices",    "Click to discover nearby BLE devices. Make sure Bluetooth is on."),
        (ui.device_list,         "Device List",         "Found devices appear here."),
        (ui.connect_button,      "Connect",             "Connects to the selected device."),
        (ui.send_file_button,    "Send Layout File",    "Sends a JSON button-layout file to the connected phone. Layout files can be created in the UI builder"),
        (ui.builder_button,      "UI Builder",          "Opens the drag-and-drop layout editor to design phone button layouts."),
        (ui.trail_group, "GPX Generation", "This section is used for random trail generation for apps such as Strava. "),
        (ui.map_view,            "Trail Map",           "Click on the map to drop a start pin before starting a trail."),
        (ui.start_trail_button,  "Start Trail",         "Begins recording a GPX trail from the pinned start point."),
        (ui.stop_trail_button,   "Stop & Save Trail",   "Ends recording and prompts you to save the trail as a .gpx file."),
        (ui.emulation_toggle,    "Xbox Emulation",      "Toggle virtual Xbox controller emulation on or off. If playing a game that is using the API, it is recommended not to use this settings as the two inputs may conflict with each other."),
        (ui.monitor_dropdown,    "Monitor Select",      "Choose which monitor is captured for screenshot actions."),
    ]

def get_config_mapper_steps(ui):
    return [
        (ui._toolbar_buttons["Load Layout"], "Load Button Layout", "Load the desired Android button layout first. This allows you to see which inputs are available."),
        (ui._toolbar_buttons["Load Config"], "Load Mapping Config", "If you have stored mappings, you can load them with this button."),
        (ui._toolbar_buttons["Export Config"], "Export Mapping Config", "This button will save the mapping to config.json. In the future, the server will allow for saving and using multiple different mapping configs."),
        (ui._content, "Mapping Zone", "Clicked the + Add button to map an Android input (e.g button or stepping) to the selected Xbox input. Tilting can only be mapped to Joystick controls.")
    ]

def get_ui_builder_steps(ui):
    return [
        (ui._save_btn, "Save Layout", "Save a layout file into JSON format"),
        (ui._load_btn, "Load Layout", "Load a layout file in JSON format to begin editing or start from scratch."),
        (ui._add_btn, "Add a button", "Add a brand new button into the screen"),
        (ui._delete_btn, "Delete Selected Button", "Delete the selected button"),
        (ui._screenshot_btn, "Add the Special Screenshot button", "This adds the special button: Screenshot to your layout. This button's text cannot be edited. This button will tell the PC server to save a screenshot."),
        (ui._pause_btn, "Add the Special Pause Button", "This adds the special button: Pause to your layout. This button's text cannot be edited. This button will tell the PC server to pause."),
        (ui._image_btn, "Add an Image", "Add an image by providing a downloadable URL"),
        (ui._bg_btn, "Add Background Image", "Add Background image by providing a downloadable URL"),
        (ui._mapper_btn, "Open Xbox Mapper", "Configure the mapping of android inputs to Xbox controller inputs."),
        (ui._replay_btn, "Replay Tutorial", "Replay the tutorial by clicking this button whenever you wish."),
    ]