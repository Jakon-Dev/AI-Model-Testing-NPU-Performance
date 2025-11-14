import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("mobilenetv2.onnx", providers=["DmlExecutionProvider"])
input_name = session.get_inputs()[0].name
input_data = np.random.rand(1, 3, 224, 224).astype(np.float32)
result = session.run(None, {input_name: input_data})
print("Resultado:", np.array(result[0]).shape)