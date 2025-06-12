import pandas as pd
import os
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Rutas centralizadas
RUTA_PACIENTES = './datasets_limpios/pacientes_limpio.csv'
RUTA_CITAS = './datasets_limpios/citas_medicas_limpio.csv'
RUTA_SALIDA = './datawarehouse_simulado/'

# Funciones profesionales
def cargar_datos(ruta, nombre):
    try:
        df = pd.read_csv(ruta)
        logging.info(f"{nombre} cargado correctamente. Registros: {len(df)}")
        return df
    except Exception as e:
        logging.error(f"Error cargando {nombre}: {e}")
        raise

def crear_dim_paciente(df):
    dim = df[['id_paciente', 'nombre', 'sexo', 'fecha_nacimiento', 'edad', 'ciudad', 'email', 'telefono']].drop_duplicates().copy()
    dim['sk_paciente'] = dim.reset_index().index + 1
    logging.info(f"Dimensión paciente creada. Registros: {len(dim)}")
    return dim

def crear_dim_fecha(df_citas, df_pacientes):
    fechas_cita = df_citas['fecha_cita'].dropna().unique().tolist()
    fechas_nac = df_pacientes['fecha_nacimiento'].dropna().unique().tolist()
    fechas = set(fechas_cita) | set(fechas_nac)
    fechas = [f for f in fechas if pd.notnull(f)]
    dim_fecha = pd.DataFrame({'fecha': fechas})
    dim_fecha['fecha'] = pd.to_datetime(dim_fecha['fecha'], errors='coerce')
    dim_fecha = dim_fecha.dropna().drop_duplicates().sort_values('fecha').reset_index(drop=True)
    dim_fecha['sk_fecha'] = dim_fecha.index + 1
    dim_fecha['anio'] = dim_fecha['fecha'].dt.year
    dim_fecha['mes'] = dim_fecha['fecha'].dt.month
    dim_fecha['dia'] = dim_fecha['fecha'].dt.day
    dim_fecha['dia_semana'] = dim_fecha['fecha'].dt.dayofweek
    logging.info(f"Dimensión fecha creada. Registros: {len(dim_fecha)}")
    return dim_fecha

def crear_hecho_citas(df_citas, dim_paciente, dim_fecha):
    # Asegurar tipos
    df_citas = df_citas.copy()
    if 'fecha_cita' in df_citas.columns:
        df_citas['fecha_cita'] = pd.to_datetime(df_citas['fecha_cita'], errors='coerce')
    # Merge con dimensiones
    df_citas = df_citas.merge(dim_paciente[['id_paciente', 'sk_paciente']], on='id_paciente', how='left')
    df_citas = df_citas.merge(dim_fecha[['fecha', 'sk_fecha']], left_on='fecha_cita', right_on='fecha', how='left', suffixes=('', '_sk'))
    hecho = df_citas[['id_cita', 'sk_paciente', 'sk_fecha', 'especialidad', 'medico', 'costo', 'estado_cita']].copy()
    logging.info(f"Tabla de hechos de citas creada. Registros: {len(hecho)}")
    return hecho

def exportar_csv(df, ruta, nombre):
    try:
        df.to_csv(ruta, index=False)
        logging.info(f"{nombre} exportado a {ruta}")
    except Exception as e:
        logging.error(f"Error exportando {nombre}: {e}")
        raise

def main():
    os.makedirs(RUTA_SALIDA, exist_ok=True)
    # Cargar datos
    pacientes = cargar_datos(RUTA_PACIENTES, 'Pacientes')
    citas = cargar_datos(RUTA_CITAS, 'Citas médicas')
    # Crear dimensiones y hechos
    dim_paciente = crear_dim_paciente(pacientes)
    dim_fecha = crear_dim_fecha(citas, pacientes)
    hecho_citas = crear_hecho_citas(citas, dim_paciente, dim_fecha)
    # Exportar
    exportar_csv(dim_paciente, os.path.join(RUTA_SALIDA, 'dim_paciente.csv'), 'Dimensión Paciente')
    exportar_csv(dim_fecha, os.path.join(RUTA_SALIDA, 'dim_fecha.csv'), 'Dimensión Fecha')
    exportar_csv(hecho_citas, os.path.join(RUTA_SALIDA, 'hecho_citas.csv'), 'Hecho Citas')
    logging.info('Migración simulada completada exitosamente.')

if __name__ == "__main__":
    main()