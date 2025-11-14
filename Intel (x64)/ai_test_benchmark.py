from openvino import Core
import numpy as np
import time
import csv
import glob
import os

# === Inicialización de OpenVINO ===
ie = Core()
available_devices = ie.available_devices
print("=== Dispositivos detectados ===")
for dev in available_devices:
    print(f" - {dev}")
print("===============================")

# === Buscar modelos .onnx en el directorio del script ===
script_dir = os.path.dirname(os.path.abspath(__file__))
onnx_models = glob.glob(os.path.join(script_dir, "*.onnx"))
if not onnx_models:
    print(" [ERROR] No se encontraron archivos .onnx en el directorio actual.")
    exit()

print(f"\nModelos detectados ({len(onnx_models)}):")
for model in onnx_models:
    print(f" - {os.path.basename(model)}")

# === Dispositivos a probar ===
devices_to_test = [d for d in ["CPU", "GPU", "NPU"] if d in available_devices]

# === Abrir archivo CSV ===
csv_file = os.path.join(script_dir, "benchmark_results.csv")
with open(csv_file, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["modelo", "dispositivo", "tiempo_ms", "estado", "forma_original", "forma_usada", "tipo_modelo"])

    # === Función para generar tensor de entrada según tipo y dispositivo ===
    def generate_input(shape, device, tipo_modelo):
        shape = [dim if dim > 0 else 1 for dim in shape]  # reemplaza 0 por 1
        if device == "NPU" and tipo_modelo == "texto":
            if len(shape) == 1:
                shape = [1, 128]
            elif len(shape) == 2:
                shape[0] = 1 if shape[0] <= 0 else shape[0]
                shape[1] = 128 if shape[1] <= 0 else shape[1]
        if tipo_modelo in ["imagen", "audio", "vector"]:
            return np.random.rand(*shape).astype(np.float32), shape
        elif tipo_modelo == "texto":
            return np.random.randint(0, 1000, size=shape, dtype=np.int64), shape
        else:
            raise ValueError(f"Forma no compatible: {shape}")

    # === Iterar sobre cada modelo ===
    for model_path in onnx_models:
        print(f"\n===============================")
        print(f"  Probando modelo: {os.path.basename(model_path)}")
        print(f"===============================")

        try:
            model = ie.read_model(model_path)
        except Exception as e:
            print(f" [ERROR] Error al cargar {os.path.basename(model_path)}: {e}")
            writer.writerow([os.path.basename(model_path), "N/A", "N/A", f"Error al cargar: {e}", "N/A", "N/A", "N/A"])
            continue

        input_info = model.inputs[0]
        input_shape = list(input_info.partial_shape.get_min_shape())
        print(f" [INFO] Forma de entrada detectada: {input_shape}")

        # Detectar tipo de modelo
        if len(input_shape) == 4:
            tipo_modelo = "imagen"
        elif len(input_shape) == 3:
            tipo_modelo = "audio"
        elif len(input_shape) in [1, 2]:
            tipo_modelo = "texto"
        else:
            tipo_modelo = "desconocido"
        print(f" [INFO] Tipo de modelo detectado: {tipo_modelo}")

        for device in devices_to_test:
            try:
                input_tensor, used_shape = generate_input(input_shape, device, tipo_modelo)
            except Exception as e:
                print(f" [WARN] No se pudo generar tensor para {device}: {e}")
                writer.writerow([os.path.basename(model_path), device, "N/A",
                                 f"Error generando tensor: {e}", str(input_shape), "N/A", tipo_modelo])
                continue

            print(f"\n [PROCESS] Compilando para: {device}")
            try:
                compiled = ie.compile_model(model, device)
            except Exception as e:
                print(f" [ERROR] No se pudo compilar en {device}: {e}")
                writer.writerow([os.path.basename(model_path), device, "N/A",
                                 f"Error al compilar: {e}", str(input_shape), str(used_shape), tipo_modelo])
                continue

            # Calentamiento
            try:
                compiled([input_tensor])
            except Exception as e:
                print(f" [ERROR] Error durante el calentamiento en {device}: {e}")
                writer.writerow([os.path.basename(model_path), device, "N/A",
                                 f"Error en inferencia: {e}", str(input_shape), str(used_shape), tipo_modelo])
                continue

            # Benchmark (10 ejecuciones)
            runs = 10
            start = time.time()
            for _ in range(runs):
                compiled([input_tensor])
            end = time.time()
            avg_time = (end - start) / runs * 1000  # ms

            print(f" [OK] {device} — {avg_time:.2f} ms/inferencia")
            writer.writerow([os.path.basename(model_path), device, f"{avg_time:.2f}", "OK",
                             str(input_shape), str(used_shape), tipo_modelo])

print(f"\n[RESULT] Resultados guardados en: {csv_file}")
