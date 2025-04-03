import carla
import numpy as np
import cv2
import torch
import torchvision.transforms as T
import time
import random
import csv
from utils.overlay import draw_overlay_terrain
from agents.terrain_classifier import MobileViTClassifier
from utils.overlay import REAL_CLASSES

classifier = MobileViTClassifier(model_path="models/mobilevit_fp16.pt")


def preview_camera_rgb(client, world, vehicle, image_size=(160, 120), save_csv=True):
    camera = None
    csv_file = None
    csv_writer = None

    try:
        vehicle.set_autopilot(True)
        spectator = world.get_spectator()

        # Spawn camera
        blueprint_lib = world.get_blueprint_library()
        camera_bp = blueprint_lib.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '640')
        camera_bp.set_attribute('image_size_y', '480')
        camera_bp.set_attribute('fov', '90')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

        transform = T.Compose([
            T.ToPILImage(),
            T.Resize(image_size),
            T.ToTensor()
        ])

        # Ghi log nếu cần
        if save_csv:
            csv_file = open('logs/terrain_log.csv', mode='w', newline='', encoding='utf-8-sig')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                "timestamp", "terrain_label", "class_id", "fps",
                "location_x", "location_y", "location_z",
                "cloudiness", "precipitation", "fog_density",
                "wetness", "sun_altitude_angle"
            ])

        print("🎥 Camera preview đang chạy... Nhấn ESC để thoát.")
        frame_count = 0
        t_start = time.time()

        def process_image(image):
            nonlocal frame_count
            frame_count += 1

            img_array = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))[:, :, :3]
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            img_resized = cv2.resize(img_rgb, image_size)
            tensor_img = transform(img_resized).unsqueeze(0).cuda().half()

            # Dự đoán địa hình
            class_id = classifier.predict_class(tensor_img)
            terrain_label = REAL_CLASSES.get(class_id, "unknown")
            fps = frame_count / (time.time() - t_start)

            # Lấy vị trí và thời tiết
            location = vehicle.get_location()
            weather = world.get_weather()

            print(f"[INFO] Terrain: {terrain_label.upper()} | FPS: {fps:.2f}")

            # Ghi vào CSV
            if csv_writer:
                csv_writer.writerow([
                    time.time(),
                    terrain_label,
                    class_id,
                    round(fps, 2),
                    round(location.x, 3),
                    round(location.y, 3),
                    round(location.z, 3),
                    round(weather.cloudiness, 2),
                    round(weather.precipitation, 2),
                    round(weather.fog_density, 2),
                    round(weather.wetness, 2),
                    round(weather.sun_altitude_angle, 2)
                ])

            # Overlay
            img_out = draw_overlay_terrain(img_resized, terrain_label, fps, weather)
            cv2.imshow("Camera RGB (160x120)", img_out)

            key = cv2.waitKey(1)
            if key == 27:
                camera.stop()
                cv2.destroyAllWindows()

        camera.listen(lambda image: process_image(image))

        while True:
            spectator.set_transform(carla.Transform(
                vehicle.get_transform().location + carla.Location(z=40),
                carla.Rotation(pitch=-90)
            ))

            key = cv2.waitKey(1)
            if key == 27:
                print("👋 ESC detected. Exiting loop...")
                break

            time.sleep(0.03)

    finally:
        print("🧹 Đang dọn camera và xe...")
        if camera is not None and camera.is_listening:
            camera.stop()
        if camera is not None:
            camera.destroy()
        if vehicle is not None:
            vehicle.destroy()
        if csv_file:
            csv_file.close()
        cv2.destroyAllWindows()