import os
import glob
import csv
import time
import numpy as np
import onnxruntime as ort

# === Inicialización ===
print("=== Inicializando ONNX Runtime con Qualcomm QNN ===")

# Detectar proveedores disponibles
providers = ort.get_available_providers()
print("=== Proveedores disponibles ===")
for p in providers:
    print(f" - {p}")
print("================================")

# Buscar modelos ONNX en el directorio actual
onnx_models = glob.glob("*.onnx")
if not onnx_models:
    print(" [ERROR] No se encontraron archivos .onnx en el directorio actual.")
    exit()

print(f"\nModelos detectados ({len(onnx_models)}):")
for m in onnx_models:
    print(f" - {m}")

# Crear CSV de resultados
csv_file = "benchmark_results_qnn.csv"
with open(csv_file, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "modelo", "proveedor", "tiempo_ms", "estado",
        "formas_originales", "formas_usadas", "tipo_modelo"
    ])


# === Función auxiliar: genera tensores de entrada válidos ===
def generate_input(session):
    """
    Genera un diccionario con todos los tensores de entrada requeridos
    por el modelo ONNX, con formas y tipos válidos.
    Soporta modelos de texto (BERT, GPT...), imagen y audio.
    """
    inputs = {}
    shapes_used = {}
    dtypes = {}

    for input_info in session.get_inputs():
        name = input_info.name
        dtype = input_info.type  # ejemplo: 'tensor(float)' o 'tensor(int64)'
        shape = [dim if isinstance(dim, int) and dim > 0 else 1 for dim in input_info.shape]

        # Generar datos según el tipo
        if "int64" in dtype:
            # Entradas típicas de texto → IDs de tokens, máscaras
            if "mask" in name:
                data = np.ones(shape, dtype=np.int64)
            elif "token_type" in name:
                data = np.zeros(shape, dtype=np.int64)
            else:
                data = np.random.randint(0, 1000, size=shape, dtype=np.int64)
        elif "float" in dtype:
            data = np.random.rand(*shape).astype(np.float32)
        else:
            # Fallback
            data = np.random.rand(*shape).astype(np.float32)

        inputs[name] = data
        shapes_used[name] = shape
        dtypes[name] = dtype

    return inputs, shapes_used, dtypes


# === Detección automática del tipo de modelo ===
def detect_model_type(model_path, input_shapes):
    name = os.path.basename(model_path).lower()

    if any(k in name for k in ["gpt", "bert", "roberta", "distilbert", "t5"]):
        return "texto"
    elif any(k in name for k in ["whisper", "wav2vec", "deepspeech", "asr", "audio"]):
        return "audio"
    elif any(k in name for k in ["resnet", "mobilenet", "inception", "efficientnet", "densenet", "vgg", "alexnet", "squeezenet"]):
        return "imagen"
    else:
        # fallback por forma
        for s in input_shapes.values():
            if len(s) == 4:
                return "imagen"
            elif len(s) == 3:
                return "audio"
            elif len(s) in [1, 2]:
                return "texto"
        return "desconocido"


# === Función principal de benchmark ===
def benchmark_model(model_path, writer):
    print(f"\n===============================")
    print(f"  Probando modelo: {model_path}")
    print(f"===============================")

    try:
        session = ort.InferenceSession(model_path, providers=providers)
    except Exception as e:
        print(f" [ERROR] No se pudo cargar el modelo: {e}")
        writer.writerow([
            os.path.basename(model_path), "N/A", "N/A",
            f"Error al cargar: {e}", "N/A", "N/A", "N/A"
        ])
        return

    # Obtener info de entradas
    input_shapes = {
        inp.name: [dim if dim is not None else 1 for dim in inp.shape]
        for inp in session.get_inputs()
    }
    print(f" [INFO] Formas de entrada: {input_shapes}")

    tipo = detect_model_type(model_path, input_shapes)

    # Generar datos de entrada
    input_dict, used_shapes, dtypes = generate_input(session)

    # Probar en cada proveedor (QNN, CPU, etc.)
    for provider in providers:
        print(f" [INFO] Ejecutando en: {provider}")
        try:
            session = ort.InferenceSession(model_path, providers=[provider])

            # Calentamiento
            session.run(None, input_dict)

            # Benchmark (10 ejecuciones)
            runs = 10
            start = time.time()
            for _ in range(runs):
                session.run(None, input_dict)
            end = time.time()

            avg_time = (end - start) / runs * 1000  # ms
            print(f" [OK] {provider} — {avg_time:.2f} ms/inferencia")

            writer.writerow([
                os.path.basename(model_path), provider,
                f"{avg_time:.2f}", "OK",
                str(input_shapes), str(used_shapes), tipo
            ])

        except Exception as e:
            print(f" [ERROR] {provider} — {e}")
            writer.writerow([
                os.path.basename(model_path), provider, "N/A",
                f"Error: {e}", str(input_shapes), "N/A", tipo
            ])


# === Ejecutar benchmark para todos los modelos ===
with open(csv_file, mode="a", newline="") as f:
    writer = csv.writer(f)
    for model_path in onnx_models:
        benchmark_model(model_path, writer)

print(f"\n[RESULT] Resultados guardados en: {csv_file}")
