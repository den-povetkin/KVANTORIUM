import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Негр ты или белый
    lower = np.array([0, 20, 70], dtype=np.uint8)
    upper = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)

    # режет шум
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    kernel = np.ones((3, 3))
    mask = cv2.dilate(mask, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)

        if cv2.contourArea(max_contour) > 3000:
            hull = cv2.convexHull(max_contour)
            cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)
            cv2.drawContours(frame, [hull], -1, (255, 0, 0), 2)

            hull_indices = cv2.convexHull(max_contour, returnPoints=False)
            defects = cv2.convexityDefects(max_contour, hull_indices)

            if defects is not None:
                count = 0
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(max_contour[s][0])
                    end = tuple(max_contour[e][0])
                    far = tuple(max_contour[f][0])

                    # залупа чтобы пальцы определить
                    if d > 8000:
                        count += 1
                        cv2.circle(frame, far, 5, (0, 0, 255), -1)

                # показывает че понял
                if count == 0:
                    gesture = "✊ Кулак"
                elif count == 1:
                    gesture = "👍 Один палец"
                elif count == 2:
                    gesture = "✌️ Два пальца"
                elif count == 3:
                    gesture = "Три пальца"
                elif count == 4:
                    gesture = "🖐 Пять пальцев"
                else:
                    gesture = "Неизвестный жест"

                cv2.putText(frame, gesture, (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2)

    cv2.imshow("Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # чтобы съебаться тык ESC
        break

cap.release()
cv2.destroyAllWindows()
