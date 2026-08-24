# EasySticky_linux_v1.5
import tkinter as tk
from tkinter import colorchooser
import tkinter.font as tkfont
from tkinter import filedialog
import re
import webbrowser
from pathlib import Path
import sys
import json

CONFIG_PATH = Path("config.json")

URL_PATTERN = r"https?://[^\s]+"


DEFAULT_CONFIG = {
    "window": {"width": 400, "height": 500, "always_on_top": True, "x": 100, "y": 100},
    "style": {
        "bg_color": "#e4e093",
        "font_color": "#000000",
        "font_family": "Yu Gothic Medium",
        "font_size": 14,
    },
}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


# Path for icon
def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    return base_path / relative_path


# Window
class MemoWindow:
    windows: list["MemoWindow"] = []

    def __init__(self, root=None):
        # root or toplevel
        if root is None:
            self.win = tk.Tk()
            # Only root window handles autosave
            self.root_flag = True
            self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        else:
            self.win = tk.Toplevel(root)
            self.root_flag = False
        icon = tk.PhotoImage(file=resource_path("assets/easysticky.png"))
        self.win.iconphoto(True, icon)
        self.icon = icon

        # Config from json file
        self.config = load_config()
        self.win.geometry(
            f"{self.config['window']['width']}x{self.config['window']['height']}+{self.config['window']['x']}+{self.config['window']['y']}"
        )
        self.win.title("EasySticky")
        self.win.configure(bg="#e4e093")

        # Status
        self.topmost = self.config["window"]["always_on_top"]
        self.resizing = False

        self.win.attributes("-topmost", self.topmost)

        # Padding
        self.container = tk.Frame(
            self.win,
            bg=self.config["style"]["bg_color"],
            padx=5,
            pady=5,
            bd=0,
            highlightthickness=0,
        )
        self.container.pack(expand=True, fill="both")

        # root marker
        if self.root_flag:
            self.corner = tk.Canvas(
                self.win,
                width=18,
                height=18,
                bg=darker(self.container["bg"], 12),
                highlightthickness=0,
            )

            self.corner.place(relx=1.0, x=-18, y=0)

            self.corner.create_polygon(
                18, 0, 18, 18, 0, 0, fill=darker(self.corner["bg"], 20), outline=""
            )

        # Apply Font
        self.font_name = self.config["style"]["font_family"]
        self.font_size = self.config["style"]["font_size"]
        # Text
        self.text = tk.Text(
            self.container,
            wrap="word",
            bg=self.config["style"]["bg_color"],
            fg=self.config["style"]["font_color"],
            insertbackground="black",
            borderwidth=0,
            highlightthickness=0,
            undo=True,
            font=(self.font_name, self.font_size),
        )
        self.text.pack(expand=True, fill="both")

        # Right-click Menu
        self.menu = tk.Menu(self.win, tearoff=0)
        self.font_var = tk.StringVar(value=self.font_name)
        # Font
        self.common_fonts = [
            "Courier",
            "Consolas",
            "Meiryo",
            "Yu Gothic Medium",
            "Arial",
            "Times New Roman",
        ]
        self.all_fonts = sorted(f for f in tkfont.families() if not f.startswith("@"))
        self.font_menu = tk.Menu(self.menu, tearoff=0)
        # Common fonts
        common_menu = tk.Menu(self.font_menu, tearoff=0)
        for f in self.common_fonts:
            common_menu.add_radiobutton(
                label=f,
                font=(f, 12),
                variable=self.font_var,
                value=f,
                command=lambda f=f: self.set_font(f),
            )
        self.font_menu.add_cascade(label="Common Fonts", menu=common_menu)

        # All fonts
        all_menu = tk.Menu(self.font_menu, tearoff=0)
        for f in self.all_fonts:
            all_menu.add_radiobutton(
                label=f,
                font=(f, 12),
                variable=self.font_var,
                value=f,
                command=lambda f=f: self.set_font(f),
            )
        self.font_menu.add_cascade(label="All Fonts", menu=all_menu)
        self.menu.add_cascade(label="Font", menu=self.font_menu)

        # Size
        self.size_var = tk.IntVar(value=self.font_size)
        self.size_menu = tk.Menu(self.menu, tearoff=0)
        for s in [10, 12, 14, 16, 18, 20, 24]:
            self.size_menu.add_radiobutton(
                label=str(s),
                variable=self.size_var,
                value=s,
                command=lambda s=s: self.set_size(s),
            )

        self.menu.add_cascade(label="Size", menu=self.size_menu)
        # --- bind ---
        self.bind_events()

        # Color settings
        self.color_menu = tk.Menu(self.menu, tearoff=0)

        self.color_menu.add_command(
            label="Background Color", command=self.choose_bg_color
        )
        self.color_menu.add_command(label="Font Color", command=self.choose_font_color)
        self.menu.add_cascade(label="Color", menu=self.color_menu)

        # Add to Window list
        MemoWindow.windows.append(self)
        # Load Auto saved file
        try:
            with open(
                f"autosave_{MemoWindow.windows.index(self)}.txt", "r", encoding="utf-8"
            ) as f:
                self.text.insert(tk.END, f.read())
        except FileNotFoundError:
            pass

        # run autosave
        self.auto_save()
        # focus
        self.win.after(100, self.force_focus)

    # ======================
    # Functions
    # ======================
    # Color Chooser
    def on_close(self):
        if self.root_flag:
            self.config["window"]["width"] = self.win.winfo_width()
            self.config["window"]["height"] = self.win.winfo_height()
            self.config["window"]["x"] = self.win.winfo_x()
            self.config["window"]["y"] = self.win.winfo_y()
            save_config(self.config)
            self.auto_save()  # Save before closing
            MemoWindow.windows.remove(self)
            self.win.destroy()
        else:
            self.quit_window()

    def choose_bg_color(self) -> None:
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:
            self.config["style"]["bg_color"] = color[1]
            self.bg_color = color[1]
            self.text.config(bg=self.bg_color)
            self.container.config(bg=self.bg_color)
            if self.root_flag:
                self.corner.config(bg=darker(self.bg_color, 12))
                self.corner.delete("all")
                self.corner.create_polygon(
                    18, 0, 18, 18, 0, 0, fill=darker(self.bg_color, 32), outline=""
                )

    def choose_font_color(self) -> None:
        color = colorchooser.askcolor(title="Choose Font Color")
        if color[1]:
            self.config["style"]["font_color"] = color[1]
            self.font_color = color[1]
            self.text.config(fg=self.font_color)

    # focus
    def force_focus(self):
        # self.win.overrideredirect(False)
        self.win.update()

        self.win.lift()
        self.win.attributes("-topmost", True)

        self.text.focus_set()

        self.win.after(50, lambda: self.win.attributes("-topmost", self.topmost))
        # self.win.after(100, lambda: self.win.overrideredirect(True))

    # font
    def set_font(self, font):
        self.config["style"]["font_family"] = font
        self.font_name = font
        self.font_var.set(font)
        self.apply_font()

    def set_size(self, size):
        self.config["style"]["font_size"] = size
        self.font_size = size
        self.size_var.set(size)
        self.apply_font()

    def apply_font(self):
        self.config["style"]["font_family"] = self.font_name
        self.config["style"]["font_size"] = self.font_size
        self.text.config(font=(self.font_name, self.font_size))

    # Right-click Menu
    def show_menu(self, event=None):
        self.font_var.set(self.font_name)
        self.size_var.set(self.font_size)

        index = self.text.index(f"@{event.x},{event.y}")

        ranges = self.text.tag_ranges("link")

        url = None

        for i in range(0, len(ranges), 2):
            start = ranges[i]
            end = ranges[i + 1]

            if self.text.compare(index, ">=", start) and self.text.compare(
                index, "<", end
            ):
                url = self.text.get(start, end)
                break

        self.menu.delete(0, tk.END)

        # link menu
        if url:
            self.menu.add_command(
                label="Open Link",
                command=lambda u=url: webbrowser.open(u),
            )

            self.menu.add_separator()
        # normal menu
        self.menu.add_cascade(label="Font", menu=self.font_menu)
        self.menu.add_cascade(label="Size", menu=self.size_menu)
        self.menu.add_cascade(label="Color", menu=self.color_menu)

        self.menu.tk_popup(event.x_root, event.y_root)

    # 保存 Ctrl+S
    def save_file(self, event=None):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))

    # 開く Ctrl+O
    def open_file(self, event=None):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, f.read())

    # 閉じる Ctrl+Q
    def quit_window(self, event=None):
        self.config["window"]["width"] = self.win.winfo_width()
        self.config["window"]["height"] = self.win.winfo_height()
        self.config["window"]["x"] = self.win.winfo_x()
        self.config["window"]["y"] = self.win.winfo_y()
        self.auto_save()
        save_config(self.config)
        MemoWindow.windows.remove(self)
        self.win.destroy()

    # 最前面表示 Ctrl+T
    def toggle_topmost(self, event=None):
        self.topmost = not self.topmost
        self.config["window"]["always_on_top"] = self.topmost
        self.win.attributes("-topmost", self.topmost)

    # 新規ウィンドウ Ctrl+N
    def new_window(self, event=None):
        save_config(self.config)
        self.win.update_idletasks()
        x = self.win.winfo_x()
        y = self.win.winfo_y()

        offset_x = 30
        offset_y = 30
        new = MemoWindow(self.win)
        new.font_name = self.font_name
        new.font_size = self.font_size
        new.win.geometry(f"+{x + offset_x}+{y + offset_y}")
        new.size_var.set(new.font_size)
        new.apply_font()

    # self.root_flagによって自動保存はルートウィンドウのみに限定しています。
    def auto_save(self):
        if not self.root_flag:
            return
        idx = MemoWindow.windows.index(self)
        with open(f"autosave_{idx}.txt", "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", tk.END))
        self.win.after(5000, self.auto_save)

    # テキストエリアをドラッグすることでウィンドウの移動
    def start_move(self, event):
        self.win.x = event.x
        self.win.y = event.y

    def do_move(self, event):
        x = self.win.winfo_pointerx() - self.win.x
        y = self.win.winfo_pointery() - self.win.y
        self.config["window"]["x"] = x
        self.config["window"]["y"] = y
        self.win.geometry(f"+{x}+{y}")

    # URL link
    # Update link jump
    def enter_link(self, event):
        self.text.config(cursor="hand2")

    def leave_link(self, event):
        self.text.config(cursor="xterm")

    def update_links(self):
        self.text.tag_remove("link", "1.0", tk.END)

        content = self.text.get("1.0", tk.END)

        for match in re.finditer(URL_PATTERN, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"

            self.text.tag_add("link", start, end)

        self.text.tag_config("link", foreground="#4ea3ff", underline=True)
        self.text.tag_bind("link", "<Control-Button-1>", self.open_link)
        self.text.tag_bind("link", "<Enter>", self.enter_link)
        self.text.tag_bind("link", "<Leave>", self.leave_link)

    def open_link(self, event):
        index = self.text.index(f"@{event.x},{event.y}")

        for tag_range in self.text.tag_ranges("link"):
            pass

        ranges = self.text.tag_ranges("link")

        for i in range(0, len(ranges), 2):
            start = ranges[i]
            end = ranges[i + 1]

            if self.text.compare(index, ">=", start) and self.text.compare(
                index, "<", end
            ):
                url = self.text.get(start, end)
                webbrowser.open(url)
                break

    # ======================
    # キーバインド
    # ======================
    def bind_events(self):
        self.win.bind("<Control-s>", self.save_file)
        self.win.bind("<Control-o>", self.open_file)
        self.win.bind("<Control-t>", self.toggle_topmost)
        self.win.bind("<Control-n>", self.new_window)
        self.win.bind("<Control-q>", self.quit_window)
        self.text.bind("<Button-1>", self.start_move)
        self.text.bind("<B1-Motion>", self.do_move)
        self.text.bind("<Button-3>", self.show_menu)
        self.text.bind("<Leave>", lambda e: self.update_links())
        self.text.bind("<Control-Shift-H>", all_windows_hide)
        self.text.bind("<Control-Shift-Z>", all_windows_hide)


# Ctrl+Shift+H　全ウィンドウの非表示
def all_windows_hide(event=None):
    def _run():
        any_visible = any(w.win.winfo_viewable() for w in MemoWindow.windows)
        if any_visible:
            for w in MemoWindow.windows:
                w.win.iconify()
        else:
            for w in MemoWindow.windows:
                w.win.deiconify()
                w.force_focus()

    if MemoWindow.windows:
        MemoWindow.windows[0].win.after(0, _run)


# Darker color
def darker(color, amount=18):
    color = color.lstrip("#")

    r = max(0, int(color[0:2], 16) - amount)
    g = max(0, int(color[2:4], 16) - amount)
    b = max(0, int(color[4:6], 16) - amount)

    return f"#{r:02x}{g:02x}{b:02x}"


# ======================
# Main
# ======================
if __name__ == "__main__":
    app = MemoWindow()
    app.win.mainloop()
