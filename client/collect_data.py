import cv2
import time
import requests
import os
from config import USER_NAME, SERVER_URL


def collect_data(interval: float, output_dir: str, camera_index: int = 0):
    """
    Снимает фото через заданный интервал
    и отправляет их на сервер для сбора датасета с указанием USER_NAME.
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    os.makedirs(output_dir, exist_ok=True)
    count = 0
    print(f"Start data collection every {interval}s for user '{USER_NAME}'. Press q to stop.")
    sleep(1)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Collect Mode', frame)

        timestamp = int(time.time())
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)

        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'image/jpeg')}
            data = {'class_name': USER_NAME}  # Используем USER_NAME из config
            try:
                resp = requests.post(f"{SERVER_URL}/collect", files=files, data=data)
                print(f"Uploaded {filename}, status: {resp.status_code}")
                print(resp.text)
            except Exception as e:
                print(f"Error sending to server: {e}")

        count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(interval)

    print(f"Collected {count} frames.")
    cap.release()
    cv2.destroyAllWindows()
