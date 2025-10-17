import onnxruntime as ort
import numpy as np

model_path = "mobilenetv2.onnx"
print(f"Cargando modelo: {model_path}")

# === Configurar ejecución con el proveedor QNN (si está disponible) ===
providers = ort.get_available_providers()
print("Proveedores disponibles:", providers)

# Si QNN no está disponible, usa CPU
provider = "QNNExecutionProvider" if "QNNExecutionProvider" in providers else "CPUExecutionProvider"
print(f"Ejecutando con: {provider}")

# === Crear sesión ONNX Runtime ===
session = ort.InferenceSession(model_path, providers=[provider])

# === Preparar entrada ===
input_name = session.get_inputs()[0].name
input_tensor = np.random.rand(1, 3, 224, 224).astype(np.float32)

# === Ejecutar inferencia ===
outputs = session.run(None, {input_name: input_tensor})

# === Mostrar información de salida ===
for i, out in enumerate(session.get_outputs()):
    arr = outputs[i]
    print(f"Salida '{out.name}': forma {arr.shape}, tipo {arr.dtype}")
