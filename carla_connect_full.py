import argparse
import sys
import carla
import time

# Import lại từ script trước
from connect_to_carla import check_port_open

def connect_to_carla_api(host="127.0.0.1", port=2000, timeout=10, silent=False):
    """
    Kiểm tra port mở, sau đó kết nối Carla bằng API client chính thức
    """
    if not check_port_open(host, port, timeout=timeout, silent=silent):
        raise ConnectionError(f"❌ Không thể kết nối tới Carla server tại {host}:{port}")

    try:
        client = carla.Client(host, port)
        client.set_timeout(2.0)
        world = client.get_world()

        if world is None or world.get_map() is None:
            raise RuntimeError("⚠️ Carla đã kết nối nhưng chưa load world/map.")

        if not silent:
            print("✅ Kết nối Carla thành công qua carla.Client().")

        return client, world

    except Exception as e:
        raise RuntimeError(f"❌ Lỗi khi khởi tạo Carla Client: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Địa chỉ host")
    parser.add_argument("--port", type=int, default=2000, help="Cổng Carla")
    parser.add_argument("--timeout", type=int, default=10, help="Thời gian chờ kiểm tra port")
    parser.add_argument("--silent", action="store_true", help="Tắt log")

    args = parser.parse_args()

    try:
        client, world = connect_to_carla_api(
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            silent=args.silent
        )
    except Exception as e:
        print(e)
        sys.exit(1)