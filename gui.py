import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, sys, os

class CarCheckGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('CarCheck Launcher')
        self.root.geometry('420x220')

        self.source_var = tk.StringVar(value='0')
        self.proc = None
        self._ui()

    def _add(self, parent, widget, **opts):
        return widget(parent, **opts)

    def _ui(self):
        frame = self._add(self.root, tk.Frame)
        frame.pack(padx=10, pady=10, fill='x')

        self._add(frame, tk.Label, text='Nguồn (0 cho webcam hoặc đường dẫn video):').pack(anchor='w')
        self._add(frame, tk.Entry, textvariable=self.source_var, width=50).pack(fill='x')

        btn_frame = self._add(self.root, tk.Frame)
        btn_frame.pack(padx=10, pady=8, fill='x')

        self._add(btn_frame, tk.Button, text='Chọn file...', command=lambda: self._action("choose")).pack(side='left')
        self._add(btn_frame, tk.Button, text='Start', command=lambda: self._action("start"),
                  bg='#4CAF50', fg='white').pack(side='left', padx=6)
        self._add(btn_frame, tk.Button, text='Stop', command=lambda: self._action("stop"),
                  bg='#f44336', fg='white').pack(side='left')

        self.status_label = self._add(self.root, tk.Label, text='Dừng', anchor='w')
        self.status_label.pack(fill='x', padx=10)

    def _action(self, mode):
        if mode == "choose":
            path = filedialog.askopenfilename(
                title='Chọn file video',
                filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv *.png *.jpg'),
                           ('All files', '*.*')]
            )
            if path:
                self.source_var.set(path)
            return

        if mode == "start":
            if self.proc and self.proc.poll() is None:
                messagebox.showinfo('Đang chạy', 'CarCheck đang chạy')
                return

            source = self.source_var.get().strip()
            if not source:
                messagebox.showwarning('Lỗi', 'Vui lòng nhập nguồn (0 cho webcam) hoặc chọn file')
                return

            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, 'main.py')
            cmd = [sys.executable or 'python', script_path, "--source", source]

            try:
                self.proc = subprocess.Popen(cmd, cwd=current_dir)
                self.status_label.config(text=f'Đang chạy: {source} (PID {self.proc.pid})')
            except Exception as e:
                messagebox.showerror('Lỗi', f'Không thể khởi động CarCheck:\n{e}')
            return

        if mode == "stop":
            if not self.proc or self.proc.poll() is not None:
                messagebox.showinfo('Không có tiến trình', 'Không có CarCheck đang chạy')
                return
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.status_label.config(text='Dừng')

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CarCheckGUI().run()

