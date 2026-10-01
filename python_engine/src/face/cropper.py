import cv2
import numpy as np
import mediapipe as mp

class AutoFaceCropper:
    def __init__(self):
        # ប្រើប្រាស់ MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        
        # Preset Target Aspect Ratios (Width / Height)
        self.presets = {
            "3x4": 3.0 / 4.0,           # 0.75
            "4x6": 4.0 / 6.0,           # 0.667
            "passport": 3.5 / 4.5,       # 0.777 (Cambodia Standard)
            "facebook_post": 1.0 / 1.0,  # 1:1 Square
            "facebook_cover": 16.0 / 9.0 # 16:9 Landscape
        }

    def crop_face(
        self, 
        image: np.ndarray, 
        preset: str = "3x4", 
        padding_top: float = 0.35,
        padding_bottom: float = 0.25
    ) -> np.ndarray:
        """
        image: រូបថត BGR ពី OpenCV
        preset: ប្រភេទទំហំ ("3x4", "4x6", "passport", "facebook_post", "facebook_cover")
        padding_top: ចន្លោះពីលើក្បាលទៅគែមខាងលើ ( Headroom)
        padding_bottom: ចន្លោះពីចង្កាទៅទ្រូង/ស្មា
        """
        if preset not in self.presets:
            raise ValueError(f"រកមិនឃើញ Preset: {preset}។ សូមជ្រើសរើស: {list(self.presets.keys())}")

        target_ratio = self.presets[preset]
        img_h, img_w, _ = image.shape

        # ១. ស្វែងរកផ្ទៃមុខជាមួយ MediaPipe
        with self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as detector:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb_img)

            if not results.detections:
                print("⚠️ រកមិនឃើញផ្ទៃមុខ! Dynamic Crop តាម Center Image...")
                return self._crop_center_fallback(image, target_ratio)

            # យកមុខដំបូងគេដែលធំជាងគេក្នុងរូប
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box

            # បំប្លែង Relative Coordinates ទៅជា Pixels
            fx = int(bbox.xmin * img_w)
            fy = int(bbox.ymin * img_h)
            fw = int(bbox.width * img_w)
            fh = int(bbox.height * img_h)

            # Center Coordinates នៃមុខ
            face_center_x = fx + (fw // 2)

            # ២. គណនា Crop Bounding Box សម្រាប់ ID Photo
            # សម្រាប់ ID photo ត្រូវទុក space ខាងលើក្បាល និងផ្នែកខាងក្រោមស្មា
            crop_h = int(fh * (1.0 + padding_top + padding_bottom))
            crop_w = int(crop_h * target_ratio)

            # កំណត់ទីតាំង Top-Y ឱ្យមុខនៅចំកណ្តាលល្មម
            crop_y1 = max(0, fy - int(fh * padding_top))
            crop_y2 = crop_y1 + crop_h

            # ប្រសិនបើ Crop Y2 លើសកម្ពស់រូបភាព ត្រូវ Adjust ឡើងលើវិញ
            if crop_y2 > img_h:
                crop_y2 = img_h
                crop_y1 = max(0, crop_y2 - crop_h)

            # កំណត់ទីតាំង Left-X ឱ្យ Center មុខនៅចំកណ្តាល Crop Box
            crop_x1 = max(0, face_center_x - (crop_w // 2))
            crop_x2 = crop_x1 + crop_w

            # ប្រសិនបើ Crop X2 លើសទទឹងរូបភាព ត្រូវ Adjust ទៅឆ្វេង
            if crop_x2 > img_w:
                crop_x2 = img_w
                crop_x1 = max(0, crop_x2 - crop_w)

            # ៣. Perform Crop & Resize
            cropped_img = image[crop_y1:crop_y2, crop_x1:crop_x2]

            print(f"✅ បាន Crop រូបភាពតាម Preset [{preset}] ដោយជោគជ័យ!")
            return cropped_img

    def _crop_center_fallback(self, image: np.ndarray, target_ratio: float) -> np.ndarray:
        """ករណីរកមិនឃើញមុខ វានឹង Crop ចំកណ្តាលរូបភាពដោយស្វ័យប្រវត្តិ"""
        img_h, img_w, _ = image.shape
        current_ratio = img_w / img_h

        if current_ratio > target_ratio:
            # រូបដើមទទឹងធំជាង -> កាត់ទទឹងចេញ
            new_w = int(img_h * target_ratio)
            start_x = (img_w - new_w) // 2
            return image[:, start_x:start_x + new_w]
        else:
            # រូបដើមកម្ពស់ខ្ពស់ជាង -> កាត់កម្ពស់ចេញ
            new_h = int(img_w / target_ratio)
            start_y = (img_h - new_h) // 2
            return image[start_y:start_y + new_h, :]

# -------------------------------------------------------------
# 🧪 ឧទាហរណ៍នៃការប្រើប្រាស់ (Quick Test)
# -------------------------------------------------------------
if __name__ == "__main__":
    cropper = AutoFaceCropper()
    input_image = cv2.imread("raw_photo.jpg")

    if input_image is not None:
        # Crop 3x4 cm
        photo_3x4 = cropper.crop_face(input_image, preset="3x4")
        cv2.imwrite("crop_3x4.jpg", photo_3x4)

        # Crop Passport
        photo_passport = cropper.crop_face(input_image, preset="passport")
        cv2.imwrite("crop_passport.jpg", photo_passport)

        # Crop Facebook Post (1:1)
        photo_fb = cropper.crop_face(input_image, preset="facebook_post")
        cv2.imwrite("crop_fb_post.jpg", photo_fb)