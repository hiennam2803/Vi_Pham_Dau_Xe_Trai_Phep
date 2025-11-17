"""
Khởi động CarCheck từ command line, chọn chạy GUI hoặc xử lý video
"""
import argparse
import sys
from gui import CarCheckGUI
from video_processor import process_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CarCheck - Phát hiện vi phạm đậu xe trái phép')
    parser.add_argument('--source', type=str, 
                       help='Nguồn video (0 cho webcam hoặc đường dẫn file video). Nếu không có, sẽ khởi chạy GUI.')
    args = parser.parse_args()
    if args.source is not None:
        success = process_video(args.source)
        sys.exit(0 if success else 1)
    else:
        gui = CarCheckGUI()
        gui.run()