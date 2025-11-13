import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
import subprocess
import sys
import os


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
            style.configure('Config.TButton', foreground='white', background='#2196F3')
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

        # Gear button (unicode gear) — opens config
        self.gear_btn = self._add(top_bar, tk.Button, text='⚙', width=3, command=self.open_config)
        self.gear_btn.pack(side='left')

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

        # Config button opens the config.py in the default editor
        self.config_btn = self._add(btn_frame, tk.Button, text='Config', command=self.open_config, style='Config.TButton')
        self.config_btn.pack(side='left', padx=(8, 0))

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
                self.config_btn.state(['disabled'])
            else:
                self.start_btn.state(['!disabled'])
                self.choose_btn.state(['!disabled'])
                self.stop_btn.state(['disabled'])
                self.config_btn.state(['!disabled'])
        except Exception:
            # Fallback to classic tk config when ttk state isn't available
            if running:
                self.start_btn.config(state='disabled')
                self.choose_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.config_btn.config(state='disabled')
            else:
                self.start_btn.config(state='normal')
                self.choose_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                self.config_btn.config(state='normal')

    def open_config(self):
        """Open the repository config.py in the default editor (Windows: os.startfile)."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cfg_path = os.path.join(current_dir, 'config.py')
            if not os.path.exists(cfg_path):
                messagebox.showwarning('Không tìm thấy', f'Không tìm thấy file cấu hình: {cfg_path}')
                return

            # Windows
            if hasattr(os, 'startfile'):
                os.startfile(cfg_path)
                return

            # macOS
            if sys.platform == 'darwin':
                subprocess.Popen(['open', cfg_path])
                return

            # Linux
            subprocess.Popen(['xdg-open', cfg_path])
        except Exception as e:
            messagebox.showerror('Lỗi', f'Không thể mở file cấu hình:\n{e}')

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
 

