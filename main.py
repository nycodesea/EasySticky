# EasySticky v1.0
import tkinter as tk
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

        # --- bind ---
        self.bind_events()

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

    # ======================
    # Functions
    # ======================
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
        MemoWindow(self.win)

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

        self.grip.bind("<Button-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.do_resize)
        self.grip.bind("<ButtonRelease-1>", self.stop_resize)


# Toggle all windows show/hide by Ctrl+H
all_windows_visible = True


def all_windows_show(event=None):
    def _run():
        global all_windows_visible
        all_windows_visible = not all_windows_visible
        for w in MemoWindow.windows:
            if all_windows_visible:
                w.win.deiconify()
                w.win.overrideredirect(True)
                w.win.lift()
                w.win.focus_force()
                w.win.attributes("-topmost", w.topmost)
            else:
                w.win.overrideredirect(False)
                w.win.iconify()

    MemoWindow.windows[0].win.after(0, _run)


# ======================
# Main
# ======================
if __name__ == "__main__":
    app = MemoWindow()
    # Toggle all windows key
    keyboard.add_hotkey("ctrl+h", all_windows_show)
    app.win.mainloop()
