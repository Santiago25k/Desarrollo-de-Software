import cv2


class ROISelector:
    def __init__(self, window_name):
        self.window_name = window_name
        self.start = None
        self.end = None
        self.drawing = False
        self.roi = None

    # ---------------------- Mouse callback ----------------------
    def _mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = (x, y)
            self.end = (x, y)
            self.drawing = True

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.end = (x, y)
            self.drawing = False

            x1, y1 = self.start
            x2, y2 = self.end
            self.roi = (
                min(x1, x2),
                min(y1, y2),
                abs(x2 - x1),
                abs(y2 - y1),
            )

    # ---------------------- Selección estática ----------------------
    def select_static(self, frame):
        self.roi = None
        self.start = None
        self.end = None

        cv2.setMouseCallback(self.window_name, self._mouse)

        while True:
            temp = frame.copy()

            if self.start and self.end:
                cv2.rectangle(temp, self.start, self.end, (0, 255, 0), 2)

            cv2.putText(
                temp,
                "Arrastra el popup | ENTER confirmar | ESC cancelar",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            cv2.imshow(self.window_name, temp)
            key = cv2.waitKey(1) & 0xFF

            if key == 13 and self.roi:
                break
            if key == 27:
                self.roi = None
                break

        cv2.setMouseCallback(self.window_name, lambda *args: None)
        return self.roi

    # ---------------------- Generar grilla ----------------------
    def generate_grid(self, roi, rows, cols):
        """
        roi: (x, y, w, h)
        rows: cantidad de filas
        cols: cantidad de columnas
        devuelve lista de celdas [(x, y, w, h), ...]
        """
        x, y, w, h = roi
        cell_w = w // cols
        cell_h = h // rows
        cells = []
        for r in range(rows):
            for c in range(cols):
                cell_x = x + c * cell_w
                cell_y = y + r * cell_h
                cells.append((cell_x, cell_y, cell_w, cell_h))
        return cells

    # ---------------------- Mostrar grilla ----------------------
    def draw_grid(self, frame, cells, color=(255, 0, 0), thickness=2):
        temp = frame.copy()
        for cx, cy, cw, ch in cells:
            cv2.rectangle(temp, (cx, cy), (cx + cw, cy + ch), color, thickness)
        cv2.imshow(self.window_name, temp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
