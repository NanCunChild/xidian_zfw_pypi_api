import onnxruntime
import numpy as np
from PIL import Image
import argparse
import io  # <--- 新增导入

# --- 1. 配置参数 ---
# ... (这部分保持不变)
MODEL_PATH = 'crnn_model.onnx'      
IMAGE_HEIGHT = 34                   
IMAGE_WIDTH = 90                    
CHARACTERS = "0123456789"

def ctc_decode_np(preds, int_to_char):
    # ... (这部分保持不变)
    preds_idx = np.argmax(preds, axis=1)
    processed_indices = []
    for i, p_idx in enumerate(preds_idx):
        if i == 0 or p_idx != preds_idx[i-1]:
            processed_indices.append(p_idx)
    decoded_text = ""
    for idx in processed_indices:
        if idx != 0:
            decoded_text += int_to_char[idx]
    return decoded_text

class OnnxCrnnPredictor:
    # ... (__init__ 方法保持不变)
    def __init__(self, model_path, characters, image_width, image_height):
        print(f"[INFO] 正在初始化预测器...")
        self.width = image_width
        self.height = image_height
        self.session = onnxruntime.InferenceSession(model_path)
        print(f"[INFO] ONNX 模型加载成功: {model_path}")
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.num_classes = len(characters) + 1
        self.int_to_char = {i + 1: char for i, char in enumerate(characters)}
        print(f"[INFO] 字符集加载完成，共 {self.num_classes} 类 (包含 blank)。")

    def predict(self, image_bytes):
        """
        对给定的图像字节流进行识别。
        :param image_bytes: 图像的字节数据。
        :return: 识别出的字符串。
        """
        # 1. 图像预处理
        # --- vvv 这里是修改的部分 vvv ---
        # 使用 io.BytesIO 将字节数据包装成一个内存中的二进制流
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream)
        # --- ^^^ 这里是修改的部分 ^^^ ---

        # a. 转换为灰度图
        image = image.convert('L')
        # b. 调整尺寸
        image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # c. 转换为 NumPy 数组，并进行归一化
        image_np = np.array(image, dtype=np.float32) / 255.0
        image_np = (image_np - 0.5) / 0.5
        
        # d. 增加 batch 和 channel 维度
        input_tensor = np.expand_dims(np.expand_dims(image_np, axis=0), axis=0)

        # 2. 执行推理
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})[0]
        
        # 3. 后处理和解码
        preds = outputs.squeeze(1)
        result = ctc_decode_np(preds, self.int_to_char)
        
        return result

# --- 主程序 (用于测试) ---
if __name__ == '__main__':
    # ... (这部分保持不变)
    parser = argparse.ArgumentParser(description="使用 ONNX CRNN 模型进行验证码识别")
    parser.add_argument("--image", type=str, required=True, help="需要识别的验证码图片路径")
    parser.add_argument("--model", type=str, default=MODEL_PATH, help="ONNX 模型文件路径")
    args = parser.parse_args()

    predictor = OnnxCrnnPredictor(
        model_path=args.model, 
        characters=CHARACTERS,
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT
    )

    print(f"[INFO] 正在识别图片: {args.image}")
    with open(args.image, 'rb') as f:
        image_bytes = f.read()

    result = predictor.predict(image_bytes)

    print(f"---" * 10)
    print(f"[SUCCESS] 识别结果 --> {result}")
    print(f"---" * 10)