import os
import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

class BackgroundRemover:
    def __init__(self, model_path: str = "models/rmbg_v1.4.onnx"):
        """
        Model Path: ទីតាំង file ONNX របស់ RMBG-v1.4
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"រកមិនឃើញ ONNX Model តាមទីតាំង: {model_path}")

        # 1. បង្កើត ONNX Runtime Session (ប្រើ CPU ឬ DirectML/CUDA បើមាន)
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name

    def preprocess(self, image_bgr: np.ndarray, target_size=(1024, 1024)):
        """
        រៀបចំទំហំរូបភាព (Resize & Normalize) ឱ្យត្រូវតាម Input Specification របស់ RMBG-v1.4
        """
        h, w = image_bgr.shape[:2]
        
        # បំប្លែង BGR (OpenCV) ទៅ RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        # Resize ទៅ 1024x1024 សម្រាប់ Model
        resized = cv2.resize(image_rgb, target_size, interpolation=cv2.INTER_LINEAR)
        
        # Normalize (0-1) និងបំប្លែង Form [H, W, C] -> [1, C, H, W]
        img_data = resized.astype(np.float32) / 255.0
        
        # Standard Normalization (Mean & Std)
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_data = (img_data - mean) / std

        # Transpose
        img_data = np.transpose(img_data, (2, 0, 1))
        img_data = np.expand_dims(img_data, axis=0)
        
        return img_data, (h, w)

    def remove_background(self, image_bgr: np.ndarray, bg_color: tuple = None) -> np.ndarray:
        """
        image_bgr: រូបភាព BGR ដើម
        bg_color: ពណ៌ Background ថ្មី (ឧ. (255, 255, 255) សម្រាប់ពណ៌ស ឬ (255, 0, 0) សម្រាប់ខៀវ)
                 ប្រសិនបើ None វានឹងបញ្ចេញជារូប PNG តម្លាភាព (BGTransparent/Alpha Mask)
        """
        orig_h, orig_w = image_bgr.shape[:2]
        
        # Preprocessing
        input_tensor, _ = self.preprocess(image_bgr)

        # 2. រត់ ONNX Model Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        mask_pred = outputs[0][0][0] # ទទួលបាន Matte Mask [1024, 1024]

        # 3. Post-processing (Resize Alpha Mask មកទំហំដើមវិញ)
        mask_resized = cv2.resize(mask_pred, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        
        # Normalize Mask ឱ្យនៅចន្លោះ 0.0 -> 1.0
        mask_resized = np.clip(mask_resized, 0, 1)
        mask_3d = np.repeat(mask_resized[:, :, np.newaxis], 3, axis=2)

        # 4. ប្រសិនបើជ្រើសរើសប្តូរពណ៌ Background (សម្រាប់ ID/Passport Photo)
        if bg_color is not None:
            # បង្កើត Background ពណ៌សុទ្ធ (Solid Color)
            bg_image = np.full_like(image_bgr, bg_color, dtype=np.uint8)
            
            # Composite រូបភាពតាម Alpha Mask
            result_bgr = (image_bgr * mask_3d + bg_image * (1.0 - mask_3d)).astype(np.uint8)
            return result_bgr
        
        # 5. ប្រសិនបើចង់បានរូបតម្លាភាព BG (PNG BG Transparent Output - BGRA)
        else:
            b, g, r = cv2.split(image_bgr)
            alpha = (mask_resized * 255).astype(np.uint8)
            result_bgra = cv2.merge([b, g, r, alpha])
            return result_bgra

# -------------------------------------------------------------
# 🧪 ឧទាហរណ៍នៃការប្រើប្រាស់ (Quick Test)
# -------------------------------------------------------------
if __name__ == "__main__":
    remover = BackgroundRemover("models/rmbg_v1.4.onnx")
    
    # អានរូបថត
    input_img = cv2.imread("test_portrait.jpg")
    
    # ករណី ១: ដោះ Background ចេញជារូប Transparent (PNG)
    png_result = remover.remove_background(input_img, bg_color=None)
    cv2.imwrite("output_transparent.png", png_result)
    
    # ករណី ២: ប្តូរ Background ទៅពណ៌ខៀវ (សម្រាប់កាត/ID Photo - Blue BG)
    # ពណ៌ BGR: (255, 0, 0) គឺពណ៌ខៀវ
    id_blue_bg = remover.remove_background(input_img, bg_color=(255, 0, 0))
    cv2.imwrite("output_id_blue.jpg", id_blue_bg)
    
    # ករណី ៣: ប្តូរ Background ទៅពណ៌ស (Passport BG - White BG)
    id_white_bg = remover.remove_background(input_img, bg_color=(255, 255, 255))
    cv2.imwrite("output_id_white.jpg", id_white_bg)
    
    print("✨ ដោះ Background និងប្តូរពណ៌ដោយជោគជ័យ!")