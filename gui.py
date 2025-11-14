import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
import subprocess
import sys
import os
import ast
import pprint
import importlib
import re


class CarCheckGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('CarCheck — Launcher')
        self._center_window(520, 260)

        # Use ttk theme when available and define some button styles
        try:
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Accent.TButton', foreground='white', background='#4CAF50')
            style.configure('Danger.TButton', foreground='white', background='#f44336')
        except Exception:
            pass

        self.source_var = tk.StringVar(value='0')
        self.proc = None

        self._ui()

    def _add(self, parent, widget, **opts):
        """Create widgets preferring ttk equivalents for basic widgets."""
        mapping = {tk.Label: ttk.Label, tk.Entry: ttk.Entry, tk.Button: ttk.Button, tk.Frame: ttk.Frame}
        Widget = mapping.get(widget, widget)
        return Widget(parent, **opts)

    def _ui(self):
        pad = {'padx': 12, 'pady': 8}
        frame = self._add(self.root, tk.Frame)
        frame.pack(fill='both', expand=True, **pad)

        title_font = font.Font(weight='bold', size=12)

        # Top bar with gear icon at left
        top_bar = self._add(frame, tk.Frame)
        top_bar.pack(fill='x')

        # Gear button (unicode gear) — opens config file in editor
        self.gear_btn = self._add(top_bar, tk.Button, text='⚙', width=3, command=self.open_config)
        self.gear_btn.pack(side='left')

        # Note: gear button will open editable config popup

        self._add(top_bar, tk.Label, text='CarCheck — Phát hiện vi phạm đậu xe', anchor='w', font=title_font).pack(side='left', padx=8)

        # Source input
        lbl = self._add(frame, tk.Label, text='Nguồn (0 cho webcam hoặc đường dẫn video):')
        lbl.pack(anchor='w', pady=(8, 0))

        entry = self._add(frame, tk.Entry, textvariable=self.source_var, width=60)
        entry.pack(fill='x')
        entry.bind('<Return>', lambda e: self._action('start'))

        # Buttons
        btn_frame = self._add(frame, tk.Frame)
        btn_frame.pack(fill='x', pady=8)

        self.choose_btn = self._add(btn_frame, tk.Button, text='Chọn file...', command=lambda: self._action('choose'))
        self.choose_btn.pack(side='left')

        self.start_btn = self._add(btn_frame, tk.Button, text='Start', command=lambda: self._action('start'), style='Accent.TButton')
        self.start_btn.pack(side='left', padx=8)

        self.stop_btn = self._add(btn_frame, tk.Button, text='Stop', command=lambda: self._action('stop'), style='Danger.TButton')
        self.stop_btn.pack(side='left')

        # NOTE: removed bottom 'Config' button — use top-left gear/info buttons instead

        # Status bar
        self.status_var = tk.StringVar(value='Dừng')
        self.status_label = self._add(self.root, tk.Label, textvariable=self.status_var, anchor='w')
        self.status_label.pack(fill='x', padx=12, pady=(0, 12))

        # initial button state
        self._set_running_state(False)

    def _action(self, mode):
        if mode == 'choose':
            path = filedialog.askopenfilename(
                title='Chọn file video',
                filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv *.png *.jpg'), ('All files', '*.*')]
            )
            if path:
                self.source_var.set(path)
            return

        if mode == 'start':
            if self.proc and self.proc.poll() is None:
                messagebox.showinfo('Đang chạy', 'CarCheck đang chạy')
                return

            source = self.source_var.get().strip()
            if not source:
                messagebox.showwarning('Lỗi', 'Vui lòng nhập nguồn (0 cho webcam) hoặc chọn file')
                return

            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, 'main.py')
            cmd = [sys.executable or 'python', script_path, '--source', source]

            try:
                self.proc = subprocess.Popen(cmd, cwd=current_dir)
                self.status_var.set(f'Đang chạy: {self._shorten_path(source)} (PID {self.proc.pid})')
                self._set_running_state(True)
            except Exception as e:
                messagebox.showerror('Lỗi', f'Không thể khởi động CarCheck:\n{e}')
            return

        if mode == 'stop':
            if not self.proc or self.proc.poll() is not None:
                messagebox.showinfo('Không có tiến trình', 'Không có CarCheck đang chạy')
                return
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except Exception:
                pass
            self.status_var.set('Dừng')
            self._set_running_state(False)

    def _set_running_state(self, running: bool):
        """Enable/disable controls depending on running state."""
        try:
            if running:
                self.start_btn.state(['disabled'])
                self.choose_btn.state(['disabled'])
                self.stop_btn.state(['!disabled'])
                # keep gear button enabled so user can edit config while running
                try:
                    self.gear_btn.state(['!disabled'])
                except Exception:
                    pass
            else:
                self.start_btn.state(['!disabled'])
                self.choose_btn.state(['!disabled'])
                self.stop_btn.state(['disabled'])
                try:
                    self.gear_btn.state(['!disabled'])
                except Exception:
                    pass
        except Exception:
            # Fallback to classic tk config when ttk state isn't available
            if running:
                self.start_btn.config(state='disabled')
                self.choose_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                try:
                    self.gear_btn.config(state='normal')
                except Exception:
                    pass
            else:
                self.start_btn.config(state='normal')
                self.choose_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                try:
                    self.gear_btn.config(state='normal')
                except Exception:
                    pass

    def open_config(self):
        """Open an editable popup for `config.Config` allowing inline edits and saving back to `config.py`."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cfg_path = os.path.join(current_dir, 'config.py')
            if not os.path.exists(cfg_path):
                messagebox.showwarning('Không tìm thấy', f'Không tìm thấy file cấu hình: {cfg_path}')
                return

            # import config module and read Config class attributes
            try:
                import config as cfg
                importlib.reload(cfg)
            except Exception as e:
                messagebox.showerror('Lỗi', f'Không thể nạp config module:\n{e}')
                return

            cfg_cls = getattr(cfg, 'Config', None)
            if cfg_cls is None:
                messagebox.showwarning('Không tìm thấy', 'Không tìm thấy class Config trong config.py')
                return

            attrs = [(name, getattr(cfg_cls, name)) for name in dir(cfg_cls) if name.isupper()]
            if not attrs:
                messagebox.showinfo('Rỗng', 'Không tìm thấy tham số cấu hình để chỉnh sửa.')
                return

            win = tk.Toplevel(self.root)
            win.title('Chỉnh sửa cấu hình')
            win.transient(self.root)
            win.geometry('640x480')

            container = ttk.Frame(win)
            container.pack(fill='both', expand=True, padx=8, pady=8)

            canvas = tk.Canvas(container)
            scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
            scroll_frame = ttk.Frame(canvas)

            scroll_frame.bind(
                '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
            )
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            editors = {}

            for r, (name, val) in enumerate(attrs):
                lbl = ttk.Label(scroll_frame, text=name)
                lbl.grid(row=r, column=0, sticky='w', padx=(2, 8), pady=6)

                # Choose editor widget by type
                if isinstance(val, bool):
                    var = tk.BooleanVar(value=val)
                    cb = ttk.Checkbutton(scroll_frame, variable=var)
                    cb.grid(row=r, column=1, sticky='w')
                    editors[name] = ('bool', var)
                elif isinstance(val, (int, float, str)):
                    ent = ttk.Entry(scroll_frame)
                    ent.insert(0, repr(val) if isinstance(val, str) and not val.isnumeric() else str(val))
                    ent.grid(row=r, column=1, sticky='we')
                    editors[name] = ('entry', ent)
                else:
                    # complex types (dict, list, etc.) - use Text
                    txt = tk.Text(scroll_frame, height=4, width=48)
                    txt.insert('1.0', pprint.pformat(val))
                    txt.grid(row=r, column=1, sticky='we')
                    editors[name] = ('text', txt)

            # make columns resize nicely
            scroll_frame.columnconfigure(1, weight=1)

            btn_frame = ttk.Frame(win)
            btn_frame.pack(fill='x', pady=(4, 8))

            def on_apply():
                new_values = {}
                # collect new values
                for name, (kind, widget) in editors.items():
                    try:
                        if kind == 'bool':
                            new_values[name] = bool(widget.get())
                        elif kind == 'entry':
                            s = widget.get().strip()
                            # Try to parse literal (numbers, strings with quotes, etc.)
                            try:
                                new_values[name] = ast.literal_eval(s)
                            except Exception:
                                # treat as plain string
                                new_values[name] = s
                        else:  # text
                            s = widget.get('1.0', 'end').strip()
                            try:
                                new_values[name] = ast.literal_eval(s)
                            except Exception:
                                new_values[name] = s
                    except Exception:
                        new_values[name] = None

                # attempt to write back to config.py using AST (safer than regex)
                try:
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        src = f.read()

                    tree = ast.parse(src)
                    changed = False

                    # find class Config
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef) and node.name == 'Config':
                            class_node = node
                            break
                    else:
                        class_node = None

                    if class_node is None:
                        raise RuntimeError('Không tìm thấy class Config trong file')

                    # helper to create AST value from Python object using literal source
                    def value_node_from(obj):
                        literal_src = pprint.pformat(obj)
                        assign_node = ast.parse(f"_TMP = {literal_src}").body[0]
                        return assign_node.value

                    for name, val in new_values.items():
                        new_val_node = value_node_from(val)
                        found = False
                        for item in class_node.body:
                            if isinstance(item, ast.Assign):
                                # only simple name targets
                                if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name) and item.targets[0].id == name:
                                    item.value = new_val_node
                                    changed = True
                                    found = True
                                    break
                        if not found:
                            # append new assignment to class body
                            assign = ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=new_val_node)
                            class_node.body.append(assign)
                            changed = True

                    if not changed:
                        # nothing to do
                        messagebox.showinfo('Không thay đổi', 'Không có thay đổi nào được phát hiện.')
                        return

                    # unparse AST back to source (requires Python 3.9+)
                    try:
                        new_src = ast.unparse(tree)
                    except Exception:
                        # fallback: raise so we don't write a broken file
                        raise RuntimeError('Không thể chuyển AST thành mã nguồn trên phiên bản Python này')

                    with open(cfg_path, 'w', encoding='utf-8') as f:
                        f.write(new_src)

                    # reload module and update in-memory Config
                    importlib.reload(cfg)
                    new_cfg_cls = getattr(cfg, 'Config', None)
                    if new_cfg_cls:
                        for name, val in new_values.items():
                            try:
                                setattr(new_cfg_cls, name, val)
                            except Exception:
                                pass

                    messagebox.showinfo('Lưu thành công', 'Cấu hình đã được cập nhật và lưu vào config.py')
                    win.destroy()
                except Exception as e:
                    messagebox.showerror('Lỗi', f'Không thể lưu cấu hình:\n{e}')

            def on_cancel():
                win.destroy()

            ttk.Button(btn_frame, text='Áp dụng', command=on_apply).pack(side='right', padx=6)
            ttk.Button(btn_frame, text='Hủy', command=on_cancel).pack(side='right')

        except Exception as e:
            messagebox.showerror('Lỗi', f'Không thể mở trình chỉnh sửa cấu hình:\n{e}')

    def show_config(self):
        """Show configuration parameters from `config.Config` in a popup window."""
        try:
            import config as cfg

            cfg_cls = getattr(cfg, 'Config', None)
            if cfg_cls is None:
                messagebox.showwarning('Không tìm thấy', 'Không tìm thấy class Config trong config.py')
                return

            lines = []
            for name in dir(cfg_cls):
                if name.isupper():
                    try:
                        val = getattr(cfg_cls, name)
                    except Exception:
                        val = '<error>'
                    lines.append(f'{name}: {val!r}')

            content = '\n'.join(lines) if lines else 'Không có tham số cấu hình.'

            win = tk.Toplevel(self.root)
            win.title('Thông số cấu hình')
            win.transient(self.root)
            win.geometry('560x360')

            txt = tk.Text(win, wrap='none')
            txt.insert('1.0', content)
            txt.config(state='disabled')
            txt.pack(fill='both', expand=True, padx=8, pady=8)

            btn = ttk.Button(win, text='Đóng', command=win.destroy)
            btn.pack(pady=(0, 8))

        except Exception as e:
            messagebox.showerror('Lỗi', f'Không thể hiển thị cấu hình:\n{e}')

    def _shorten_path(self, p: str, maxlen: int = 40) -> str:
        if len(p) <= maxlen:
            return p
        head = p[:20]
        tail = p[-(maxlen - 23):]
        return head + '...' + tail

    def _center_window(self, w: int, h: int):
        # position the window in the center of the screen
        self.root.update_idletasks()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    CarCheckGUI().run()
 

