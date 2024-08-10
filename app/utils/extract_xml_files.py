import os
import shutil
import settings as s

# Ruta de la carpeta principal
root_dir = "app/indicators_data/eurostat/eurostat_metadata"

def move_smdx_files_and_cleanup(root_dir):
    # Recorre los subdirectorios de primer nivel en root_dir
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith('.sdmx.xml'):
                    xml_file_path = subentry.path
                    new_path = os.path.join(root_dir, subentry.name)
                    
                    # Asegúrate de que el nombre del archivo no sobrescriba a otros
                    if os.path.exists(new_path):
                        base, extension = os.path.splitext(subentry.name)
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(root_dir, f"{base}_{counter}{extension}")
                            counter += 1

                    shutil.move(xml_file_path, new_path)
                    print(f'Moved: {xml_file_path} to {new_path}')

def remove_all_dirs(root_dir):
    # Recorre los subdirectorios y archivos en el directorio dado
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            # Elimina subdirectorios recursivamente
            remove_all_dirs(entry.path)
            
            # Intenta eliminar el directorio actual y todo su contenido
            try:
                shutil.rmtree(entry.path)  # Elimina el directorio y todo su contenido
                print(f'Removed directory and its contents: {entry.path}')
            except OSError as e:
                print(f'Could not remove directory: {entry.path}. Error: {e}')






# Ejecutar la función
move_smdx_files_and_cleanup(root_dir=s.eurostat_metadata_folder)
remove_all_dirs(root_dir=s.eurostat_metadata_folder)