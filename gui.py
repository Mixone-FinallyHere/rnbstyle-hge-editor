import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import importlib.util
import types

import main as main_module

DEFAULT_CONFIG_FILE = "config.py"

AI_FLAGS = [
    "F_PRIORITIZE_SUPER_EFFECTIVE",
    "F_EVALUATE_ATTACKS",
    "F_EXPERT_ATTACKS",
    "F_PRIORITIZE_STATUS_MOVES",
    "F_RISKY_ATTACKS",
    "F_PRIORITIZE_DAMAGE",
    "F_MULTI_BATTLE_PARTNER",
    "F_DOUBLE_BATTLE",
    "F_PRIORITIZE_HEALING",
    "F_USE_WEATHER",
    "F_HARRASSMENT",
    "F_ROAMING_MON",
    "F_SAFARI_ZONE",
    "F_CATCHING_DEMO",
]

class ConfigEditor:
    def __init__(self, filepath, savepath=None):
        self.filepath = filepath
        self.savepath = savepath or filepath
        self.config_instance = None
        self.config_data = {}
        self.load()

    def load(self):
        module_name = "user_config"
        spec = importlib.util.spec_from_file_location(module_name, self.filepath)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        config_class = getattr(config_module, "Config", None)
        if config_class is None:
            raise ValueError("No Config class found in config file.")
        self.config_instance = config_class()
        self.config_data = {
            key: getattr(self.config_instance, key)
            for key in dir(self.config_instance)
            if not key.startswith("_") and not callable(getattr(self.config_instance, key))
        }

        with open(self.filepath, "r") as f:
            self.source = f.read()

    def save(self, updated_values, savepath=None):
        savepath = savepath or self.savepath
        lines = []
        for key, val in updated_values.items():
            if isinstance(val, str):
                val_str = f'"{val}"'
            elif isinstance(val, bool):
                val_str = "True" if val else "False"
            elif isinstance(val, list):
                val_str = str(val)
            else:
                val_str = str(val)
            lines.append(f"{key} = {val_str}")

        with open(savepath, "w") as f:
            f.write("\n".join(lines) + "\n")

        self.savepath = savepath




class VisualConfigTab(ttk.Frame):
    BASE_KEYS = [
        "INPUT_DIR",
        "ROOT_DIR",
        "CREATE_BACKUP",
        "DEFAULT_AI_FLAGS",
        "DEFAULT_ITEMS",
        "DEFAULT_DV",
        "USE_IV_EV",
        "DEFAULT_IVS",
        "DEFAULT_EVS",
        "DEFAULT_BALL",
        "ADVANCED_MODE"
    ]

    CALCULATED_KEYS = [
        "TRAINER_DIR",
        "OUTPUT_FILE",
        "BACKUP_FILE",
        "INCLUDE_DIR",
        "CONSTANTS_DIR",
        "ABILITY_HEADER",
        "ITEM_HEADER",
        "MOVE_HEADER",
        "SPECIES_HEADER",
        "TRAINERCLASS_HEADER",
        "BATTLE_HEADER",
        "POKEMON_HEADER"
    ]

    def __init__(self, master, config_editor):
        super().__init__(master)
        self.editor = config_editor
        self.fields = {}

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_form()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        save_btn = ttk.Button(btn_frame, text="Save", command=self.save)
        saveas_btn = ttk.Button(btn_frame, text="Save As...", command=self.save_as)

        save_btn.pack(side="left", padx=5)
        saveas_btn.pack(side="left", padx=5)

    def build_form(self):
        self.fields.clear()
        data = self.editor.config_data
        # We'll show all base keys + calculated keys, but calculated keys only if in advanced mode or for display
        advanced_mode = data.get("ADVANCED_MODE", False)

        all_keys = self.BASE_KEYS + self.CALCULATED_KEYS

        for idx, key in enumerate(all_keys):
            value = data.get(key, "")

            ttk.Label(self.scrollable_frame, text=key).grid(row=idx, column=0, sticky="w", padx=5, pady=5)

            widget = None

            # Disable calculated keys if advanced_mode is False
            is_calculated = key in self.CALCULATED_KEYS
            disabled = is_calculated and not advanced_mode

            if key == "DEFAULT_ITEMS":
                self.fields[key] = []
                frame = ttk.Frame(self.scrollable_frame)
                for i in range(4):
                    item_val = value[i] if i < len(value) else ""
                    var = tk.StringVar(value=item_val)
                    entry = ttk.Entry(frame, textvariable=var, width=15)
                    entry.grid(row=0, column=i, padx=2, pady=2)
                    self.fields[key].append(var)
                frame.grid(row=idx, column=1, padx=5, pady=5, sticky="we")

            elif key == "DEFAULT_AI_FLAGS":
                self.fields[key] = {}
                frame = ttk.Frame(self.scrollable_frame)
                for i, flag in enumerate(AI_FLAGS):
                    var = tk.BooleanVar(value=(flag in value))
                    chk = ttk.Checkbutton(frame, text=flag, variable=var)
                    chk.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
                    self.fields[key][flag] = var
                frame.grid(row=idx, column=1, padx=5, pady=5, sticky="we")

            elif isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                widget = ttk.Checkbutton(self.scrollable_frame, variable=var)
                if disabled:
                    widget.state(['disabled'])
                widget.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
                self.fields[key] = var

            elif isinstance(value, int):
                var = tk.IntVar(value=value)
                widget = ttk.Spinbox(self.scrollable_frame, from_=0, to=999, textvariable=var)
                if disabled:
                    widget.config(state="readonly")
                widget.grid(row=idx, column=1, padx=5, pady=5, sticky="we")
                self.fields[key] = var

            elif isinstance(value, str) and ("DIR" in key or "FILE" in key):
                var = tk.StringVar(value=value)
                widget = ttk.Entry(self.scrollable_frame, textvariable=var, width=50)
                if disabled:
                    widget.config(state="readonly")

                def choose_dir_or_file(k=key, v=var, dis=disabled):
                    if dis:
                        return
                    if "DIR" in k:
                        path = filedialog.askdirectory()
                    else:
                        path = filedialog.askopenfilename()
                    if path:
                        v.set(path)

                browse_btn = ttk.Button(self.scrollable_frame, text="Browse", command=choose_dir_or_file)
                if disabled:
                    browse_btn.state(['disabled'])

                widget.grid(row=idx, column=1, padx=5, pady=5, sticky="we")
                browse_btn.grid(row=idx, column=2, padx=5)
                self.fields[key] = var

            elif isinstance(value, list):
                # For other lists (not DEFAULT_ITEMS or DEFAULT_AI_FLAGS), just use string entry
                var = tk.StringVar(value=str(value))
                widget = ttk.Entry(self.scrollable_frame, textvariable=var, width=50)
                if disabled:
                    widget.config(state="readonly")
                widget.grid(row=idx, column=1, padx=5, pady=5, sticky="we")
                self.fields[key] = var

            else:
                var = tk.StringVar(value=str(value))
                widget = ttk.Entry(self.scrollable_frame, textvariable=var, width=50)
                if disabled:
                    widget.config(state="readonly")
                widget.grid(row=idx, column=1, padx=5, pady=5, sticky="we")
                self.fields[key] = var

        # Watch ADVANCED_MODE changes to enable/disable calculated fields dynamically
        adv_mode_var = self.fields.get("ADVANCED_MODE")
        if adv_mode_var:
            adv_mode_var.trace_add("write", self.toggle_advanced_mode)


    def toggle_advanced_mode(self, *args):
        advanced_mode = self.fields["ADVANCED_MODE"].get()
        for key in self.CALCULATED_KEYS:
            widget_var = self.fields.get(key)
            if widget_var is None:
                continue
            # Get the widget from grid slaves (a little hacky, but we know the layout)
            for widget in self.scrollable_frame.grid_slaves():
                info = widget.grid_info()
                label = None
                try:
                    label = self.scrollable_frame.grid_slaves(row=info["row"], column=0)[0]
                except Exception:
                    pass
                if label and label.cget("text") == key:
                    # Enable/disable widget accordingly
                    if isinstance(widget, ttk.Checkbutton):
                        if advanced_mode:
                            widget.state(["!disabled"])
                        else:
                            widget.state(["disabled"])
                    else:
                        if advanced_mode:
                            widget.config(state="normal")
                        else:
                            widget.config(state="readonly")

    def collect_updates(self):
        updated = {}
        for key, var in self.fields.items():
            value = var.get()
            if key == "DEFAULT_ITEMS":
                updated[key] = [var.get() for var in self.fields[key]]
            elif key == "DEFAULT_AI_FLAGS":
                updated[key] = [flag for flag, var in self.fields[key].items() if var.get()]
            elif isinstance(value, bool):
                updated[key] = value
            elif isinstance(value, str):
                if value == "True":
                    updated[key] = True
                elif value == "False":
                    updated[key] = False
                elif value.isdigit():
                    updated[key] = int(value)
                elif value.startswith("[") and value.endswith("]"):
                    try:
                        updated[key] = eval(value, {"__builtins__": None}, {})
                    except Exception:
                        updated[key] = value
                else:
                    updated[key] = value
            else:
                updated[key] = value

        return updated

    def save(self):
        updated = self.collect_updates()
        # If advanced mode is off, save only base keys + ADVANCED_MODE (exclude calculated)
        if not updated.get("ADVANCED_MODE", False):
            filtered = {k: v for k, v in updated.items() if k in self.BASE_KEYS}
        else:
            filtered = updated

        self.editor.save(filtered)
        messagebox.showinfo("Saved", f"Configuration saved to:\n{self.editor.savepath}")

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            updated = self.collect_updates()
            if not updated.get("ADVANCED_MODE", False):
                filtered = {k: v for k, v in updated.items() if k in self.BASE_KEYS}
            else:
                filtered = updated
            self.editor.save(filtered, savepath=path)
            messagebox.showinfo("Saved As", f"Configuration saved to:\n{path}")



class RunTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        run_btn = ttk.Button(self, text="Run Script", command=self.run_script)
        run_btn.pack(pady=10)

        self.output = tk.Text(self, height=15, wrap="word", state="disabled")
        self.output.pack(expand=True, fill="both", padx=10, pady=10)

    def run_script(self):
        try:
            # Dynamically load and instantiate the Config class to pass as an object
            module_name = "user_config"
            config_path = DEFAULT_CONFIG_FILE
            spec = importlib.util.spec_from_file_location(module_name, config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            config_class = getattr(config_module, "Config", None)
            if config_class is None:
                raise ValueError("No Config class found in config file.")
            config_instance = config_class()

            main_module.main(config_instance)

            self.output.config(state="normal")
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "Script completed successfully.")
            self.output.config(state="disabled")

            messagebox.showinfo("Success", "Script completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


class App(tk.Tk):
    def __init__(self, config_path=DEFAULT_CONFIG_FILE):
        super().__init__()
        self.title("Trainer Config Editor")
        self.geometry("900x650")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.config_editor = ConfigEditor(config_path)
        visual_tab = VisualConfigTab(notebook, self.config_editor)
        run_tab = RunTab(notebook)

        notebook.add(visual_tab, text="Visual Config Editor")
        notebook.add(run_tab, text="Run Script")


if __name__ == "__main__":
    App().mainloop()
