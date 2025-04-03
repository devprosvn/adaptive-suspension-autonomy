from utils.camera_preview import preview_camera_rgb
import carla
import random
import math
import os
import subprocess
import time


def distance(loc1, loc2):
    return math.sqrt((loc1.x - loc2.x)**2 + (loc1.y - loc2.y)**2)


def spawn_vehicle_nearby(world, center_location, radius=80.0):
    blueprint_lib = world.get_blueprint_library()
    vehicle_bp = blueprint_lib.filter('vehicle.carlamotors.carlacola')[0]  # Xe off-road
    spawn_points = world.get_map().get_spawn_points()
    nearby_spawns = [sp for sp in spawn_points if distance(sp.location, center_location) <= radius]
    random.shuffle(nearby_spawns)

    for spawn_point in nearby_spawns:
        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        if vehicle is not None:
            print("🚗 Spawned vehicle near", center_location, "→ at", spawn_point.location)

            # ⚙️ Tăng lực kéo
            physics = vehicle.get_physics_control()
            physics.max_rpm = 6000
            physics.torque_curve = [(0.0, 400.0), (0.5, 500.0), (1.0, 400.0)]
            physics.damping_rate_full_throttle = 0.15
            vehicle.apply_physics_control(physics)

            return vehicle

    raise RuntimeError("❌ Không tìm được vị trí spawn trong vùng lân cận.")


if __name__ == "__main__":
    # 🚀 Chạy dynamic_weather song song
    subprocess.Popen(["python", "utils/dynamic_weather.py"])
    time.sleep(2)

    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(10.0)

    # Tải map phù hợp
    world = client.load_world('Town03')

    # Lấy vị trí camera hiện tại
    spectator = world.get_spectator()
    center_location = spectator.get_transform().location

    # Tạo thư mục log
    os.makedirs("logs", exist_ok=True)

    # Spawn xe & chạy camera preview
    vehicle = spawn_vehicle_nearby(world, center_location)
    preview_camera_rgb(client=client, world=world, vehicle=vehicle)