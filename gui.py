import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import sys
import os
import webbrowser
import threading
import time
from datetime import datetime
import ast
import pprint
import importlib
from models.picturemodel import PictureModel
import uuid
class CarCheckGUI:
    """Giao diện chính của app CarCheck với các chức năng điều khiển, cấu hình, xem lịch sử."""
    def __init__(self):
        DB_FILE = "pictures.txt"
        self.root = tk.Tk()
        self.root.title('CarCheck — Phát hiện vi phạm đậu xe')
        self.root.configure(bg='#ffffff')
        self.root.geometry('1000x600')
        
        # Modern color scheme
        self.colors = {
            'primary': '#4361ee',
            'success': '#06d6a0', 
            'danger': '#ef476f',
            'accent': '#7209b7',
            'background': '#ffffff',
            'card_bg': '#f8f9fa',
            'text': '#2b2d42',
            'border': '#dee2e6'
        }
        
        self.source_var = tk.StringVar(value='0')
        self.proc = None
        self.violation_history = []  # Store violation data
        self._create_compact_ui()

    def _create_compact_ui(self):
        # Main container with two columns
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left column - Controls (60%)
        left_frame = tk.Frame(main_frame, bg=self.colors['background'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right column - Violation history (40%)
        right_frame = tk.Frame(main_frame, bg=self.colors['background'])
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # === LEFT COLUMN - CONTROLS ===
        
        # Header
        header_frame = tk.Frame(left_frame, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text='🚗 CarCheck - Phát hiện vi phạm đậu xe', 
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(expand=True)
        
        # Input section
        input_card = self._create_card(left_frame, "📹 NGUỒN VIDEO")
        input_card.pack(fill='x', pady=(0, 10))
        
        input_row = tk.Frame(input_card, bg=self.colors['card_bg'])
        input_row.pack(fill='x', pady=5)
        
        self.source_entry = tk.Entry(input_row, textvariable=self.source_var,
                                    font=('Segoe UI', 11), 
                                    relief='solid', bd=1)
        self.source_entry.pack(side='left', fill='x', expand=True, ipady=6)
        
        tk.Button(input_row, text='📁 Chọn file', font=('Segoe UI', 10),
                 command=self._choose_file, bg=self.colors['primary'],
                 fg='white', relief='flat').pack(side='left', padx=(10,0))
        
        # Control buttons - compact layout
        control_card = self._create_card(left_frame, "🎮 ĐIỀU KHIỂN")
        control_card.pack(fill='x', pady=(0, 10))
        
        # First row of buttons
        btn_row1 = tk.Frame(control_card, bg=self.colors['card_bg'])
        btn_row1.pack(fill='x', pady=5)
        
        self.start_btn = tk.Button(btn_row1, text='🎬 BẮT ĐẦU',
                                  font=('Segoe UI', 11, 'bold'),
                                  bg=self.colors['success'],
                                  fg='white',
                                  relief='flat',
                                  command=self._start_detection)
        self.start_btn.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        self.stop_btn = tk.Button(btn_row1, text='⏹ DỪNG',
                                 font=('Segoe UI', 11, 'bold'),
                                 bg=self.colors['danger'],
                                 fg='white',
                                 relief='flat',
                                 state='disabled',
                                 command=self._stop_detection)
        self.stop_btn.pack(side='left', padx=5, fill='x', expand=True)
        
        # Second row of buttons
        btn_row2 = tk.Frame(control_card, bg=self.colors['card_bg'])
        btn_row2.pack(fill='x', pady=5)
        
        tk.Button(btn_row2, text='⚙ CẤU HÌNH',
                 font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['accent'],
                 fg='white',
                 relief='flat',
                 command=self.open_config).pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        tk.Button(btn_row2, text='🗺 BẢN ĐỒ',
                 font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['primary'],
                 fg='white',
                 relief='flat',
                 command=self._open_map).pack(side='left', padx=5, fill='x', expand=True)
        
        # Status display
        status_card = self._create_card(left_frame, "📊 TRẠNG THÁI")
        status_card.pack(fill='x')
        
        status_content = tk.Frame(status_card, bg=self.colors['card_bg'])
        status_content.pack(fill='x', pady=10)
        
        status_left = tk.Frame(status_content, bg=self.colors['card_bg'])
        status_left.pack(side='left')
        
        self.status_indicator = tk.Label(status_left, text='●', 
                                        font=('Arial', 20),
                                        bg=self.colors['card_bg'],
                                        fg=self.colors['danger'])
        self.status_indicator.pack(side='left', padx=(0, 10))
        
        self.status_var = tk.StringVar(value='Hệ thống đang dừng')
        tk.Label(status_left, textvariable=self.status_var,
                bg=self.colors['card_bg'], 
                font=('Segoe UI', 11, 'bold')).pack(side='left')
        
        # === RIGHT COLUMN - VIOLATION HISTORY ===
        
        history_card = tk.Frame(right_frame, bg=self.colors['card_bg'], 
                               relief='solid', bd=1, padx=15, pady=15)
        history_card.pack(fill='both', expand=True)
        
        # History header
        history_header = tk.Frame(history_card, bg=self.colors['card_bg'])
        history_header.pack(fill='x', pady=(0, 10))
        
        # --- XÓA hai nút Làm mới và Xuất báo cáo ---
        tk.Label(history_header, text='📋 LỊCH SỬ VI PHẠM',
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side='left')

        tk.Button(history_header, text='🔄 Làm mới',
                font=('Segoe UI', 11),
                bg=self.colors['primary'],
                fg='white',
                relief='flat',
                command=self._load_history_from_txt).pack(side='right', padx=(0, 5))


        # --- TreeView hiển thị lịch sử ---
        tree_frame = tk.Frame(history_card, bg=self.colors['card_bg'])
        tree_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')

        columns = ('time', 'license_plate', 'image', 'location')
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )

        # Set tiêu đề cột
        self.history_tree.heading('time', text='Thời gian')
        self.history_tree.heading('license_plate', text='Id')
        self.history_tree.heading('image', text='Ảnh vi phạm')
        self.history_tree.heading('location', text='Vị trí')

        # Set độ rộng cột
        self.history_tree.column('time', width=50)
        self.history_tree.column('license_plate', width=100)
        self.history_tree.column('image', width=200)
        self.history_tree.column('location', width=200)

        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.history_tree.yview)
        # Thêm sự kiện double click
        self.history_tree.bind("<Double-1>", self._on_history_tree_double_click)
        # ---- TỰ ĐỘNG LOAD TỪ TXT ----
        self._load_history_from_txt()
        

    @staticmethod
    def load_all_pictures():
        pictures = []

        if not os.path.exists("pictures.txt"):
            return pictures

        with open("pictures.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) != 5:
                    continue

                pic_id, img_path, lat, lon, timestamp = parts

                picture = PictureModel(
                    id=pic_id,
                    image_path=img_path,
                    lat=float(lat),
                    lon=float(lon),
                    timestamp=timestamp
                )
                pictures.append(picture)

        return pictures
        
    
    def _load_history_from_txt(self):
        """Load violation history from pictures.txt"""

        # Clear table
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        pictures = self.load_all_pictures()

        for pic in pictures:
            # Format timestamp để hiển thị đẹp
            try:
                time_str = datetime.strptime(pic.timestamp, "%Y%m%d_%H%M%S") \
                                    .strftime("%H:%M %d/%m")
            except:
                time_str = pic.timestamp
            img_name = os.path.basename(pic.image_path)
            self.history_tree.insert(
                "", "end",
                iid=str(uuid.uuid4()),
                values=(
                    time_str,
                    pic.id,                 # tạm xem id là biển số
                    img_name,
                    f"{pic.lat}, {pic.lon}"
                ),
                tags=(pic.image_path,)
            )

    def _create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors['card_bg'], 
                       relief='solid', bd=1, padx=15, pady=10)
        
        title_label = tk.Label(card, text=title,
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['card_bg'],
                              fg=self.colors['text'])
        title_label.pack(anchor='w')
        
        return card

    

    def _refresh_history(self):
        """Refresh violation history"""
        # Clear current data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # In real app, load from database
        self._add_sample_data()
        messagebox.showinfo("Thông báo", "Đã làm mới dữ liệu lịch sử vi phạm")

    def _export_report(self):
        """Export violation report"""
        # In real app, this would generate and save a report
        messagebox.showinfo("Xuất báo cáo", "Đã xuất báo cáo vi phạm thành công!")

    def _choose_file(self):
        path = filedialog.askopenfilename(
            title='Chọn file video',
            filetypes=[('Video files', '*.mp4 *.avi *.mov *.mkv'), ('All files', '*.*')]
        )
        if path:
            self.source_var.set(path)

    def _start_detection(self):
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
            self.status_var.set('🟢 Đang chạy...')
            self.status_indicator.config(fg=self.colors['success'])
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self._monitor_process()
            
            # self._simulate_new_violation()
            
        except Exception as e:
            messagebox.showerror('Lỗi', f'Không thể khởi động:\n{e}')


    def _stop_detection(self):
        if not self.proc or self.proc.poll() is not None:
            return
            
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except:
            pass
            
        self.status_var.set('Hệ thống đang dừng')
        self.status_indicator.config(fg=self.colors['danger'])
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def _monitor_process(self):
        if self.proc and self.proc.poll() is not None:
            self.status_var.set('Đã dừng')
            self.status_indicator.config(fg=self.colors['danger'])
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.proc = None
        else:
            self.root.after(500, self._monitor_process)

    def open_config(self):
        """Open configuration editor with modern design"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cfg_path = os.path.join(current_dir, 'config.py')
            if not os.path.exists(cfg_path):
                messagebox.showwarning('Không tìm thấy', f'Không tìm thấy file cấu hình: {cfg_path}')
                return

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

            # Create modern config window
            win = tk.Toplevel(self.root)
            win.title('Cấu hình CarCheck')
            win.transient(self.root)
            win.geometry('500x700')
            win.configure(bg=self.colors['background'])
            self._center_window_on_parent(win, 500, 700)

            # Header
            header = tk.Frame(win, bg=self.colors['primary'], height=60)
            header.pack(fill='x')
            header.pack_propagate(False)

            header_content = tk.Frame(header, bg=self.colors['primary'])
            header_content.pack(fill='both', padx=20, pady=15)

            title_font = ('Segoe UI', 14, 'bold')
            tk.Label(header_content, 
                    text='⚙ Cấu hình hệ thống CarCheck', 
                    font=title_font,
                    bg=self.colors['primary'],
                    fg='white').pack(side='left')

            # Container
            container = tk.Frame(win, bg=self.colors['background'], padx=15, pady=15)
            container.pack(fill='both', expand=True)

            # Scrollable content
            canvas = tk.Canvas(container, bg=self.colors['background'], highlightthickness=0)
            scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg=self.colors['background'])

            scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            editors = {}

            # --- MAP tiếng Việt cho từng tham số phổ biến ---
            CONFIG_VN_LABELS = {
                # ==== HIỂN THỊ ====
                'VISUALIZER_MODE': 'Chế độ hiển thị khung (Nhanh / Đơn giản / Đầy đủ)',
                'DRAW_VEHICLE_TRAILS': 'Vẽ đường di chuyển của xe',
                'DRAW_CONFIDENCE': 'Hiển thị % độ tin cậy YOLO',
                'MIN_DISPLAY_CONFIDENCE': 'Chỉ hiển thị box nếu độ tin cậy ≥ giá trị này',

                # ==== HÀNH VI XE ====
                'MOVE_THRESHOLD': 'Ngưỡng tốc độ: > giá trị này → xe đang di chuyển',
                'STOP_THRESHOLD': 'Ngưỡng tốc độ: < giá trị này → xe đang dừng',
                'MIN_FRAMES_STOP': 'Số frame liên tiếp để xác định xe đã dừng',
                'MIN_FRAMES_MOVE': 'Số frame liên tiếp để xác định xe đang di chuyển',

                # ==== LỌC YOLO ====
                'CONFIDENCE_THRESHOLD': 'Ngưỡng tin cậy YOLO tối thiểu',
                'VEHICLE_CONFIDENCE_THRESHOLDS': 'Ngưỡng tin cậy riêng từng loại xe',
                'MIN_BOX_AREA': 'Diện tích bbox nhỏ nhất (lọc nhiễu)',
                'MIN_BOX_WIDTH': 'Chiều rộng bbox nhỏ nhất',
                'MIN_BOX_HEIGHT': 'Chiều cao bbox nhỏ nhất',

                # ==== TRACKING ====
                'IOU_THRESHOLD': 'Ngưỡng IoU để ghép detection vào track',
                'MAX_TRACK_AGE': 'Track bị mất dấu quá số frame này → xoá',
                'MIN_TRACK_CONFIDENCE': 'Track có tin cậy trung bình thấp hơn → xoá',
                'MIN_DETECTIONS_TO_KEEP': 'Cần detect tối thiểu bao nhiêu lần để tạo track',
                'OCCLUSION_THRESHOLD': 'Số frame cho phép xe bị che khuất',
                'MISSING_SECONDS': 'Số giây tối đa xe mất dấu trước khi xoá',

                # ==== HIỆU NĂNG ====
                'DETECTION_INTERVAL': 'Số frame giữa mỗi lần YOLO chạy detect',
                'MODEL_IMG_SIZE': 'Kích thước input YOLO',
                'SKIP_FRAMES': 'Bỏ qua bao nhiêu frame giữa các lần xử lý',

                # ==== CHỤP VI PHẠM ====
                'VIOLATION_CAPTURE_ENABLED': 'Bật/tắt chụp ảnh xe vi phạm',
                'MAX_STOP_TIME_BEFORE_CAPTURE': 'Thời gian dừng (giây) trước khi chụp vi phạm',
                'CAPTURE_DIR': 'Thư mục lưu ảnh',
                'SAVE_FULL_FRAME': 'Lưu toàn bộ frame thay vì chỉ vùng xe',
                'CAPTURE_COOLDOWN': 'Thời gian cooldown mỗi xe (giây)',

                # ==== TÊN PHƯƠNG TIỆN ====
                'VEHICLE_NAMES': 'Tên hiển thị cho từng loại xe'
            }



            for r, (name, val) in enumerate(attrs):
                setting_card = tk.Frame(scroll_frame, bg=self.colors['card_bg'], pady=8)
                setting_card.pack(fill='x', pady=4)
                # Tiêu đề tiếng Việt hoặc tên biến
                label_text = CONFIG_VN_LABELS.get(name, name)
                name_font = ('Segoe UI', 10, 'bold')
                label = tk.Label(setting_card,
                    text=label_text,
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['card_bg'],
                    fg='#4D4D4D', anchor='w')
                label.pack(fill='x', pady=(0, 3))
                # Phụ đề: tên biến và kiểu
                subtitle = f"({name}: {type(val).__name__})"
                subtitle_label = tk.Label(setting_card, text=subtitle, font=('Segoe UI', 8, 'italic'),
                    bg=self.colors['card_bg'], fg='#999999', anchor='w')
                subtitle_label.pack(fill='x', pady=(0, 2))
                # Editor như logic cũ
                if isinstance(val, bool):
                    var = tk.BooleanVar(value=val)
                    cb_frame = tk.Frame(setting_card, bg=self.colors['card_bg'])
                    cb_frame.pack(fill='x')
                    cb = tk.Checkbutton(cb_frame,
                        variable=var,
                        text='Bật/Tắt',
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'],
                        selectcolor=self.colors['primary'],
                        font=('Segoe UI', 9))
                    cb.pack(side='left')
                    editors[name] = ('bool', var)
                elif isinstance(val, (int, float)):
                    var = tk.StringVar(value=str(val))
                    entry = tk.Entry(setting_card, textvariable=var, font=('Segoe UI', 9), bg='white', relief='solid', bd=1)
                    entry.pack(fill='x', pady=2)
                    editors[name] = ('number', var)
                elif isinstance(val, str):
                    entry = tk.Entry(setting_card, font=('Segoe UI', 9), bg='white', relief='solid', bd=1)
                    entry.insert(0, val)
                    entry.pack(fill='x', pady=2)
                    editors[name] = ('string', entry)
                else:
                    txt_frame = tk.Frame(setting_card, bg=self.colors['card_bg'])
                    txt_frame.pack(fill='x')
                    txt = tk.Text(txt_frame, height=3, font=('Consolas', 8), bg='#f8f9fa', relief='solid', bd=1)
                    txt.insert('1.0', pprint.pformat(val))
                    txt.pack(fill='x', pady=2)
                    editors[name] = ('text', txt)

            # Action buttons
            btn_frame = tk.Frame(win, bg=self.colors['background'], pady=10)
            btn_frame.pack(fill='x', padx=15)

            def on_apply():
                new_values = {}
                for name, (kind, widget) in editors.items():
                    try:
                        if kind == 'bool':
                            new_values[name] = bool(widget.get())
                        elif kind == 'number':
                            s = widget.get().strip()
                            if '.' in s:
                                new_values[name] = float(s)
                            else:
                                new_values[name] = int(s)
                        elif kind == 'string':
                            new_values[name] = widget.get().strip()
                        else:  # text
                            s = widget.get('1.0', 'end').strip()
                            try:
                                new_values[name] = ast.literal_eval(s)
                            except:
                                new_values[name] = s
                    except Exception as e:
                        messagebox.showerror('Lỗi', f'Lỗi khi xử lý giá trị {name}: {e}')
                        return

                # Save configuration
                try:
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        src = f.read()

                    tree = ast.parse(src)
                    changed = False

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef) and node.name == 'Config':
                            class_node = node
                            break
                    else:
                        class_node = None

                    if class_node is None:
                        raise RuntimeError('Không tìm thấy class Config trong file')

                    def value_node_from(obj):
                        literal_src = pprint.pformat(obj)
                        assign_node = ast.parse(f"_TMP = {literal_src}").body[0]
                        return assign_node.value

                    for name, val in new_values.items():
                        new_val_node = value_node_from(val)
                        found = False
                        for item in class_node.body:
                            if isinstance(item, ast.Assign):
                                if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name) and item.targets[0].id == name:
                                    item.value = new_val_node
                                    changed = True
                                    found = True
                                    break
                        if not found:
                            assign = ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=new_val_node)
                            class_node.body.append(assign)
                            changed = True

                    if not changed:
                        messagebox.showinfo('Không thay đổi', 'Không có thay đổi nào được phát hiện.')
                        return

                    try:
                        new_src = ast.unparse(tree)
                    except Exception:
                        raise RuntimeError('Không thể chuyển AST thành mã nguồn trên phiên bản Python này')

                    with open(cfg_path, 'w', encoding='utf-8') as f:
                        f.write(new_src)

                    importlib.reload(cfg)
                    messagebox.showinfo('Thành công', '✅ Cấu hình đã được cập nhật thành công!')
                    win.destroy()
                except Exception as e:
                    messagebox.showerror('Lỗi', f'Không thể lưu cấu hình:\n{e}')

            # Các nút cũng chỉnh Việt hóa rõ ràng
            save_btn = tk.Button(btn_frame,
                               text='💾 LƯU CẤU HÌNH',
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['success'],
                               fg='white',
                               relief='flat',
                               cursor='hand2',
                               bd=0,
                               padx=20,
                               pady=8,
                               command=on_apply)
            save_btn.pack(side='right', padx=(10, 0))
            cancel_btn = tk.Button(btn_frame,
                                 text='↩ ĐÓNG',
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['danger'],
                                 fg='white',
                                 relief='flat',
                                 cursor='hand2',
                                 bd=0,
                                 padx=20,
                                 pady=8,
                                 command=win.destroy)
            cancel_btn.pack(side='right')

        except Exception as e:
            messagebox.showerror('Lỗi', f'Không thể mở trình chỉnh sửa cấu hình:\n{e}')

    def _center_window_on_parent(self, window, w: int, h: int):
        window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)
        window.geometry(f'{w}x{h}+{x}+{y}')

    def _open_map(self):
        try:
            def start_server():
                sys.path.append("c:\\Users\\ASUS\\Desktop\\Viphamdauxe\\map")
                from map_server import start_server
                start_server()

            server_thread = threading.Thread(target=start_server)
            server_thread.daemon = True
            server_thread.start()
            time.sleep(2)
            webbrowser.open("http://127.0.0.1:5001")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở bản đồ: {e}")

    def _on_history_tree_double_click(self, event):
        item = self.history_tree.identify_row(event.y)
        if not item:
            return
        # Lấy path ảnh từ tag của item
        tags = self.history_tree.item(item, 'tags')
        if tags:
            img_path = tags[0]
            if os.path.exists(img_path):
                try:
                    os.startfile(img_path)
                except Exception as e:
                    messagebox.showerror("Không thể mở ảnh", str(e))
            else:
                messagebox.showerror("Lỗi", "File ảnh không tồn tại: " + img_path)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    CarCheckGUI().run()