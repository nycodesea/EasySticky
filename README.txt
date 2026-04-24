# EasySticky

A simple and lightweight sticky notes app built with Tkinter.

Supports multiple windows, always-on-top mode, and auto-save window.

---

## 🖼️ Screenshot

![EasySticky Screenshot](assets/screenshot.png)

---

## ✨ Features

* Frameless sticky-note style UI
* Multiple memo windows
* Toggle always-on-top
* Drag to move and resize
* Auto-save with restore on restart

---

## 🚀 Usage

```bash
python main.py
```

---

## ⌨️ Controls

### Keyboard

* **Ctrl + O** : Open file
* **Ctrl + S** : Save file
* **Ctrl + T** : Toggle always-on-top
* **Ctrl + N** : Open new memo window
* **Ctrl + Q** : Close window (or exit app if root)
* **Ctrl + H** : Show / hide all windows

### Mouse

* **Drag (text area)** : Move window
* **Drag bottom-right** : Resize window
* **Click top-right** : Close window

---

## 💾 Auto Save

The first window opened (root window) is treated specially:

* Automatically saved to `autosave_0.txt`
* Restored when the app restarts

⚠️ **Warning**
Do not manually edit or save to `autosave_0.txt`, as it will be overwritten.

---

## 📦 Requirements

* Python 3.x

### Additional dependency

```bash
pip install keyboard
```

---

## 🛠️ Future Plans

* UI customization (colors, fonts)
* Toggle visibility of control panels
* Auto save functionality

---

## 📄 License

This project is licensed under the MIT License.


