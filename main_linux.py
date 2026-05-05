# EasySticky_linux_v1.1
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog
from tkinter import colorchooser


class MemoWindow:
    windows: list["MemoWindow"] = []

    def __init__(self, root=None):
        # root or toplevel
        if root is None:
            self.win = tk.Tk()
            # Only root window handles autosave
            self.root_flag = True
        else:
            self.win = tk.Toplevel(root)
            self.root_flag = False

        # Position + gap
        offset = len(MemoWindow.windows) * 30
        self.win.geometry(f"400x500+{100 + offset}+{100 + offset}")
        # self.win.overrideredirect(True)
        self.win.title("")
        self.win.configure(bg="#e4e093")

        # Status
        self.topmost = True
        self.resizing = False

        self.win.attributes("-topmost", self.topmost)

        # Padding
        self.container = tk.Frame(
            self.win, bg="#e4e093", padx=5, pady=5, bd=0, highlightthickness=0
        )
        self.container.pack(expand=True, fill="both")
        # Text
        self.text = tk.Text(
            self.container,
            wrap="word",
            bg="#e4e093",
            fg="#000000",
            insertbackground="black",
            borderwidth=0,
            highlightthickness=0,
            undo=True,
            font=("Courier", 16),
        )
        self.text.pack(expand=True, fill="both")

        # Default Font
        self.font_name = "Courier"
        self.font_size = 16
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
        self.all_fonts = sorted(tkfont.families())
        font_menu = tk.Menu(self.menu, tearoff=0)
        # Common fonts
        common_menu = tk.Menu(font_menu, tearoff=0)
        for f in self.common_fonts:
            common_menu.add_radiobutton(
                label=f,
                font=(f, 12),
                variable=self.font_var,
                value=f,
                command=lambda f=f: self.set_font(f),
            )
        font_menu.add_cascade(label="Common Fonts", menu=common_menu)

        # All fonts
        all_menu = tk.Menu(font_menu, tearoff=0)
        font_menu.add_separator()
        for f in self.all_fonts:
            all_menu.add_radiobutton(
                label=f,
                font=(f, 12),
                variable=self.font_var,
                value=f,
                command=lambda f=f: self.set_font(f),
            )
        font_menu.add_cascade(label="All Fonts", menu=all_menu)
        self.menu.add_cascade(label="Font", menu=font_menu)

        # Size
        self.size_var = tk.IntVar(value=self.font_size)
        size_menu = tk.Menu(self.menu, tearoff=0)
        for s in [10, 12, 14, 16, 18, 20, 24]:
            size_menu.add_radiobutton(
                label=str(s),
                variable=self.size_var,
                value=s,
                command=lambda s=s: self.set_size(s),
            )

        self.menu.add_cascade(label="Size", menu=size_menu)
        # --- bind ---
        self.bind_events()

        # Color settings
        color_menu = tk.Menu(self.menu, tearoff=0)

        color_menu.add_command(label="Background Color", command=self.choose_bg_color)
        color_menu.add_command(label="Font Color", command=self.choose_font_color)
        self.menu.add_cascade(label="Color", menu=color_menu)

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
    def choose_bg_color(self) -> None:
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:
            self.bg_color = color[1]
            self.text.config(bg=self.bg_color)
            self.container.config(bg=self.bg_color)

    def choose_font_color(self) -> None:
        color = colorchooser.askcolor(title="Choose Font Color")
        if color[1]:
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
        self.font_name = font
        self.font_var.set(font)
        self.apply_font()

    def set_size(self, size):
        self.font_size = size
        self.size_var.set(size)
        self.apply_font()

    def apply_font(self):
        self.text.config(font=(self.font_name, self.font_size))

    # Right-click Menu
    def show_menu(self, event=None):
        self.font_var.set(self.font_name)
        self.size_var.set(self.font_size)
        self.menu.tk_popup(event.x_root, event.y_root)

    # Save Ctrl+S
    def save_file(self, event=None):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))

    # Open Ctrl+O
    def open_file(self, event=None):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, f.read())

    # Close Ctrl+Q
    def quit_window(self, event=None):
        self.auto_save()
        MemoWindow.windows.remove(self)
        self.win.destroy()

    # Toggle topmost Ctrl+T
    def toggle_topmost(self, event=None):
        self.topmost = not self.topmost
        self.win.attributes("-topmost", self.topmost)

    # New window Ctrl+N
    def new_window(self, event=None):
        new = MemoWindow(self.win)
        new.font_name = self.font_name
        new.font_size = self.font_size
        new.size_var.set(new.font_size)
        new.apply_font()

    # Auto Save restricted to root window by self.root_flag
    def auto_save(self):
        if not self.root_flag:
            return
        idx = MemoWindow.windows.index(self)
        with open(f"autosave_{idx}.txt", "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", tk.END))
        self.win.after(5000, self.auto_save)

    # Move window by dragging text area
    def start_move(self, event):
        self.win.x = event.x
        self.win.y = event.y

    def do_move(self, event):
        x = self.win.winfo_pointerx() - self.win.x
        y = self.win.winfo_pointery() - self.win.y
        self.win.geometry(f"+{x}+{y}")

    # ======================
    # Key Bindings
    # ======================
    def bind_events(self):
        self.win.bind("<Control-s>", self.save_file)
        self.win.bind("<Control-o>", self.open_file)
        self.win.bind("<Control-t>", self.toggle_topmost)
        self.win.bind("<Control-n>", self.new_window)
        self.win.bind("<Control-q>", self.quit_window)
        self.win.bind("<Control-w>", self.quit_window)
        self.text.bind("<Button-1>", self.start_move)
        self.text.bind("<B1-Motion>", self.do_move)
        self.text.bind("<Button-3>", self.show_menu)

        self.text.bind("<Control-Shift-H>", all_windows_hide)


# Hide all windows
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


# ======================
# Main
# ======================
if __name__ == "__main__":
    app = MemoWindow()
    app.win.mainloop()
