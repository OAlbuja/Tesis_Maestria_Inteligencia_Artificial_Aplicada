import pandas as pd
import os

def split_file(filepath, chunksize=500000):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    out_dir = os.path.join(os.path.dirname(filepath), 'chunks')
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Dividiendo {filename}...")
    try:
        df_iter = pd.read_csv(filepath, dtype=str, chunksize=chunksize)
        for i, chunk in enumerate(df_iter):
            out_name = os.path.join(out_dir, f"{name}_parte{i+1}{ext}")
            chunk.to_csv(out_name, index=False, encoding='utf-8')
            print(f"  -> Creado {os.path.basename(out_name)} con {len(chunk)} filas.")
    except Exception as e:
        print(f"Error procesando {filename}: {e}")

if __name__ == "__main__":
    split_file('outputs/scvs_ranking_resumen.csv', 500000)
    split_file('outputs/sri_ruc_empresas_resumen.csv', 500000)
    print("¡División terminada con éxito!")
