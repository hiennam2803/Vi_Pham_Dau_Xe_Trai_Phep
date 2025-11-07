import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os

class CarCheckGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('CarCheck Launcher')
        self.root.geometry('420x220')
        
        self.source_var = tk.StringVar(value='0')
        self.proc = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup giao diện"""
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill='x')
        
        lbl = tk.Label(frame, text='Nguồn (0 cho webcam hoặc đường dẫn video):')
        lbl.pack(anchor='w')
        
        entry = tk.Entry(frame, textvariable=self.source_var, width=50)
        entry.pack(fill='x')
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(padx=10, pady=8, fill='x')
        
        choose_btn = tk.Button(btn_frame, text='Chọn file...', command=self.choose_file)
        choose_btn.pack(side='left')
        
        start_btn = tk.Button(btn_frame, text='Start', command=self.start_carcheck, bg='#4CAF50', fg='white')
        start_btn.pack(side='left', padx=6)
        
        stop_btn = tk.Button(btn_frame, text='Stop', command=self.stop_carcheck, bg='#f44336', fg='white')
        stop_btn.pack(side='left')
        
        self.status_label = tk.Label(self.root, text='Dừng', anchor='w')
        self.status_label.pack(fill='x', padx=10)
        
    def choose_file(self):
        """Chọn file video"""
        path = filedialog.askopenfilename(
            title='Chọn file video',
            filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv'), ('All files', '*.*')]
        )
        if path:
            self.source_var.set(path)
            
    def start_carcheck(self):
        """Khởi động tiến trình CarCheck"""
        if self.proc is not None and self.proc.poll() is None:
            messagebox.showinfo('Đang chạy', 'CarCheck đang chạy')
            return
            
        source = self.source_var.get().strip()
        if source == '':
            messagebox.showwarning('Lỗi', 'Vui lòng nhập nguồn (0 cho webcam) hoặc chọn file')
            return
            
        # Dẫn đường đến file main.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, 'main.py')
        pyexe = sys.executable or 'python'

        # Nếu main.py nằm trong package Viphamdauxe, ta chạy theo dạng module
        cmd = [pyexe, "-m", "Viphamdauxe.main", "--source", source]
        print("Chạy lệnh:", " ".join(cmd))
        
        try:
            self.proc = subprocess.Popen(cmd, cwd=os.path.dirname(current_dir))
            self.status_label.config(text=f'Đang chạy: {source} (PID {self.proc.pid})')
        except Exception as e:
            messagebox.showerror('Lỗi', f'Không thể khởi động CarCheck:\n{e}')
            
    def stop_carcheck(self):
        """Dừng CarCheck"""
        if self.proc is None or self.proc.poll() is not None:
            messagebox.showinfo('Không có tiến trình', 'Không có CarCheck đang chạy')
            return
            
        self.proc.terminate()
        self.proc.wait(timeout=5)
        self.status_label.config(text='Dừng')
        
    def run(self):
        """Chạy GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    gui = CarCheckGUI()
    gui.run()
