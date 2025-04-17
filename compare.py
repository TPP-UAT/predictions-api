import os

# Define las rutas de las dos carpetas
folder1 = "models/summarize"
folder2 = "models-2/summarize"

# Obtener nombres de carpetas en ambas rutas
ids_folder1 = set(os.listdir(folder1))
ids_folder2 = set(os.listdir(folder2))

# Verificar qué carpetas faltan
faltan_en_folder1 = ids_folder2 - ids_folder1
faltan_en_folder2 = ids_folder1 - ids_folder2

# Mostrar resultados
if faltan_en_folder1:
    print(f"Faltan {len(faltan_en_folder1)} carpetas en {folder1}:")
    for carpeta in faltan_en_folder1:
        print(carpeta)

if faltan_en_folder2:
    print(f"Faltan {len(faltan_en_folder2)} carpetas en {folder2}:")
    for carpeta in faltan_en_folder2:
        print(carpeta)

if not faltan_en_folder1 and not faltan_en_folder2:
    print("No faltan carpetas en ninguna de las rutas. Todo está sincronizado.")
