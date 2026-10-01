import base64
import cv2
import numpy as np

def base64_to_cv2(base64_string: str) -> np.ndarray:
    """បំប្លែង Base64 String ទៅជា OpenCV BGR Image"""
    # លុប Header Prefix ករណីមាន data:image/png;base64,
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image

def cv2_to_base64(image: np.ndarray, format_ext: str = ".jpg") -> str:
    """បំប្លែង OpenCV BGR Image ទៅជា Base64 String"""
    success, buffer = cv2.imencode(format_ext, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not success:
        raise ValueError("មិនអាច Encode រូបភាពទៅជា JPEG បានឡើយ!")
    
    encoded_string = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_string}"