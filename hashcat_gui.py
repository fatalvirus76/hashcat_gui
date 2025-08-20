import sys
import os
import json
import subprocess
import re
import platform
import shlex

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
    QTextEdit, QTabWidget, QSpinBox, QCheckBox, QFormLayout,
    QGroupBox, QScrollArea, QMessageBox, QCompleter, QDialog,
    QListWidget, QListWidgetItem, QDialogButtonBox, QMenuBar, QProgressBar
)
from PySide6.QtCore import Qt, QSettings, QProcess
from PySide6.QtGui import QTextCursor, QAction, QActionGroup

# =============================================================================
# Configuration Data
# =============================================================================

# Attack Modes (-a)
ATTACK_MODES = {
    "0 - Straight": 0,
    "1 - Combination": 1,
    "3 - Brute-force": 3,
    "6 - Hybrid Wordlist + Mask": 6,
    "7 - Hybrid Mask + Wordlist": 7,
    "9 - Association": 9,
}

# Workload Profiles (-w)
WORKLOAD_PROFILES = {
    "1 - Low": 1,
    "2 - Default": 2,
    "3 - High": 3,
    "4 - Nightmare": 4,
}

# Hash modes that use specific parameters
WPA_HASH_MODES = [2500, 2501, 22000, 22001]
VERACRYPT_HASH_MODES = [13711, 13712, 13713, 13721, 13722, 13723, 13731, 13732, 13733, 13741, 13742, 13743, 13751, 13752, 13753, 13761, 13762, 13763]


# Theme Stylesheets (QSS) with new button colors
THEMES = {
    "Light": """
        QMainWindow { background-color: #f0f0f0; }
        QWidget { background-color: #f0f0f0; color: #333; }
        QGroupBox { border: 1px solid #ccc; margin-top: 10px; background-color: #f8f8f8; border-radius: 5px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; background-color: #f0f0f0;}
        QLineEdit, QSpinBox, QComboBox { background-color: white; border: 1px solid #ccc; padding: 4px; border-radius: 3px; }
        QPushButton { background-color: #e0e0e0; border: 1px solid #ccc; padding: 5px 10px; border-radius: 3px; }
        QPushButton:hover { background-color: #d0d0d0; }
        QPushButton:pressed { background-color: #c0c0c0; }
        QPushButton#runButton { background-color: #28a745; border-color: #228b3a; color: white; }
        QPushButton#runButton:hover { background-color: #218838; }
        QPushButton#stopButton { background-color: #dc3545; border-color: #b02a37; color: white; }
        QPushButton#stopButton:hover { background-color: #c82333; }
        QTextEdit { background-color: white; border: 1px solid #ccc; color: #333; border-radius: 3px; }
        QTabWidget::pane { border-top: 1px solid #ccc; }
        QTabBar::tab { background: #e0e0e0; border: 1px solid #ccc; padding: 6px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: #f0f0f0; border-bottom-color: #f0f0f0; }
        QMenuBar { background-color: #e0e0e0; }
        QMenu { background-color: #f0f0f0; border: 1px solid #ccc; }
        QMenu::item:selected { background-color: #0078d7; color: white; }
        QProgressBar { border: 1px solid #ccc; border-radius: 3px; text-align: center; background-color: white;}
        QProgressBar::chunk { background-color: #0078d7; }
    """,
    "Dark": """
        QMainWindow { background-color: #2e2e2e; }
        QWidget { background-color: #2e2e2e; color: #e0e0e0; }
        QGroupBox { border: 1px solid #444; margin-top: 10px; background-color: #383838; border-radius: 5px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; background-color: #2e2e2e;}
        QLineEdit, QSpinBox, QComboBox { background-color: #3c3c3c; border: 1px solid #555; padding: 4px; color: #e0e0e0; border-radius: 3px; }
        QLineEdit:read-only { background-color: #333; }
        QPushButton { background-color: #4a4a4a; border: 1px solid #555; padding: 5px 10px; color: #e0e0e0; border-radius: 3px; }
        QPushButton:hover { background-color: #5a5a5a; }
        QPushButton:pressed { background-color: #6a6a6a; }
        QPushButton#runButton { background-color: #28a745; border-color: #34c759; color: white; }
        QPushButton#runButton:hover { background-color: #218838; }
        QPushButton#stopButton { background-color: #dc3545; border-color: #ff453a; color: white; }
        QPushButton#stopButton:hover { background-color: #c82333; }
        QTextEdit { background-color: #252525; border: 1px solid #555; color: #e0e0e0; border-radius: 3px; }
        QTabWidget::pane { border-top: 1px solid #444; }
        QTabBar::tab { background: #3c3c3c; border: 1px solid #444; padding: 6px; color: #e0e0e0; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: #2e2e2e; border-bottom-color: #2e2e2e; }
        QMenuBar { background-color: #3c3c3c; color: #e0e0e0;}
        QMenu { background-color: #3c3c3c; border: 1px solid #555; color: #e0e0e0;}
        QMenu::item:selected { background-color: #0078d7; color: white; }
        QProgressBar { color: #e0e0e0; border: 1px solid #555; border-radius: 3px; text-align: center; background-color: #3c3c3c;}
        QProgressBar::chunk { background-color: #0078d7; border-radius: 2px;}
    """,
    "Dracula": """
        QWidget { background-color: #282a36; color: #f8f8f2; selection-background-color: #44475a; }
        QGroupBox { border: 1px solid #44475a; margin-top: 10px; background-color: #2f3240; border-radius: 5px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; color: #bd93f9; }
        QLineEdit, QSpinBox, QComboBox, QTextEdit { background-color: #21222c; border: 1px solid #44475a; padding: 4px; border-radius: 3px; }
        QPushButton { background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; padding: 5px 10px; border-radius: 3px; }
        QPushButton:hover { background-color: #515568; }
        QPushButton:pressed { background-color: #6272a4; }
        QPushButton#runButton { background-color: #50fa7b; border-color: #50fa7b; color: #282a36; }
        QPushButton#runButton:hover { background-color: #61fc8c; }
        QPushButton#stopButton { background-color: #ff5555; border-color: #ff5555; color: #282a36; }
        QPushButton#stopButton:hover { background-color: #ff6e67; }
        QTabBar::tab { background: #2f3240; border: 1px solid #44475a; padding: 6px; color: #f8f8f2; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: #282a36; color: #bd93f9; border-bottom-color: #282a36; }
        QTabWidget::pane { border-top: 1px solid #44475a; }
        QMenuBar { background-color: #21222c; color: #f8f8f2; }
        QMenu { background-color: #2f3240; border: 1px solid #44475a; }
        QMenu::item:selected { background-color: #6272a4; }
        QProgressBar { color: #f8f8f2; border: 1px solid #44475a; border-radius: 3px; text-align: center; background-color: #21222c;}
        QProgressBar::chunk { background-color: #ff79c6; border-radius: 2px;}
    """,
    "Synthwave": """
        QWidget { background-color: #2a2139; color: #f6d5a2; font-family: "Lucida Console", "Courier New", monospace; }
        QGroupBox { border: 1px solid #ff7ac6; margin-top: 10px; background-color: #322844; border-radius: 5px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; color: #ff7ac6; }
        QLineEdit, QSpinBox, QComboBox, QTextEdit { background-color: #241c31; border: 1px solid #72f1b8; padding: 4px; border-radius: 3px; color: #f4eee3; }
        QPushButton { background-color: #322844; color: #72f1b8; border: 1px solid #ff7ac6; padding: 5px 10px; border-radius: 3px; }
        QPushButton:hover { background-color: #41355a; }
        QPushButton:pressed { border-color: #72f1b8; }
        QPushButton#runButton { background-color: #00f5d4; border-color: #00f5d4; color: #2a2139; }
        QPushButton#runButton:hover { background-color: #33f7da; }
        QPushButton#stopButton { background-color: #ff42b3; border-color: #ff42b3; color: #2a2139; }
        QPushButton#stopButton:hover { background-color: #ff66c3; }
        QTabBar::tab { background: #322844; border: 1px solid #ff7ac6; padding: 6px; color: #f6d5a2; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: #2a2139; color: #ff7ac6; border-bottom-color: #2a2139; }
        QTabWidget::pane { border-top: 1px solid #ff7ac6; }
        QMenuBar { background-color: #241c31; color: #f6d5a2; }
        QMenu { background-color: #322844; border: 1px solid #ff7ac6; }
        QMenu::item:selected { background-color: #ff7ac6; color: #2a2139; }
        QProgressBar { color: #f4eee3; border: 1px solid #72f1b8; border-radius: 3px; text-align: center; background-color: #241c31;}
        QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7ac6, stop:1 #72f1b8); border-radius: 2px;}
    """,
    "Matrix": """
        QWidget { background-color: black; color: #00FF00; selection-background-color: #008800; font-family: "Monospace", "Courier New"; }
        QGroupBox { border: 1px solid #00AA00; margin-top: 10px; background-color: #050505; border-radius: 0px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; color: #00FF00; }
        QLineEdit, QSpinBox, QComboBox, QTextEdit { background-color: #0A0A0A; color: #00FF00; border: 1px solid #00AA00; padding: 4px; border-radius: 0px; }
        QPushButton { background-color: #0F0F0F; color: #00FF00; border: 1px solid #00AA00; padding: 5px 10px; border-radius: 0px; }
        QPushButton:hover { background-color: #002200; }
        QPushButton:pressed { background-color: #003300; }
        QPushButton#runButton { background-color: #004d00; border-color: #00ff00; }
        QPushButton#runButton:hover { background-color: #006600; }
        QPushButton#stopButton { background-color: #660000; border-color: #ff0000; }
        QPushButton#stopButton:hover { background-color: #8b0000; }
        QTabBar::tab { background: #0A0A0A; color: #00FF00; border: 1px solid #00AA00; padding: 6px; border-radius: 0px; }
        QTabBar::tab:selected { background: black; border-bottom: 1px solid black; }
        QTabWidget::pane { border-top: 1px solid #00AA00; }
        QMenuBar { background-color: black; color: #00FF00; }
        QMenu { background-color: black; border: 1px solid #00AA00; }
        QMenu::item:selected { background-color: #008800; color: black; }
        QSpinBox::up-button, QSpinBox::down-button { border: 1px solid #00AA00; background-color: #0A0A0A; }
        QComboBox::down-arrow { image: none; }
        QProgressBar { color: #00FF00; border: 1px solid #00AA00; border-radius: 0px; text-align: center; background-color: #0A0A0A;}
        QProgressBar::chunk { background-color: #00AA00; }
    """
}

# =============================================================================
# Main Application Class
# =============================================================================

class HashcatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hashcat GUI v2.3.1")
        self.setGeometry(100, 100, 1000, 850)

        # --- Instance Variables ---
        self.controls = {}
        self.HASH_MODES = {}
        self.command_history = []
        self.MAX_HISTORY_ITEMS = 20
        self.settings = QSettings("MyCompany", "HashcatGUI_v2.3")
        self.process = None

        # --- UI Initialization ---
        self._create_menu_bar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # --- Corrected initialization flow ---
        self._create_path_widgets()
        self._create_tabs()
        self._create_command_output_widgets()
        self._create_control_buttons()

        self.load_hashcat_path() 
        self._parse_and_populate_hash_modes(silent_on_error=True)

        self._load_theme()
        self.update_contextual_widgets()
        self.display_command()

    # -------------------------------------------------------------------------
    # UI Creation Methods
    # -------------------------------------------------------------------------

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        save_action = QAction("&Save Profile...", self); save_action.triggered.connect(self.save_settings_dialog); file_menu.addAction(save_action)
        load_action = QAction("&Load Profile...", self); load_action.triggered.connect(self.load_settings_dialog); file_menu.addAction(load_action)
        file_menu.addSeparator()
        exit_action = QAction("&Exit", self); exit_action.triggered.connect(self.close); file_menu.addAction(exit_action)
        view_menu = menu_bar.addMenu("&View")
        theme_menu = view_menu.addMenu("&Themes")
        self.theme_action_group = QActionGroup(self); self.theme_action_group.setExclusive(True)
        self.theme_actions = {}
        # Translate theme names for the menu
        theme_map = {"Ljust": "Light", "Mörkt": "Dark"}
        for theme_name in THEMES.keys():
            display_name = theme_map.get(theme_name, theme_name)
            action = QAction(display_name, self, checkable=True)
            action.triggered.connect(lambda checked=False, name=theme_name: self.apply_theme(name))
            self.theme_action_group.addAction(action); theme_menu.addAction(action)
            self.theme_actions[theme_name] = action


    def _create_path_widgets(self):
        path_layout = QHBoxLayout()
        self.path_label = QLabel("Hashcat Executable:")
        self.path_input = QLineEdit(); self.path_input.textChanged.connect(self.display_command)
        self.path_button = QPushButton("Browse..."); self.path_button.clicked.connect(self.browse_hashcat_path)
        path_layout.addWidget(self.path_label); path_layout.addWidget(self.path_input); path_layout.addWidget(self.path_button)
        self.main_layout.addLayout(path_layout)

    def _create_tabs(self):
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        tab_configs = {
            "Basic Attack": "_create_basic_tab_content", "Performance/Hardware": "_create_performance_tab_content",
            "Output/Session": "_create_output_tab_content", "Rules": "_create_rules_tab_content",
            "Mask/Charsets": "_create_mask_tab_content", "Advanced/Misc": "_create_advanced_tab_content",
            "Potfile Viewer": "_create_potfile_tab_content"
        }
        for name, method_name in tab_configs.items():
            scroll_area = self._create_scrollable_tab()
            getattr(self, method_name)(scroll_area.widget().layout())
            self.tabs.addTab(scroll_area, name)
        for control in self.controls.values():
            if isinstance(control, QLineEdit): control.textChanged.connect(self.display_command)
            elif isinstance(control, QCheckBox): control.toggled.connect(self.display_command)
            elif isinstance(control, QComboBox): control.currentIndexChanged.connect(self.display_command)
            elif isinstance(control, QSpinBox): control.valueChanged.connect(self.display_command)

    def _create_command_output_widgets(self):
        command_group = QGroupBox("Command & Output")
        command_layout = QVBoxLayout(command_group)
        cmd_line_layout = QHBoxLayout()
        self.command_output_display = QLineEdit(); self.command_output_display.setReadOnly(True)
        self.autocopy_checkbox = QCheckBox("Autocopy"); self.autocopy_checkbox.setToolTip("Automatically copy the command to the clipboard on change")
        self.controls['autocopy'] = self.autocopy_checkbox
        cmd_line_layout.addWidget(QLabel("Generated Command:")); cmd_line_layout.addWidget(self.command_output_display); cmd_line_layout.addWidget(self.autocopy_checkbox)
        command_layout.addLayout(cmd_line_layout)
        history_layout = QHBoxLayout()
        self.history_combo = QComboBox(); self.history_combo.setToolTip("Select a previous command"); self.history_combo.currentIndexChanged.connect(self._on_history_selected)
        history_layout.addWidget(QLabel("History:")); history_layout.addWidget(self.history_combo)
        command_layout.addLayout(history_layout)
        self._load_command_history()
        self._create_live_status_panel(command_layout)
        output_layout = QHBoxLayout()
        self.output_text = QTextEdit(); self.output_text.setReadOnly(True); self.output_text.setFontFamily("Monospace")
        self.clear_output_button = QPushButton("Clear Output"); self.clear_output_button.clicked.connect(self.output_text.clear)
        output_layout.addWidget(QLabel("Hashcat Output:")); output_layout.addStretch(); output_layout.addWidget(self.clear_output_button)
        command_layout.addLayout(output_layout)
        command_layout.addWidget(self.output_text, 1)
        self.main_layout.addWidget(command_group, 1)

    def _create_live_status_panel(self, parent_layout):
        self.status_group = QGroupBox("Live Status"); parent_layout.addWidget(self.status_group)
        status_layout = QFormLayout(self.status_group)
        self.progress_bar = QProgressBar(); self.progress_bar.setValue(0)
        self.status_label_recovered = QLabel("N/A")
        self.status_label_speed = QLabel("N/A")
        self.status_label_eta = QLabel("N/A")
        status_layout.addRow("Progress:", self.progress_bar)
        status_layout.addRow("Recovered:", self.status_label_recovered)
        status_layout.addRow("Total Speed:", self.status_label_speed)
        status_layout.addRow("Time Estimated:", self.status_label_eta)
        self.status_group.setVisible(False)

    def _create_control_buttons(self):
        control_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Command"); self.generate_button.clicked.connect(self.display_command)
        self.benchmark_button = QPushButton("Run Benchmark"); self.benchmark_button.clicked.connect(self.run_benchmark)
        self.run_button = QPushButton("Run Hashcat"); self.run_button.clicked.connect(self.run_hashcat); self.run_button.setObjectName("runButton")
        self.run_in_terminal_button = QPushButton("Run in Terminal"); self.run_in_terminal_button.clicked.connect(self.run_in_terminal); self.run_in_terminal_button.setObjectName("runButton")
        self.stop_button = QPushButton("Stop Hashcat"); self.stop_button.clicked.connect(self.stop_hashcat); self.stop_button.setEnabled(False); self.stop_button.setObjectName("stopButton")
        control_layout.addWidget(self.generate_button); control_layout.addWidget(self.benchmark_button); control_layout.addStretch(1)
        control_layout.addWidget(self.run_button); control_layout.addWidget(self.run_in_terminal_button); control_layout.addWidget(self.stop_button)
        self.main_layout.addLayout(control_layout)

    def _create_scrollable_tab(self):
        tab_widget = QWidget(); layout = QVBoxLayout(tab_widget); layout.setAlignment(Qt.AlignTop)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True); scroll_area.setWidget(tab_widget)
        return scroll_area

    def _create_basic_tab_content(self, layout):
        form_layout = QFormLayout()
        hash_file_layout = QHBoxLayout()
        self.hash_file_input = QLineEdit(); self.controls['hash_file'] = self.hash_file_input
        hash_file_layout.addWidget(self.hash_file_input)
        self.hash_file_button = QPushButton("Browse..."); self.hash_file_button.clicked.connect(lambda: self.browse_file(self.hash_file_input, "Select Hash File"))
        hash_file_layout.addWidget(self.hash_file_button)
        self.identify_hash_button = QPushButton("Identify Type"); self.identify_hash_button.setToolTip("Run 'hashcat --identify'"); self.identify_hash_button.clicked.connect(self.identify_hash_type)
        hash_file_layout.addWidget(self.identify_hash_button)
        form_layout.addRow("Hash File/HCCAPX:", hash_file_layout)
        self.hash_type_combo = QComboBox(); self.hash_type_combo.setEditable(True); self.hash_type_combo.setInsertPolicy(QComboBox.NoInsert)
        self.hash_type_combo.completer().setCompletionMode(QCompleter.PopupCompletion); self.hash_type_combo.completer().setFilterMode(Qt.MatchContains)
        self.hash_type_combo.currentIndexChanged.connect(self.update_contextual_widgets)
        form_layout.addRow("Hash Type (-m):", self.hash_type_combo); self.controls['hash_type'] = self.hash_type_combo
        self.attack_mode_combo = QComboBox()
        for name, code in ATTACK_MODES.items(): self.attack_mode_combo.addItem(name, userData=code)
        form_layout.addRow("Attack Mode (-a):", self.attack_mode_combo); self.controls['attack_mode'] = self.attack_mode_combo
        self.input_group = QGroupBox("Input Arguments"); self.input_layout = QVBoxLayout()
        self.input_fields = []; self.input_group.setLayout(self.input_layout)
        form_layout.addRow(self.input_group); self.controls['input_fields'] = self.input_fields
        layout.addLayout(form_layout)
        self.attack_mode_combo.currentIndexChanged.connect(self.update_input_fields)
        self.update_input_fields()

    def _create_performance_tab_content(self, layout):
        form_layout = QFormLayout()
        self.controls['workload'] = self._add_form_widget(form_layout, "Workload Profile (-w):", QComboBox(), combo_items=WORKLOAD_PROFILES, combo_default="Default")
        self.controls['optimized_kernels'] = self._add_form_widget(form_layout, "Optimized Kernels (-O):", QCheckBox("Enable optimized kernels (limits password length)"))
        devices_layout = QHBoxLayout()
        self.backend_devices_input = QLineEdit(); self.backend_devices_input.setPlaceholderText("e.g., 1,2")
        self.controls['backend_devices'] = self.backend_devices_input
        self.list_devices_button = QPushButton("List Devices"); self.list_devices_button.clicked.connect(self.list_devices)
        devices_layout.addWidget(self.backend_devices_input); devices_layout.addWidget(self.list_devices_button)
        form_layout.addRow("Backend Devices (-d):", devices_layout)
        self.controls['kernel_accel'] = self._add_form_widget(form_layout, "Kernel Accel (-n):", QSpinBox(minimum=0, maximum=1024), tooltip="Manual workload tuning, outerloop step size (0=auto)")
        self.controls['kernel_loops'] = self._add_form_widget(form_layout, "Kernel Loops (-u):", QSpinBox(minimum=0, maximum=1024), tooltip="Manual workload tuning, innerloop step size (0=auto)")
        layout.addLayout(form_layout)

    def _create_output_tab_content(self, layout):
        form_layout = QFormLayout()
        self.controls['outfile'] = self._add_form_widget(form_layout, "Output File (-o):", QLineEdit(), browse_type='save')
        self.controls['outfile_format_input'] = self._add_form_widget(form_layout, "Outfile Format:", QLineEdit(), placeholder="e.g., 1,3 (see --outfile-format)")
        self.controls['show_cracked'] = self._add_form_widget(form_layout, "Show Cracked (--show):", QCheckBox("Compare hashlist with potfile and show cracked"))
        self.controls['show_uncracked'] = self._add_form_widget(form_layout, "Show Uncracked (--left):", QCheckBox("Compare hashlist with potfile and show uncracked"))
        self.controls['remove_cracked'] = self._add_form_widget(form_layout, "Remove Cracked (--remove):", QCheckBox("Enable removal of cracked hashes"))
        self.controls['session_name'] = self._add_form_widget(form_layout, "Session Name (--session):", QLineEdit())
        self.controls['restore_session'] = self._add_form_widget(form_layout, "Restore Session (--restore):", QCheckBox("Restore session specified by --session"))
        layout.addLayout(form_layout)

    def _create_rules_tab_content(self, layout):
        form_layout = QFormLayout()
        self.controls['rules_file'] = self._add_form_widget(form_layout, "Rules File (-r):", QLineEdit(), browse_type='open')
        self.controls['generate_rules'] = self._add_form_widget(form_layout, "Generate Rules (-g):", QSpinBox(minimum=0, maximum=100000), tooltip="Generate X random rules (0=disable)")
        layout.addLayout(form_layout)

    def _create_mask_tab_content(self, layout):
        form_layout = QFormLayout()
        self.controls['custom_charset1'] = self._add_form_widget(form_layout, "Custom Charset 1 (-1):", QLineEdit(), placeholder="e.g., ?l?d?u")
        self.controls['custom_charset2'] = self._add_form_widget(form_layout, "Custom Charset 2 (-2):", QLineEdit(), placeholder="e.g., ?l?d?s")
        self.controls['increment'] = self._add_form_widget(form_layout, "Increment Mode (-i):", QCheckBox("Enable mask increment mode"))
        self.controls['increment_min'] = self._add_form_widget(form_layout, "Increment Min:", QSpinBox(minimum=0, maximum=64))
        self.controls['increment_max'] = self._add_form_widget(form_layout, "Increment Max:", QSpinBox(minimum=0, maximum=64))
        self.controls['increment_min'].setEnabled(False); self.controls['increment_max'].setEnabled(False)
        self.controls['increment'].toggled.connect(self.controls['increment_min'].setEnabled)
        self.controls['increment'].toggled.connect(self.controls['increment_max'].setEnabled)
        layout.addLayout(form_layout)

    def _create_advanced_tab_content(self, layout):
        form_layout = QFormLayout()
        self.controls['force'] = self._add_form_widget(form_layout, "Force (--force):", QCheckBox("Ignore warnings"))
        self.controls['status'] = self._add_form_widget(form_layout, "Status (--status):", QCheckBox("Enable automatic status screen update"))
        self.controls['status_timer'] = self._add_form_widget(form_layout, "Status Timer (sec):", QSpinBox(minimum=0, maximum=3600), tooltip="Seconds between status updates (0=default)")
        self.controls['username'] = self._add_form_widget(form_layout, "Ignore Username:", QCheckBox("Enable ignoring of usernames in hashfile"))
        self.controls['runtime'] = self._add_form_widget(form_layout, "Runtime (seconds):", QSpinBox(minimum=0, maximum=3600*24*7), tooltip="Abort session after X seconds (0=disable)")
        self.controls['hccapx_message_pair_widget'] = self._add_form_widget(form_layout, "HCCAPX Message Pair:", QSpinBox(minimum=0, maximum=10), tooltip="Load only message pairs from hccapx matching X (0=all)")
        self.controls['veracrypt_pim_start_widget'] = self._add_form_widget(form_layout, "VeraCrypt PIM Start:", QSpinBox(minimum=0, maximum=5000))
        self.controls['veracrypt_pim_stop_widget'] = self._add_form_widget(form_layout, "VeraCrypt PIM Stop:", QSpinBox(minimum=0, maximum=5000))
        layout.addLayout(form_layout)

    def _create_potfile_tab_content(self, layout):
        v_layout = QVBoxLayout()
        path_layout = QHBoxLayout()
        self.potfile_viewer_path_input = QLineEdit(); self.potfile_viewer_path_input.setPlaceholderText("Path to potfile")
        self.controls['potfile_viewer_path'] = self.potfile_viewer_path_input
        self._set_default_potfile_path()
        browse_pot_button = QPushButton("Browse..."); browse_pot_button.clicked.connect(lambda: self.browse_file(self.potfile_viewer_path_input, "Select Potfile"))
        load_pot_button = QPushButton("Load Potfile"); load_pot_button.clicked.connect(self.load_potfile_content)
        path_layout.addWidget(QLabel("Potfile:")); path_layout.addWidget(self.potfile_viewer_path_input, 1); path_layout.addWidget(browse_pot_button); path_layout.addWidget(load_pot_button)
        v_layout.addLayout(path_layout)
        search_layout = QHBoxLayout()
        self.potfile_search_input = QLineEdit(); self.potfile_search_input.setPlaceholderText("Search in potfile..."); self.potfile_search_input.textChanged.connect(self.search_in_potfile_viewer)
        search_layout.addWidget(QLabel("Search:")); search_layout.addWidget(self.potfile_search_input, 1)
        v_layout.addLayout(search_layout)
        self.potfile_viewer_text_edit = QTextEdit(); self.potfile_viewer_text_edit.setReadOnly(True); self.potfile_viewer_text_edit.setFontFamily("Monospace")
        v_layout.addWidget(self.potfile_viewer_text_edit, 1)
        layout.addLayout(v_layout)

    def _add_form_widget(self, form_layout, label, widget, **kwargs):
        if isinstance(widget, QComboBox) and 'combo_items' in kwargs:
            if 'combo_default' in kwargs: widget.addItem(kwargs['combo_default'], userData=None)
            for name, code in kwargs['combo_items'].items(): widget.addItem(name, userData=code)
        if isinstance(widget, QLineEdit) and 'placeholder' in kwargs: widget.setPlaceholderText(kwargs['placeholder'])
        if 'tooltip' in kwargs: widget.setToolTip(kwargs['tooltip'])
        if 'browse_type' in kwargs:
            row_layout = QHBoxLayout(); row_layout.addWidget(widget)
            browse_button = QPushButton("..."); browse_button.setFixedWidth(30)
            browse_type = kwargs['browse_type']
            if browse_type == 'open': browse_button.clicked.connect(lambda: self.browse_file(widget, f"Select {label}"))
            elif browse_type == 'save': browse_button.clicked.connect(lambda: self.browse_save_file(widget, f"Select {label}"))
            elif browse_type == 'dir': browse_button.clicked.connect(lambda: self.browse_directory(widget, f"Select {label}"))
            row_layout.addWidget(browse_button); form_layout.addRow(label, row_layout)
        else:
            form_layout.addRow(label, widget)
        return widget

    def apply_theme(self, theme_name):
        if theme_name in THEMES:
            self.setStyleSheet(THEMES[theme_name])
            self.settings.setValue("theme", theme_name)
            if theme_name in self.theme_actions: self.theme_actions[theme_name].setChecked(True)

    def _load_theme(self):
        # Default to "Dark" theme if none is set
        self.apply_theme(self.settings.value("theme", "Dark"))

    def _parse_and_populate_hash_modes(self, silent_on_error=False):
        if not hasattr(self, 'hash_type_combo'): return
        hashcat_path = self.path_input.text().strip()
        if not hashcat_path:
            self.HASH_MODES = {}; self.hash_type_combo.clear(); return
        try:
            process_result = subprocess.run([hashcat_path, '-hh'], capture_output=True, text=True, encoding='utf-8', errors='ignore', check=False, timeout=10)
            if process_result.returncode != 0:
                if not silent_on_error: QMessageBox.warning(self, "Hashcat Error", f"hashcat -hh failed: {process_result.stderr[:200]}")
                return
            help_text = process_result.stdout
        except Exception as e:
            if not silent_on_error: QMessageBox.warning(self, "Execution Error", f"Failed to run hashcat -hh: {e}")
            return
        parsed_modes = {}
        try:
            modes_text_match = re.search(r"^- \[ Hash Modes \] -$(.*?)^\s*- \[", help_text, re.MULTILINE | re.DOTALL)
            if modes_text_match:
                modes_text = modes_text_match.group(1)
                for line in modes_text.splitlines():
                    match = re.match(r"^\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$", line)
                    if match:
                        code, name, category = int(match.group(1)), match.group(2).strip(), match.group(3).strip()
                        parsed_modes[f"{code} | {name} | {category}"] = code
        except Exception as e:
            if not silent_on_error: QMessageBox.warning(self, "Parse Error", f"Could not parse hash modes from hashcat -hh: {e}")
        self.HASH_MODES = parsed_modes
        self._populate_hash_type_combo()

    def _populate_hash_type_combo(self):
        if not hasattr(self, 'hash_type_combo'): return
        current_selection_code = self.hash_type_combo.currentData()
        self.hash_type_combo.blockSignals(True); self.hash_type_combo.clear()
        sorted_hash_items = sorted(self.HASH_MODES.items(), key=lambda item: item[1])
        for name, code in sorted_hash_items: self.hash_type_combo.addItem(name, userData=code)
        index_to_select = self.hash_type_combo.findData(current_selection_code)
        if index_to_select != -1: self.hash_type_combo.setCurrentIndex(index_to_select)
        elif self.hash_type_combo.count() > 0: self.hash_type_combo.setCurrentIndex(0)
        self.hash_type_combo.blockSignals(False)

    def update_contextual_widgets(self):
        current_mode = self.controls['hash_type'].currentData()
        is_wpa = current_mode in WPA_HASH_MODES
        is_veracrypt = current_mode in VERACRYPT_HASH_MODES
        self.controls['hccapx_message_pair_widget'].setEnabled(is_wpa)
        self.controls['veracrypt_pim_start_widget'].setEnabled(is_veracrypt)
        self.controls['veracrypt_pim_stop_widget'].setEnabled(is_veracrypt)
        self.display_command()

    def identify_hash_type(self):
        if not self._pre_run_checks(check_hash_file_only=True): return
        self.output_text.append(f"\n--- Running 'hashcat --identify' ---\n")
        QApplication.processEvents()
        try:
            process_result = subprocess.run([self.path_input.text().strip(), '--identify', self.hash_file_input.text().strip()], capture_output=True, text=True, encoding='utf-8', errors='ignore', check=False, timeout=15)
            output = process_result.stdout + "\n" + process_result.stderr
            self.output_text.append(output)
            possible_section = re.search(r"Possible Hash-Modes:\n(?:-+\n)?(.*?)(?=\n\n|\n\s*---)", output, re.DOTALL | re.IGNORECASE)
            if possible_section:
                identified_modes = {code: dn for match in re.finditer(r"^\s*(\d+)\s*\|", possible_section.group(1), re.MULTILINE) if (code := int(match.group(1))) and (dn := next((d for d, c in self.HASH_MODES.items() if c == code), None))}
                if identified_modes: self._show_hash_suggestion_dialog(identified_modes)
                else: QMessageBox.information(self, "Identify Type", "No matching hash types found in your version of Hashcat.")
            else: QMessageBox.information(self, "Identify Type", "Could not identify any hash types.")
        except Exception as e: QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def _show_hash_suggestion_dialog(self, identified_modes):
        dialog = QDialog(self); dialog.setWindowTitle("Suggested Hash Types")
        layout = QVBoxLayout(dialog); list_widget = QListWidget()
        for code, display_name in sorted(identified_modes.items()):
            item = QListWidgetItem(display_name); item.setData(Qt.UserRole, code); list_widget.addItem(item)
        if list_widget.count() > 0: list_widget.setCurrentRow(0)
        layout.addWidget(QLabel("Select a hash type:")); layout.addWidget(list_widget)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec() and list_widget.currentItem():
            index = self.hash_type_combo.findData(list_widget.currentItem().data(Qt.UserRole))
            if index != -1: self.hash_type_combo.setCurrentIndex(index)

    def load_potfile_content(self):
        potfile_path = self.potfile_viewer_path_input.text().strip()
        if potfile_path and os.path.exists(potfile_path):
            try:
                with open(potfile_path, 'r', encoding='utf-8', errors='ignore') as f: self.potfile_viewer_text_edit.setText(f.read())
                self.output_text.append(f"\nPotfile loaded: {potfile_path}")
            except Exception as e: QMessageBox.critical(self, "Loading Error", f"Could not load the potfile: {e}")
        else: QMessageBox.warning(self, "File Missing", f"The potfile was not found: {potfile_path}")

    def search_in_potfile_viewer(self, text):
        self.potfile_viewer_text_edit.moveCursor(QTextCursor.Start)
        if text: self.potfile_viewer_text_edit.find(text)

    def _set_default_potfile_path(self):
        hc_path = self.path_input.text().strip()
        default_path = os.path.join(os.path.dirname(hc_path), "hashcat.potfile") if hc_path and os.path.isdir(os.path.dirname(hc_path)) else "hashcat.potfile"
        self.potfile_viewer_path_input.setText(default_path)

    def build_command_list(self):
        hashcat_path = self.path_input.text().strip()
        if not hashcat_path: return None
        cmd_list = [hashcat_path]
        
        def add_arg(flag, value, is_bool=False):
            if is_bool:
                if value: cmd_list.append(flag)
            elif isinstance(value, str) and value.strip(): cmd_list.extend([flag, value])
            elif isinstance(value, int) and (value != 0 or flag in ["-m", "-a", "--hccapx-message-pair"]):
                cmd_list.extend([flag, str(value)])
            elif value is not None and not isinstance(value, (str, int, bool)):
                cmd_list.extend([flag, str(value)])
        
        # *** BUGFIX: Explicitly handle -m and -a flags ***
        hash_type_widget = self.controls.get('hash_type')
        if hash_type_widget:
            add_arg("-m", hash_type_widget.currentData())

        attack_mode_widget = self.controls.get('attack_mode')
        if attack_mode_widget:
            add_arg("-a", attack_mode_widget.currentData())
        
        current_mode = self.controls['hash_type'].currentData()
        for name, widget in self.controls.items():
            if name in ['hash_type', 'attack_mode', 'hash_file', 'input_fields', 'potfile_viewer_path', 'autocopy']: continue
            flag_map = {'workload': '-w', 'optimized_kernels': '-O', 'backend_devices': '-d', 'kernel_accel': '-n', 'kernel_loops': '-u', 'outfile': '-o', 'outfile_format_input': '--outfile-format', 'show_cracked': '--show', 'show_uncracked': '--left', 'remove_cracked': '--remove', 'session_name': '--session', 'restore_session': '--restore', 'rules_file': '-r', 'generate_rules': '-g', 'custom_charset1': '-1', 'custom_charset2': '-2', 'increment': '-i', 'increment_min': '--increment-min', 'increment_max': '--increment-max', 'force': '--force', 'status': '--status', 'status_timer': '--status-timer', 'username': '--username', 'runtime': '--runtime', 'hccapx_message_pair_widget': '--hccapx-message-pair', 'veracrypt_pim_start_widget': '--veracrypt-pim-start', 'veracrypt_pim_stop_widget': '--veracrypt-pim-stop'}
            if name in flag_map:
                flag, value, is_bool = flag_map[name], None, isinstance(widget, QCheckBox)
                if is_bool: value = widget.isChecked()
                elif isinstance(widget, (QSpinBox, QComboBox)): value = widget.currentData() if isinstance(widget, QComboBox) else widget.value()
                elif isinstance(widget, QLineEdit): value = widget.text()
                
                if name == 'hccapx_message_pair_widget' and current_mode not in WPA_HASH_MODES: continue
                if name.startswith('veracrypt_pim') and current_mode not in VERACRYPT_HASH_MODES: continue
                if name.startswith('increment_') and not self.controls.get('increment', QCheckBox()).isChecked(): continue
                
                if value is not None: add_arg(flag, value, is_bool)
        
        hash_file = self.controls.get('hash_file', QLineEdit()).text().strip()
        if not hash_file: return None
        cmd_list.append(hash_file)
        for field in self.input_fields:
            if field.text().strip(): cmd_list.append(field.text().strip())
        return cmd_list

    def display_command(self):
        command_list = self.build_command_list()
        if command_list:
            full_command_str = shlex.join(command_list)
            self.command_output_display.setText(full_command_str)
            if self.controls.get('autocopy', QCheckBox()).isChecked():
                QApplication.clipboard().setText(full_command_str)
        else:
            self.command_output_display.setText("[Error generating command - check required fields]")

    def _add_to_history(self):
        full_command_str = self.command_output_display.text()
        if full_command_str.startswith("[Error"): return
        if full_command_str in self.command_history: self.command_history.remove(full_command_str)
        self.command_history.insert(0, full_command_str)
        if len(self.command_history) > self.MAX_HISTORY_ITEMS: self.command_history.pop()
        self._populate_history_combo(); self._save_command_history()
        self.history_combo.setCurrentIndex(0)

    def _pre_run_checks(self, check_hash_file_only=False):
        hashcat_path = self.path_input.text().strip()
        if not hashcat_path or not os.path.exists(hashcat_path):
            QMessageBox.warning(self, "Error", f"Hashcat executable not found: {hashcat_path}"); return False
        if sys.platform != "win32" and not os.access(hashcat_path, os.X_OK):
             QMessageBox.warning(self, "Error", f"Hashcat executable is not executable: {hashcat_path}"); return False
        if check_hash_file_only:
            hash_file = self.hash_file_input.text().strip()
            if not hash_file or not os.path.exists(hash_file):
                QMessageBox.warning(self, "Error", f"Hash file not found or not specified: {hash_file}"); return False
        return True

    def _start_process(self, command_list):
        if self.process and self.process.state() == QProcess.Running:
            QMessageBox.warning(self, "Warning", "A process is already running."); return
        self.output_text.clear(); QApplication.processEvents()
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        try:
            self.process.setWorkingDirectory(os.path.dirname(command_list[0]))
            self.process.start(command_list[0], command_list[1:])
            self.set_running_state(True)
            self.output_text.append(f"Starting: {shlex.join(command_list)}\n---\n")
        except Exception as e:
            self.output_text.append(f"\n--- Failed to start process: {e} ---")
            self.set_running_state(False)

    def run_hashcat(self):
        if not self._pre_run_checks(check_hash_file_only=True): return
        self.display_command()
        command_list = self.build_command_list()
        if not command_list:
            self.output_text.setText("Cannot run: Command generation failed."); return
        self._add_to_history()
        self._start_process(command_list)

    def run_benchmark(self):
        if not self._pre_run_checks(): return
        self._start_process([self.path_input.text().strip(), '--benchmark'])
    
    def list_devices(self):
        if not self._pre_run_checks(): return
        self._start_process([self.path_input.text().strip(), '-I'])

    def run_in_terminal(self):
        if not self._pre_run_checks(check_hash_file_only=True): return
        self.display_command(); command_list = self.build_command_list()
        if not command_list: QMessageBox.warning(self, "Error", "Command generation failed."); return
        self._add_to_history(); final_command = self.command_output_display.text()
        self.output_text.append(f"\nAttempting to run in new terminal:\n{final_command}\n")
        try:
            cmd, cwd = "", os.path.dirname(command_list[0])
            if platform.system() == "Windows": cmd = f'start "Hashcat" cmd /k "cd /d {shlex.quote(cwd)} && {final_command}"'
            elif platform.system() == "Darwin": cmd = f'tell application "Terminal" to do script "cd {shlex.quote(cwd)} && {final_command}"'
            elif platform.system() == "Linux":
                shell_cmd = f"cd {shlex.quote(cwd)} && {final_command}; exec bash"
                for term in [["gnome-terminal", "--", "bash", "-c", shell_cmd], ["konsole", "-e", shell_cmd], ["xterm", "-e", shell_cmd]]:
                    try: subprocess.Popen(term); return
                    except FileNotFoundError: continue
                QMessageBox.warning(self, "Error", "Could not find a known terminal emulator."); return
            if cmd: subprocess.Popen(cmd, shell=True if platform.system() == "Windows" else False)
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to open terminal: {e}")

    def stop_hashcat(self):
        if self.process and self.process.state() == QProcess.Running:
            self.output_text.append("\n--- Sending termination signal ---")
            self.process.terminate()
            if not self.process.waitForFinished(2000):
                 self.output_text.append("\n--- Forcing shutdown (kill) ---"); self.process.kill()
        else: self.set_running_state(False)

    def handle_output(self):
        if not self.process: return
        text = bytes(self.process.readAllStandardOutput()).decode(errors='ignore')
        self.output_text.moveCursor(QTextCursor.End); self.output_text.insertPlainText(text); self.output_text.moveCursor(QTextCursor.End)
        status_match = re.search(r"^Status.*?: (.*?)\s*$", text, re.MULTILINE)
        if status_match and status_match.group(1) == "Running": self.status_group.setVisible(True)
        progress_match = re.search(r"^Progress.*?\(([\d.]+)%\)", text, re.MULTILINE)
        if progress_match: self.progress_bar.setValue(int(float(progress_match.group(1))))
        recovered_match = re.search(r"^Recovered.*?: (\d+/\d+)", text, re.MULTILINE)
        if recovered_match: self.status_label_recovered.setText(recovered_match.group(1))
        speed_match = re.search(r"^Speed.*?: (.*) ", text, re.MULTILINE)
        if speed_match: self.status_label_speed.setText(speed_match.group(1).strip())
        eta_match = re.search(r"^Time.Estimated.*?: (.*) ", text, re.MULTILINE)
        if eta_match: self.status_label_eta.setText(eta_match.group(1).strip())

    def process_finished(self, exit_code=0, exit_status=QProcess.NormalExit):
        status_text = "Finished" if exit_status == QProcess.NormalExit else "Crashed"
        self.output_text.append(f"\n--- Process {status_text} (Code: {exit_code}) ---")
        self.set_running_state(False)

    def process_error(self, error):
        self.output_text.append(f"\n--- Process Error: {self.process.errorString()} ---")
        self.set_running_state(False)

    def set_running_state(self, is_running):
        self.run_button.setEnabled(not is_running)
        self.run_in_terminal_button.setEnabled(not is_running)
        self.benchmark_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        if not is_running:
            self.status_group.setVisible(False)
            self.progress_bar.setValue(0)
        self.process = None if not is_running else self.process

    def closeEvent(self, event):
        self._save_command_history()
        self.settings.setValue("theme", next((name for name, action in self.theme_actions.items() if action.isChecked()), "Dark"))
        self.save_hashcat_path()
        if self.process and self.process.state() == QProcess.Running:
            reply = QMessageBox.question(self, 'Confirm Exit', "Hashcat is running. Do you want to stop it and exit?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes: self.stop_hashcat(); event.accept()
            elif reply == QMessageBox.No: event.accept()
            else: event.ignore()
        else: event.accept()

    def get_settings_dict(self):
        settings_data = {'hashcat_executable_path': self.path_input.text()}
        for name, widget in self.controls.items():
            if name == 'input_fields': settings_data[name] = [field.text() for field in widget]
            elif isinstance(widget, QLineEdit): settings_data[name] = widget.text()
            elif isinstance(widget, QCheckBox): settings_data[name] = widget.isChecked()
            elif isinstance(widget, QComboBox): settings_data[name + "_text"] = widget.currentText(); settings_data[name + "_data"] = widget.currentData()
            elif isinstance(widget, QSpinBox): settings_data[name] = widget.value()
        return settings_data

    def load_settings_dict(self, settings_data):
        self.path_input.setText(settings_data.get('hashcat_executable_path', ''))
        self._parse_and_populate_hash_modes(silent_on_error=True)
        for name, widget in self.controls.items():
            value = settings_data.get(name)
            try:
                if isinstance(widget, QLineEdit): widget.setText(str(value))
                elif isinstance(widget, QCheckBox): widget.setChecked(bool(value))
                elif isinstance(widget, QComboBox):
                    if widget.findData(settings_data.get(name + "_data")) != -1: widget.setCurrentIndex(widget.findData(settings_data.get(name + "_data")))
                    elif widget.findText(settings_data.get(name + "_text")) != -1: widget.setCurrentIndex(widget.findText(settings_data.get(name + "_text")))
                elif isinstance(widget, QSpinBox): widget.setValue(int(value))
            except (TypeError, ValueError): continue
        self.update_input_fields()
        if 'input_fields' in settings_data:
            for i, field_val in enumerate(settings_data['input_fields']):
                if i < len(self.controls['input_fields']): self.controls['input_fields'][i].setText(str(field_val))
        self.update_contextual_widgets()
        self.display_command()

    def save_settings_dialog(self):
        session_name = self.controls.get('session_name', QLineEdit()).text().strip()
        default_filename = f"{session_name}.hcatgui" if session_name else "hashcat_profile.hcatgui"
        start_dir = self.settings.value("lastSettingsDir", "")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Profile As...", os.path.join(start_dir, default_filename), "Hashcat GUI Profiles (*.hcatgui);;JSON (*.json)")
        if file_path:
            try:
                with open(file_path, 'w') as f: json.dump(self.get_settings_dict(), f, indent=4)
                self.output_text.append(f"\nSettings saved to: {file_path}")
                self.settings.setValue("lastSettingsDir", os.path.dirname(file_path))
            except Exception as e: QMessageBox.critical(self, "Error", f"Error while saving: {e}")

    def load_settings_dialog(self):
        start_dir = self.settings.value("lastSettingsDir", "")
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Profile From...", start_dir, "Hashcat GUI Profiles (*.hcatgui);;JSON (*.json);;All files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as f: self.load_settings_dict(json.load(f))
                self.output_text.append(f"\nSettings loaded from: {file_path}")
                self.settings.setValue("lastSettingsDir", os.path.dirname(file_path))
            except Exception as e: QMessageBox.critical(self, "Error", f"Error while loading: {e}")

    def _save_command_history(self): self.settings.setValue("commandHistory", self.command_history)
    def _load_command_history(self): self.command_history = self.settings.value("commandHistory", [])[:self.MAX_HISTORY_ITEMS]; self._populate_history_combo()
    def _populate_history_combo(self): self.history_combo.blockSignals(True); self.history_combo.clear(); self.history_combo.addItems(self.command_history); self.history_combo.setCurrentIndex(-1); self.history_combo.blockSignals(False)
    def _on_history_selected(self, index):
        if index >= 0: self.command_output_display.setText(self.history_combo.itemText(index))

    def update_input_fields(self):
        while self.input_layout.count():
            child = self.input_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub_child = child.layout().takeAt(0)
                    if sub_child.widget(): sub_child.widget().deleteLater()
                child.layout().deleteLater()
        self.input_fields.clear()
        attack_mode_code = self.controls.get('attack_mode', QComboBox()).currentData()
        field_configs = {0: [("Wordlist/Directory:", False)], 1: [("Left Wordlist/Directory:", False), ("Right Wordlist/Directory:", False)], 3: [("Mask:", True)], 6: [("Wordlist/Directory:", False), ("Mask:", True)], 7: [("Mask:", True), ("Wordlist/Directory:", False)], 9: [("Base Wordlist/Directory:", False)]}.get(attack_mode_code, [])
        form_layout = QFormLayout()
        for label, is_mask in field_configs:
            input_widget = QLineEdit(); input_widget.textChanged.connect(self.display_command); self.input_fields.append(input_widget)
            if is_mask: form_layout.addRow(label, input_widget)
            else:
                browse_button = QPushButton("..."); browse_button.setFixedWidth(30); browse_button.clicked.connect(lambda c, lw=input_widget: self.browse_file_or_dir(lw))
                row = QHBoxLayout(); row.addWidget(input_widget); row.addWidget(browse_button); form_layout.addRow(label, row)
        self.input_layout.addLayout(form_layout)

    def browse_file(self, line_edit, caption="Select File"):
        start_dir = os.path.dirname(line_edit.text()) or self.settings.value("lastBrowseDir", "")
        file_path, _ = QFileDialog.getOpenFileName(self, caption, dir=start_dir)
        if file_path: line_edit.setText(file_path); self.settings.setValue("lastBrowseDir", os.path.dirname(file_path))
    def browse_save_file(self, line_edit, caption="Save File"):
        start_dir = os.path.dirname(line_edit.text()) or self.settings.value("lastBrowseDir", "")
        file_path, _ = QFileDialog.getSaveFileName(self, caption, dir=start_dir)
        if file_path: line_edit.setText(file_path); self.settings.setValue("lastBrowseDir", os.path.dirname(file_path))
    def browse_directory(self, line_edit, caption="Select Directory"):
        start_dir = line_edit.text() if os.path.isdir(line_edit.text()) else self.settings.value("lastBrowseDir", "")
        dir_path = QFileDialog.getExistingDirectory(self, caption, dir=start_dir)
        if dir_path: line_edit.setText(dir_path); self.settings.setValue("lastBrowseDir", dir_path)
    def browse_file_or_dir(self, line_edit): self.browse_file(line_edit, "Select Input File or Directory")
    def browse_hashcat_path(self):
        start_dir = os.path.dirname(self.path_input.text()) or self.settings.value("lastHashcatDir", "")
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Hashcat Executable", dir=start_dir, filter="Executables (*.exe *.bin hashcat hashcat.bin);;All files (*)")
        if file_path: self.path_input.setText(file_path); self.save_hashcat_path(); self._parse_and_populate_hash_modes(silent_on_error=False); self.settings.setValue("lastHashcatDir", os.path.dirname(file_path))
    def save_hashcat_path(self): self.settings.setValue("hashcatPath", self.path_input.text())
    def load_hashcat_path(self): self.path_input.setText(self.settings.value("hashcatPath", ""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HashcatGUI()
    window.show()
    sys.exit(app.exec())
