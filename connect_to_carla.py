import socket
import time
import argparse
import sys

def check_port_open(host='127.0.0.1', port=2000, timeout=15, silent=False):
    """
    Kiểm tra xem có thể kết nối đến host:port qua socket TCP hay không
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                result = s.connect_ex((host, port))
                if result == 0:
                    if not silent:
                        print(f"✅ Port {port} đã mở trên {host}.")
                    return True
        except Exception as e:
            if not silent:
                print(f"⚠️ Lỗi khi kết nối socket: {e}")
        if not silent:
            print(f"⏳ Đang chờ port {port} mở trên {host}...")
        time.sleep(1)
    if not silent:
        print(f"❌ Không thể kết nối tới {host}:{port} trong {timeout} giây.")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--silent", action="store_true", help="Tắt log")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Địa chỉ host")
    parser.add_argument("--port", type=int, default=2000, help="Cổng kết nối")
    parser.add_argument("--timeout", type=int, default=15, help="Thời gian chờ kết nối")
    args = parser.parse_args()

    success = check_port_open(host=args.host, port=args.port, timeout=args.timeout, silent=args.silent)
    sys.exit(0 if success else 1)