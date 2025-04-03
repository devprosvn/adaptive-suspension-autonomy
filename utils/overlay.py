import cv2

REAL_CLASSES = {
    0: "road",
    1: "pavement",
    2: "grass",
    3: "dirt",
    4: "obstacle"
}

def draw_overlay_terrain(img, terrain_label: str, fps: float, weather=None):
    """
    Vẽ overlay nhãn class + thời tiết + FPS lên khung hình
    """
    lines = [f"{terrain_label.upper()} | FPS: {fps:.2f}"]

    if weather:
        lines.append(f"☁️ Clouds: {weather.cloudiness:.1f}%")
        lines.append(f"🌧️ Rain: {weather.precipitation:.1f}%")
        lines.append(f"🌫️ Fog: {weather.fog_density:.1f}%")
        lines.append(f"💧 Wetness: {weather.wetness:.1f}%")
        lines.append(f"☀️ Sun: {weather.sun_altitude_angle:.1f}°")

    org_y = 25
    for line in lines:
        org = (10, org_y)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        thickness = 1

        text_size, _ = cv2.getTextSize(line, font, font_scale, thickness)
        box_coords = ((org[0] - 5, org[1] - 20), (org[0] + text_size[0] + 5, org[1] + 5))
        cv2.rectangle(img, box_coords[0], box_coords[1], (0, 0, 0), cv2.FILLED)
        cv2.putText(img, line, org, font, font_scale, color, thickness, cv2.LINE_AA)
        org_y += 30

    return img