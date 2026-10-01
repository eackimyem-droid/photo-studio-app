import cv2
import numpy as np
import mediapipe as mp

class SkinBeautyEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def process_beauty(self, image: np.ndarray, smoothness: float = 0.5, brightness: float = 0.1) -> np.ndarray:
        """
        smoothness: 0.0 -> 1.0 (កម្រិតស្បែករលោង)
        brightness: -0.5 -> 0.5 (កម្រិតពន្លឺមុខ)
        """
        h, w, _ = image.shape
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.mp_face_mesh.process(rgb_img)

        # 1. ធ្វើឱ្យស្បែករលោងដោយប្រើ Guided / Bilateral Filter
        # វិធីនេះជួយឱ្យស្បែករលោង ប៉ុន្តែមិនបាត់បង់ Detail គែមភ្នែក និងច្រមុះឡើយ
        d = int(5 + smoothness * 10)
        sigma_color = 25 + smoothness * 50
        sigma_space = 25 + smoothness * 50
        smoothed = cv2.bilateralFilter(image, d, sigma_color, sigma_space)

        # ២. បង្កើត Mask សម្រាប់ផ្ទៃមុខ ដើម្បីកុំឱ្យ Filter ប៉ះពាល់ដល់ Background
        mask = np.zeros((h, w), dtype=np.uint8)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            hull_points = []
            # ប្រើ Oval Face Landmark Indices របស់ MediaPipe
            face_oval_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
            for idx in face_oval_indices:
                pt = landmarks[idx]
                hull_points.append((int(pt.x * w), int(pt.y * h)))
            
            hull = cv2.convexHull(np.array(hull_points))
            cv2.fillConvexPoly(mask, hull, 255)
            # Blur គែម Mask ដើម្បីឱ្យវាបាញ់ចូលគ្នារលូន
            mask = cv2.GaussianBlur(mask, (21, 21), 0)

        # ៣. Blend រូបស្បែករលោង និងរូបដើមចូលគ្នា តាម Mask
        mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        result = (smoothed * mask_3d + image * (1 - mask_3d)).astype(np.uint8)

        # ៤. កែសម្រួលពន្លឺ (Brightness & Contrast Adjustment)
        if brightness != 0:
            alpha = 1.0 + brightness
            beta = brightness * 30
            result = cv2.convertScaleAbs(result, alpha=alpha, beta=beta)

        return result