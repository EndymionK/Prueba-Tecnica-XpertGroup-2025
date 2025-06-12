import pandas as pd
import os
from ydata_profiling import ProfileReport
import json

# Obtener la ruta absoluta de la raíz del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def cargar_datos_originales():
    with open('../dataset_original/dataset_hospital 2.json', encoding='utf-8') as f:
        data = json.load(f)
    df_pacientes = pd.DataFrame(data['pacientes'])
    df_citas = pd.DataFrame(data['citas_medicas']) if 'citas_medicas' in data and len(data['citas_medicas']) > 0 else pd.DataFrame()
    return df_pacientes, df_citas

def cargar_datos_limpios():
    df_pacientes = pd.read_csv('../datasets_limpios/pacientes_limpio.csv')
    df_citas = pd.read_csv('../datasets_limpios/citas_medicas_limpio.csv')
    return df_pacientes, df_citas

# Crear carpeta para reportes si no existe
RUTA_REPORTES = os.path.join(BASE_DIR, 'reportes_automaticos')
os.makedirs(RUTA_REPORTES, exist_ok=True)

def generar_reporte(df, nombre, prefijo):
    profile = ProfileReport(
        df,
        title=f'Reporte de {nombre}',
        explorative=True,
        correlations={"auto": {"calculate": False}},
        missing_diagrams={"heatmap": False}
    )
    ruta = os.path.join(RUTA_REPORTES, f'{prefijo}_{nombre.lower().replace(" ", "_")}_report.html')
    profile.to_file(ruta)
    print(f'Reporte de {nombre} generado en {ruta}')

def pruebas_automaticas(tipo):
    if tipo == 'original':
        df_pacientes, df_citas = cargar_datos_originales()
        prefijo = 'original'
    elif tipo == 'limpio':
        df_pacientes, df_citas = cargar_datos_limpios()
        prefijo = 'limpio'
    else:
        raise ValueError('Tipo de dataset no válido. Usa "original" o "limpio".')
    generar_reporte(df_pacientes, 'Pacientes', prefijo)
    generar_reporte(df_citas, 'Citas Médicas', prefijo)
    print(f'Todos los reportes avanzados ({tipo}) han sido generados.')

def main():
    print('Generando reportes para el dataset original...')
    pruebas_automaticas('original')
    print('Generando reportes para el dataset limpio...')
    pruebas_automaticas('limpio')

if __name__ == '__main__':
    main()
