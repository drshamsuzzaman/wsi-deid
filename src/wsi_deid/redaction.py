from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


SLIDE_LENGTH_MM = 75.0
SLIDE_WIDTH_MM = 25.0


def find_slide_box(rgb_img: Image.Image) -> tuple[int, int, int, int]:
    arr = np.array(rgb_img.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 248, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return (0, 0, arr.shape[1], arr.shape[0])
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)
    return (x, y, x + w, y + h)


def infer_barcode_side(rgb_img: Image.Image, slide_box: tuple[int, int, int, int]) -> tuple[str, float, float]:
    arr = np.array(rgb_img.convert("RGB"))
    x0, y0, x1, y1 = slide_box
    width = x1 - x0
    end_w = max(1, int(width * 0.28))
    left = arr[y0:y1, x0 : x0 + end_w]
    right = arr[y0:y1, x1 - end_w : x1]

    def barcode_score(region: np.ndarray) -> float:
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        dark = gray < 90
        edges = cv2.Canny(gray, 40, 140)
        vertical_kernel = np.ones((25, 3), np.uint8)
        vertical = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        return float(dark.mean()) + 2.0 * float((vertical > 0).mean())

    left_score = barcode_score(left)
    right_score = barcode_score(right)
    return ("left" if left_score >= right_score else "right", left_score, right_score)


def redact_slide_ends(
    rgb_img: Image.Image,
    barcode_side: str = "auto",
    barcode_end_mm: float = 22.0,
    handwritten_end_mm: float = 12.0,
    top_bottom_margin_mm: float = 1.0,
    fill: tuple[int, int, int] = (255, 255, 255),
) -> tuple[Image.Image, Image.Image, dict]:
    img = rgb_img.convert("RGB")
    arr = np.array(img).copy()
    mask = np.zeros(arr.shape[:2], dtype=np.uint8)
    box = find_slide_box(img)
    x0, y0, x1, y1 = box
    slide_px = x1 - x0

    if barcode_side == "auto":
        barcode_side, left_score, right_score = infer_barcode_side(img, box)
    else:
        left_score = right_score = None

    barcode_px = int(slide_px * barcode_end_mm / SLIDE_LENGTH_MM)
    handwritten_px = int(slide_px * handwritten_end_mm / SLIDE_LENGTH_MM)
    margin_px = int((y1 - y0) * top_bottom_margin_mm / SLIDE_WIDTH_MM)
    yy0 = max(0, y0 + margin_px)
    yy1 = min(arr.shape[0], y1 - margin_px)

    if barcode_side == "left":
        mask[yy0:yy1, x0 : min(x1, x0 + barcode_px)] = 255
        mask[yy0:yy1, max(x0, x1 - handwritten_px) : x1] = 255
    else:
        mask[yy0:yy1, max(x0, x1 - barcode_px) : x1] = 255
        mask[yy0:yy1, x0 : min(x1, x0 + handwritten_px)] = 255

    arr[mask > 0] = fill
    info = {
        "slide_box": box,
        "barcode_side": barcode_side,
        "left_score": left_score,
        "right_score": right_score,
        "barcode_px": barcode_px,
        "handwritten_px": handwritten_px,
    }
    return Image.fromarray(arr), Image.fromarray(mask), info
