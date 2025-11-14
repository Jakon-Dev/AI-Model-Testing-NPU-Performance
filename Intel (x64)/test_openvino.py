from openvino import Core
import numpy as np

ie = Core()
model = ie.read_model("mobilenetv2.onnx")

# Compilar para NPU si está disponible
available = ie.available_devices
print("Dispositivos disponibles:", available)

target_device = "NPU" if "NPU" in available else "CPU"
compiled = ie.compile_model(model, target_device)

print(f"Modelo compilado para: {target_device}")

input_tensor = np.random.rand(1, 3, 224, 224).astype(np.float32)
output = compiled([input_tensor])

# Obtener el nombre de salida dinámicamente
output_tensor_name = compiled.outputs[0]
print("Salida:", np.array(output[output_tensor_name]).shape)
