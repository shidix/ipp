import whisper
import sys
import os
import requests

# Verificar que se proporcionó un archivo como argumento
if len(sys.argv) != 2:
    print("Uso: python3 transcribir.py <ruta_al_archivo_audio>")
    sys.exit(1)

# Obtener la ruta del archivo de audio desde los argumentos
audio_file = sys.argv[1]

# Verificar si el archivo existe
if not os.path.isfile(audio_file):
    print(f"Error: El archivo '{audio_file}' no existe.")
    sys.exit(1)

# Generar el nombre del archivo de salida (cambia extensión a .txt)
output_file = os.path.splitext(audio_file)[0] + ".txt"
print(output_file)

# Cargar el modelo preentrenado de Whisper
#print("Cargando el modelo de Whisper...")
model = whisper.load_model("base")  # Puedes usar "tiny", "base", "small", "medium", o "large"

# Transcribir el audio
#print("Transcribiendo el audio...")
result = model.transcribe(audio_file, language="es")

#print("Sending...")
res = requests.post("https://ipp.shidix.es/gestion/set-note-concept", headers={"Accept": "application/txt"}, data={"token": "1234", "text": result["text"], "note": 5})
# Guardar la transcripción en el archivo de salida
#print(res)
#with open(output_file, "w", encoding="utf-8") as file:
#    file.write(result["text"])

#print(f"Transcripción completa. Archivo guardado como: {output_file}")
