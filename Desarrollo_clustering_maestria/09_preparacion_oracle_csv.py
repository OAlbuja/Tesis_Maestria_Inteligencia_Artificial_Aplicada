import pandas as pd
import glob
import os
from collections import defaultdict

os.makedirs('outputs', exist_ok=True)

print("=== 1. Procesando Golden Record ===")
df_golden = pd.read_csv('02_data_cleaning/data_ruc_universo_empresas/match_final_empresas_verificado.csv', dtype=str)
df_golden['ruc'] = df_golden['ruc'].astype(str).str.zfill(13)
df_golden['n_apariciones'] = pd.to_numeric(df_golden['n_apariciones'], errors='coerce').fillna(0).astype(int)

# Master (1 fila por RUC) - Aggregation
agg_funcs = {
    'razon_social': 'first',
    'razon_social_norm': 'first',
    'pais_empresa': lambda x: ' | '.join(x.dropna().astype(str).unique()),
    'sede_ecuador': 'first',
    'n_apariciones': 'sum',
    'fuentes': lambda x: ' | '.join(x.dropna().astype(str).unique())
}
df_master = df_golden.groupby('ruc').agg({k: v for k, v in agg_funcs.items() if k in df_golden.columns}).reset_index()
df_master.columns = df_master.columns.str.upper()
df_master.to_csv('outputs/ml_empresas_master.csv', index=False)
print(f"-> ml_empresas_master.csv generado con {len(df_master)} filas únicas.")

# Alias
cols_alias = ['ruc', 'nombre_original', 'nombre_original_norm']
df_alias = df_golden[[c for c in cols_alias if c in df_golden.columns]].copy()
df_alias = df_alias.drop_duplicates()
df_alias.columns = df_alias.columns.str.upper()
df_alias.to_csv('outputs/ml_empresas_alias_golden_record.csv', index=False)
print(f"-> ml_empresas_alias_golden_record.csv generado con {len(df_alias)} filas.")

print("\n=== 2. Procesando SCVS Directorio ===")
df_dir = pd.read_excel('02_data_cleaning/data_super_compañias/directorio_companias.xlsx', skiprows=4)
df_dir.columns = df_dir.columns.str.strip()
if 'RUC' in df_dir.columns:
    df_dir = df_dir[df_dir['RUC'].notna() & (df_dir['RUC'] != 'NO APLICA')].copy()
    df_dir['RUC'] = df_dir['RUC'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(13)
    # Filtrar solo RUCs ecuatorianos con 13 digitos reales.
    df_dir = df_dir[df_dir['RUC'].str.fullmatch(r'\d{13}', na=False)]
if 'EXPEDIENTE' in df_dir.columns:
    df_dir['EXPEDIENTE'] = df_dir['EXPEDIENTE'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

col_nombre = 'NOMBRE' if 'NOMBRE' in df_dir.columns else 'RAZÓN SOCIAL' if 'RAZÓN SOCIAL' in df_dir.columns else df_dir.columns[2]
df_dir = df_dir[['EXPEDIENTE', 'RUC', col_nombre]].rename(columns={col_nombre: 'NOMBRE'})
df_dir.to_csv('outputs/scvs_directorio_limpio.csv', index=False)
print(f"-> scvs_directorio_limpio.csv generado con {len(df_dir)} filas.")

print("\n=== 3. Procesando Ranking SCVS ===")
try:
    df_ranking = pd.read_csv('02_data_cleaning/data_super_compañias/Ranking/bi_ranking.csv', sep=',', encoding='utf-8', dtype=str)
    df_ranking.rename(columns={'expediente': 'EXPEDIENTE', 'anio': 'ANIO'}, inplace=True)
    df_ranking['EXPEDIENTE'] = df_ranking['EXPEDIENTE'].astype(str).str.replace(r'\.0$', '', regex=True)
    
    if 'ingresos_ventas' in df_ranking.columns and 'ingresos_totales' in df_ranking.columns:
        df_ranking['INGRESOS'] = df_ranking['ingresos_ventas'].fillna(df_ranking['ingresos_totales'])
    if 'n_empleados' in df_ranking.columns:
        df_ranking['EMPLEADOS'] = df_ranking['n_empleados']
    if 'activos' in df_ranking.columns:
        df_ranking['ACTIVOS'] = df_ranking['activos']
    if 'patrimonio' in df_ranking.columns:
        df_ranking['PATRIMONIO'] = df_ranking['patrimonio']
    if 'utilidad_neta' in df_ranking.columns and 'utilidad_ejercicio' in df_ranking.columns:
        df_ranking['UTILIDAD'] = df_ranking['utilidad_neta'].fillna(df_ranking['utilidad_ejercicio'])

    cols_ranking = ['EXPEDIENTE', 'ANIO', 'INGRESOS', 'EMPLEADOS', 'ACTIVOS', 'PATRIMONIO', 'UTILIDAD']
    cols_avail = [c for c in cols_ranking if c in df_ranking.columns]
    df_ranking[cols_avail].to_csv('outputs/scvs_ranking_resumen.csv', index=False)
    print(f"-> scvs_ranking_resumen.csv generado con {len(df_ranking)} filas.")
except Exception as e:
    print("No se pudo procesar Ranking SCVS:", e)

print("\n=== 4. Procesando SRI Resumen (Chunking Real con temp file) ===")
sri_files = glob.glob('02_data_cleaning/data_SRI/SRI_RUC_*.csv')
print(f"Se encontraron {len(sri_files)} archivos del SRI.")

establecimientos_counts = defaultdict(int)
provincias_por_ruc = defaultdict(set)
seen_matriz_rucs = set()

temp_csv = 'outputs/sri_matriz_temp.csv'
if os.path.exists(temp_csv):
    os.remove(temp_csv)

chunksize = 100000
first_write = True

for file in sri_files:
    try:
        with open(file, 'r', encoding='latin1') as f:
            first_line = f.readline()
            sep = '|' if '|' in first_line else ','
            
        for chunk in pd.read_csv(file, sep=sep, dtype=str, encoding='latin1', on_bad_lines='skip', chunksize=chunksize):
            chunk.columns = chunk.columns.str.strip().str.upper()

            if 'NUMERO_RUC' not in chunk.columns:
                continue

            chunk['NUMERO_RUC'] = (
                chunk['NUMERO_RUC']
                .astype(str)
                .str.replace(r'\.0$', '', regex=True)
                .str.strip()
                .str.zfill(13)
            )
            chunk = chunk[chunk['NUMERO_RUC'].str.fullmatch(r'\d{13}', na=False)].copy()
            
            # Conteo incremental
            counts = chunk['NUMERO_RUC'].value_counts()
            for ruc, c in counts.items():
                establecimientos_counts[ruc] += c
                    
            # Provincias únicas
            if 'DESCRIPCION_PROVINCIA_EST' in chunk.columns and 'NUMERO_RUC' in chunk.columns:
                for ruc, prov in zip(chunk['NUMERO_RUC'], chunk['DESCRIPCION_PROVINCIA_EST']):
                    if pd.notna(prov) and str(prov).strip():
                        provincias_por_ruc[ruc].add(str(prov).strip())
                
            # Extraer matriz y escribir a archivo temporal
            if 'NUMERO_ESTABLECIMIENTO' in chunk.columns:
                establecimiento_norm = (
                    chunk['NUMERO_ESTABLECIMIENTO']
                    .astype(str)
                    .str.replace(r'\.0$', '', regex=True)
                    .str.strip()
                    .str.lstrip('0')
                )
                matriz_chunk = chunk[establecimiento_norm == '1'].copy()
                if not matriz_chunk.empty:
                    matriz_chunk = matriz_chunk[~matriz_chunk['NUMERO_RUC'].isin(seen_matriz_rucs)].copy()
                if not matriz_chunk.empty:
                    seen_matriz_rucs.update(matriz_chunk['NUMERO_RUC'].tolist())
                    matriz_chunk.to_csv(temp_csv, mode='a', header=first_write, index=False)
                    first_write = False
                    
    except Exception as e:
        print(f"Error procesando {file}: {e}")

if os.path.exists(temp_csv):
    cols_sri = ['RUC', 'RAZON_SOCIAL_SRI', 'ESTADO_CONTRIBUYENTE', 'TIPO_CONTRIBUYENTE', 
                'OBLIGADO_CONTABILIDAD', 'AGENTE_RETENCION', 'CONTRIBUYENTE_ESPECIAL', 
                'FECHA_INICIO_ACTIVIDADES', 'CIIU_PRINCIPAL', 'PROVINCIA_PRINCIPAL', 
                'CANTON_PRINCIPAL', 'NUMERO_ESTABLECIMIENTOS', 'NUMERO_PROVINCIAS']

    sri_output = 'outputs/sri_ruc_empresas_resumen.csv'
    if os.path.exists(sri_output):
        os.remove(sri_output)

    first_sri_write = True
    final_seen_rucs = set()
    sri_rows = 0
    for df_sri_final in pd.read_csv(temp_csv, dtype=str, chunksize=chunksize):
        df_sri_final = df_sri_final.drop_duplicates(subset=['NUMERO_RUC']).copy()
        df_sri_final = df_sri_final[~df_sri_final['NUMERO_RUC'].isin(final_seen_rucs)].copy()
        final_seen_rucs.update(df_sri_final['NUMERO_RUC'].tolist())
        df_sri_final['NUMERO_ESTABLECIMIENTOS'] = df_sri_final['NUMERO_RUC'].map(establecimientos_counts)
        df_sri_final['NUMERO_PROVINCIAS'] = df_sri_final['NUMERO_RUC'].map(lambda x: len(provincias_por_ruc.get(x, set())))

        df_sri_final = df_sri_final.rename(columns={'NUMERO_RUC': 'RUC', 'RAZON_SOCIAL': 'RAZON_SOCIAL_SRI'})
        df_sri_final['RUC'] = df_sri_final['RUC'].astype(str).str.zfill(13)
        if 'FECHA_INICIO_ACTIVIDADES' in df_sri_final.columns:
            df_sri_final['FECHA_INICIO_ACTIVIDADES'] = df_sri_final['FECHA_INICIO_ACTIVIDADES'].astype(str).str.slice(0, 10)

        if 'OBLIGADO' in df_sri_final.columns and 'OBLIGADO_CONTABILIDAD' not in df_sri_final.columns:
            df_sri_final.rename(columns={'OBLIGADO': 'OBLIGADO_CONTABILIDAD'}, inplace=True)
        if 'ESPECIAL' in df_sri_final.columns and 'CONTRIBUYENTE_ESPECIAL' not in df_sri_final.columns:
            df_sri_final.rename(columns={'ESPECIAL': 'CONTRIBUYENTE_ESPECIAL'}, inplace=True)

        df_sri_final.rename(columns={
            'CODIGO_CIIU': 'CIIU_PRINCIPAL',
            'DESCRIPCION_PROVINCIA_EST': 'PROVINCIA_PRINCIPAL',
            'DESCRIPCION_CANTON_EST': 'CANTON_PRINCIPAL'
        }, inplace=True)

        cols_sri_exist = [c for c in cols_sri if c in df_sri_final.columns]
        df_sri_final[cols_sri_exist].to_csv(sri_output, mode='a', header=first_sri_write, index=False)
        first_sri_write = False
        sri_rows += len(df_sri_final)

    print(f"-> sri_ruc_empresas_resumen.csv generado con {sri_rows} filas.")
    
    os.remove(temp_csv)
else:
    print("No se procesaron archivos SRI.")

print("\n=== 5. Generando Tablas Modelo Oracle ===")

def prep_table(input_path, output_name, cols_to_keep=None, cols_to_rename=None):
    if not os.path.exists(input_path):
        print(f"No se encontró {input_path}")
        return
    df = pd.read_csv(input_path, dtype=str)
    if 'RUC' in df.columns:
        df['RUC'] = df['RUC'].astype(str).str.zfill(13)
    if cols_to_keep:
        cols_exist = [c for c in cols_to_keep if c in df.columns]
        df = df[cols_exist]
    if cols_to_rename:
        df.rename(columns=cols_to_rename, inplace=True)
    if 'anio' in df.columns:
        df['anio'] = pd.to_numeric(df['anio'], errors='coerce').astype('Int64').astype(str).replace('<NA>', '')
    if 'ANIO' in df.columns:
        df['ANIO'] = pd.to_numeric(df['ANIO'], errors='coerce').astype('Int64').astype(str).replace('<NA>', '')
    df.columns = df.columns.str.upper()
    df.to_csv(f'outputs/{output_name}.csv', index=False)
    print(f"-> {output_name}.csv ({len(df)} filas)")

# features_capa1
prep_table('03_feature_engineering/outputs/features_capa1.csv', 'ml_features_capa1', 
           cols_to_keep=['RUC', 'name_norm', 'tipo_sociedad', 'obligado_contabilidad', 'es_agente_retencion', 'es_contribuyente_especial', 'estado_activo', 'antiguedad_anos', 'sector_ciiu_macro', 'region'])

# labels_capa1
prep_table('03_feature_engineering/outputs/features_capa1.csv', 'ml_labels_capa1', 
           cols_to_keep=['RUC', 'source_label', 'source_winner', 'es_cliente_fpa'])

# features_capa2
prep_table('03_feature_engineering/outputs/features_capa2.csv', 'ml_features_capa2', 
           cols_to_keep=['RUC', 'anio', 'name_norm', 'tipo_sociedad', 'obligado_contabilidad', 'es_agente_retencion', 'es_contribuyente_especial', 'estado_activo', 'antiguedad_anos', 'sector_ciiu_macro', 'region', 'log_empleados', 'log_ingresos', 'log_activos', 'liquidez_corriente', 'margen_operacional'])

# labels_capa2
prep_table('03_feature_engineering/outputs/features_capa2.csv', 'ml_labels_capa2', 
           cols_to_keep=['RUC', 'anio', 'source_label', 'source_winner', 'es_cliente_fpa'])

# clusters_capa1
prep_table('04_modeling/outputs/clusters_capa1.csv', 'ml_clusters_capa1', 
           cols_to_keep=['RUC', 'cluster_capa1', 'segmento_capa1'],
           cols_to_rename={'cluster_capa1': 'CLUSTER_ID', 'segmento_capa1': 'SEGMENTO'})

# clusters_capa2
prep_table('04_modeling/outputs/clusters_capa2.csv', 'ml_clusters_capa2', 
           cols_to_keep=['RUC', 'anio', 'cluster_capa2', 'segmento_capa2'],
           cols_to_rename={'cluster_capa2': 'CLUSTER_ID', 'segmento_capa2': 'SEGMENTO'})

# validacion_capa1
prep_table('05_evaluation/outputs/validacion_externa_capa1.csv', 'ml_validacion_capa1', 
           cols_to_keep=['cluster_capa1', 'segmento', 'n', 'clientes_fpa', 'tasa_clientes', 'vs_base'],
           cols_to_rename={'cluster_capa1': 'CLUSTER_ID'})

# validacion_capa2
prep_table('05_evaluation/outputs/validacion_externa_capa2.csv', 'ml_validacion_capa2', 
           cols_to_keep=['cluster_capa2', 'segmento', 'n', 'clientes_fpa', 'tasa_clientes', 'vs_base'],
           cols_to_rename={'cluster_capa2': 'CLUSTER_ID'})

# concordancia_ari
prep_table('05_evaluation/outputs/tabla_concordancia_ari.csv', 'ml_concordancia_ari', 
           cols_to_keep=['comparacion', 'n_empresas_comunes', 'ARI'])

print("\nProceso Finalizado. Archivos listos en la carpeta 'outputs/'.")
