from time import sleep

import cv2
import requests

from client.config import SERVER_URL, CLASS_NAME


def recognize_live(camera_index: int = 0):
    """
    Снимает потоки с камеры и отправляет кадры на сервер
    для распознавания. Выводит имена распознанных студентов.
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")
    sleep(0.5)
    print("Start live recognition. Press q to stop.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {
            'file': (
                'frame.jpg',
                img_encoded.tobytes(),
                'image/jpeg'
            )
        }
        data = {'mode': 'recognize', 'class_name': CLASS_NAME}

        # Инициализируем список до запроса
        names = []
        try:
            resp = requests.post(f"{SERVER_URL}/recognize", files=files, data=data)
            if resp.status_code == 200 and resp.text:
                try:
                    result = resp.json()
                    if isinstance(result, dict):
                        names = result.get('recognized_students', []) or []
                except ValueError:
                    print("Warning: Server returned non-JSON response:", resp.text)
            else:
                print(f"Warning: Server responded with status {resp.status_code}")
        except requests.RequestException as e:
            print(f"Error during recognition request: {e}")

        # Отображаем имена и рамки
        for idx, name in enumerate(names):
            cv2.putText(frame, name, (10, 30 + 30 * idx), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Live Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)
        sleep(30)

    cap.release()
    cv2.destroyAllWindows()
