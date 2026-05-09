# EasySticky v1.3
import tkinter as tk
from tkinter import colorchooser
import tkinter.font as tkfont
from tkinter import filedialog
import keyboard


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

        self.win.geometry("400x500+100+100")
        self.win.overrideredirect(True)

        # Status
        self.topmost = True
        self.resizing = False

        self.win.attributes("-topmost", self.topmost)

        # Padding
        self.container = tk.Frame(self.win, bg="#e4e093", padx=5, pady=5)
        self.container.pack(expand=True, fill="both")

        # root marker
        if self.root_flag:
            self.corner = tk.Canvas(
                self.win,
                width=18,
                height=18,
                bg=darker(self.container["bg"], 14),
                highlightthickness=0,
            )

            self.corner.place(x=0, y=0)

            self.corner.create_polygon(
                0, 0, 18, 0, 0, 18, fill=darker(self.corner["bg"], 20), outline=""
            )

        # Default font
        self.font_name = "Courier"
        self.font_size = 16
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
            font=(self.font_name, self.font_size),
        )
        self.text.pack(expand=True, fill="both", padx=5, pady=5)

        # Close guide panel
        self.close_btn = tk.Label(
            self.win, width=2, height=1, bg="#e4a48f", cursor="hand2"
        )
        self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")
        # Resize guide panel
        self.grip = tk.Label(self.win, width=4, height=2, bg="#938d69", cursor="hand2")
        self.grip.place(relx=1.0, rely=1.0, anchor="se")

        # Hide panels
        self.close_btn.place_forget()
        self.grip.place_forget()

        def show_panels(event=None):
            self.close_btn.place(relx=1.0, rely=0.0, anchor="ne")
            self.grip.place(relx=1.0, rely=1.0, anchor="se")

        def hide_panels(event=None):
            self.close_btn.place_forget()
            self.grip.place_forget()

        self.win.bind("<Enter>", show_panels)
        self.win.bind("<Leave>", hide_panels)

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
            if self.root_flag:
                self.corner.config(bg=darker(self.bg_color, 14))
                self.corner.delete("all")
                self.corner.create_polygon(
                    0, 0, 18, 0, 0, 18, fill=darker(self.bg_color, 20), outline=""
                )

    def choose_font_color(self) -> None:
        color = colorchooser.askcolor(title="Choose Font Color")
        if color[1]:
            self.font_color = color[1]
            self.text.config(fg=self.font_color)

    # focus
    def force_focus(self):
        self.win.overrideredirect(False)
        self.win.update()

        self.win.lift()
        self.win.attributes("-topmost", True)

        self.text.focus_set()

        self.win.after(50, lambda: self.win.attributes("-topmost", self.topmost))
        self.win.after(100, lambda: self.win.overrideredirect(True))

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

    # Resize window by dragging grip
    def start_resize(self, event):
        self.resizing = True
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_w = self.win.winfo_width()
        self.start_h = self.win.winfo_height()

    def do_resize(self, event):
        if not self.resizing:
            return

        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        w = max(100, self.start_w + dx)
        h = max(100, self.start_h + dy)

        self.win.geometry(f"{w}x{h}")

    def stop_resize(self, event):
        self.resizing = False

    # ======================
    # Key Bindings
    # ======================
    def bind_events(self):
        self.win.bind("<Control-s>", self.save_file)
        self.win.bind("<Control-o>", self.open_file)
        self.win.bind("<Control-t>", self.toggle_topmost)
        self.win.bind("<Control-n>", self.new_window)
        self.win.bind("<Control-q>", self.quit_window)
        self.close_btn.bind("<Button-1>", self.quit_window)
        self.text.bind("<Button-1>", self.start_move)
        self.text.bind("<B1-Motion>", self.do_move)
        self.text.bind("<Button-3>", self.show_menu)

        self.grip.bind("<Button-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.do_resize)
        self.grip.bind("<ButtonRelease-1>", self.stop_resize)


# Toggle all windows show/hide by Ctrl+Shift+H
all_windows_visible = True


def all_windows_show(event=None):
    def _run():
        global all_windows_visible
        all_windows_visible = not all_windows_visible
        for i, w in enumerate(MemoWindow.windows):
            if all_windows_visible:
                w.win.deiconify()
                w.force_focus()
            else:
                w.win.overrideredirect(False)
                w.win.iconify()

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
    # Toggle all windows key
    keyboard.add_hotkey("ctrl+Shift+h", all_windows_show)
    app.win.mainloop()
