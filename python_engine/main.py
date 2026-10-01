import sys
import json
import tracebacks
import numpy as np
import cv2

# Import AI Modules ដែលយើងបានបង្កើត
from src.face.cropper import AutoFaceCropper
from src.beauty.skin import SkinRetoucher
from src.id_photo.a4_layout import A4PrintLayoutGenerator
from src.utils.image_io import base64_to_cv2, cv2_to_base64


class PythonEngineBridge:
    def __init__(self):
        # Initialize Core Engines
        self.cropper = AutoFaceCropper()
        self.retoucher = SkinRetoucher()
        self.a4_generator = A4PrintLayoutGenerator(dpi=300)

    def process_request(self, request_json: str):
        """ទទួល Request ជា JSON String រួច Parse និង Route ទៅកាន់ Processors"""
        try:
            data = json.loads(request_json)
            command = data.get("command")
            payload = data.get("payload", {})

            # 1. Route Commands
            if command == "PING":
                return self.send_success({"message": "PONG! Python Engine is alive."})

            elif command == "CROP_FACE":
                return self.handle_crop_face(payload)

            elif command == "RETOUCH":
                return self.handle_beauty_retouch(payload)

            elif command == "GENERATE_A4":
                return self.handle_generate_a4(payload)

            else:
                return self.send_error(f"Unknown command: {command}")

        except Exception as e:
            error_details = traceback.format_exc()
            return self.send_error(str(e), details=error_details)

    # -------------------------------------------------------------
    # ⚙️ Command Handlers
    # -------------------------------------------------------------

    def handle_crop_face(self, payload: dict):
        image_base64 = payload.get("image")
        preset = payload.get("preset", "3x4")

        if not image_base64:
            return self.send_error("Missing 'image' base64 data.")

        # Base64 -> OpenCV Image
        cv_img = base64_to_cv2(image_base64)

        # Process Auto Face Crop
        cropped_img = self.cropper.crop_face(cv_img, preset=preset)

        # OpenCV Image -> Base64
        output_base64 = cv2_to_base64(cropped_img)

        return self.send_success({
            "image": output_base64,
            "preset": preset,
            "width": cropped_img.shape[1],
            "height": cropped_img.shape[0]
        })

    def handle_beauty_retouch(self, payload: dict):
        image_base64 = payload.get("image")
        smoothness = float(payload.get("smoothness", 0.35))
        brightness = float(payload.get("brightness", 0.1))

        if not image_base64:
            return self.send_error("Missing 'image' base64 data.")

        cv_img = base64_to_cv2(image_base64)

        # Process Retouch (Smoothness + Brightness)
        retouched_img = self.retoucher.apply_retouch(
            cv_img, 
            smoothness=smoothness, 
            brightness=brightness
        )

        output_base64 = cv2_to_base64(retouched_img)

        return self.send_success({"image": output_base64})

    def handle_generate_a4(self, payload: dict):
        image_base64 = payload.get("image")
        size_type = payload.get("size_type", "3x4")
        draw_crop_marks = payload.get("crop_marks", True)

        if not image_base64:
            return self.send_error("Missing 'image' base64 data.")

        cv_img = base64_to_cv2(image_base64)

        # Process A4 Grid Generation
        a4_sheet = self.a4_generator.generate_a4_sheet(
            cv_img, 
            size_type=size_type, 
            draw_crop_marks=draw_crop_marks
        )

        output_base64 = cv2_to_base64(a4_sheet)

        return self.send_success({
            "image": output_base64,
            "size_type": size_type
        })

    # -------------------------------------------------------------
    # 📤 Response Helpers (Standard JSON Payload)
    # -------------------------------------------------------------

    def send_success(self, data: dict):
        response = {
            "status": "success",
            "data": data,
            "error": None
        }
        self._write_stdout(response)

    def send_error(self, message: str, details: str = None):
        response = {
            "status": "error",
            "data": None,
            "error": message,
            "details": details
        }
        self._write_stdout(response)

    def _write_stdout(self, response_dict: dict):
        """បាញ់ JSON String ទៅ stdout ជាមួយ flush=True សម្រាប់ឆ្លើយតបទៅ Rust ភ្លាមៗ"""
        json_output = json.dumps(response_dict)
        print(json_output, flush=True)


# -------------------------------------------------------------
# 🔄 Event Loop (StdIn Listener)
# -------------------------------------------------------------
def main():
    engine = PythonEngineBridge()

    # Log សារដំបូងបញ្ជាក់ថា Python Sidecar រួចរាល់
    # print(json.dumps({"status": "ready"}), flush=True)

    # អាន Input ជួរនីមួយៗដែលបាញ់មកពី Rust sys.stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # ចាកចេញពេលទទួល Command EXIT
        if line == "EXIT":
            break

        # Process Request
        engine.process_request(line)


if __name__ == "__main__":
    main()