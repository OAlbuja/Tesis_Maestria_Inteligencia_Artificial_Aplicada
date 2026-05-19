#!/usr/bin/env python3
"""
Búsqueda de empresas en datos SRI y Superintendencia de Compañías (SCVS).

Uso:
    python buscar_empresa.py "NOMBRE DE EMPRESA"
    python buscar_empresa.py "CORPORACION FAVORITA" --threshold 70 --top 15
    python buscar_empresa.py   (modo interactivo)

Opciones:
    --threshold  Puntaje mínimo para mostrar resultado (0-100, default=60)
    --top        Máximo de resultados por fuente (default=20)
"""

import os
import sys
import glob
import unicodedata
import argparse
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRI_DIR  = os.path.join(BASE_DIR, "02_data_cleaning", "data_SRI")
SCVS_DIR = os.path.join(BASE_DIR, "02_data_cleaning", "data_super_compañias")

# ── Motor de fuzzy matching ────────────────────────────────────────────────────
try:
    from rapidfuzz import fuzz, process as rfprocess
    USE_RAPIDFUZZ = True
except ImportError:
    from difflib import SequenceMatcher
    USE_RAPIDFUZZ = False

# ── Config global (sobreescrita por args) ─────────────────────────────────────
SCORE_THRESHOLD = 60
TOP_N = 20


# ── Normalización ──────────────────────────────────────────────────────────────
def normalize(text) -> str:
    """Mayúsculas, sin acentos, sin puntuación redundante."""
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.upper().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


# ── Scoring ────────────────────────────────────────────────────────────────────
def score(query_norm: str, candidate_norm: str) -> float:
    if not candidate_norm:
        return 0.0
    if USE_RAPIDFUZZ:
        return fuzz.token_set_ratio(query_norm, candidate_norm)
    return SequenceMatcher(None, query_norm, candidate_norm).ratio() * 100


def best_scores_chunk(query_norm: str, series: pd.Series) -> pd.Series:
    """Calcula scores para una Series completa, devuelve Series de floats."""
    norm_series = series.map(normalize)
    if USE_RAPIDFUZZ:
        # rapidfuzz vectorizado sobre la lista
        names = norm_series.tolist()
        results = rfprocess.cdist(
            [query_norm], names, scorer=fuzz.token_set_ratio, workers=1
        )[0]
        return pd.Series(results, index=series.index)
    else:
        return norm_series.map(lambda x: score(query_norm, x))


# ── Búsqueda SRI ───────────────────────────────────────────────────────────────
def search_sri(query_norm: str) -> list:
    results = []
    csv_files = sorted(glob.glob(os.path.join(SRI_DIR, "SRI_RUC_*.csv")))

    for csv_path in csv_files:
        fname = os.path.basename(csv_path)
        sys.stdout.write(f"  SRI: {fname} ... ")
        sys.stdout.flush()

        try:
            # Detectar columnas desde la primera línea
            with open(csv_path, "r", encoding="latin-1") as fh:
                header_line = fh.readline().strip()
            all_cols = header_line.split("|")

            if "RAZON_SOCIAL" not in all_cols:
                print("sin columna RAZON_SOCIAL, omitido.")
                continue

            # Columna de nombre fantasia (buscar por "FANTASIA" en el nombre)
            fantasia_col = next(
                (c for c in all_cols if "FANTASIA" in c.upper()), None
            )

            keep_cols = ["NUMERO_RUC", "RAZON_SOCIAL", "ESTADO_CONTRIBUYENTE"]
            if fantasia_col:
                keep_cols.append(fantasia_col)
            usecols = [c for c in keep_cols if c in all_cols]

            file_hits = 0
            for chunk in pd.read_csv(
                csv_path,
                sep="|",
                encoding="latin-1",
                usecols=usecols,
                on_bad_lines="skip",
                chunksize=50_000,
                dtype=str,
                low_memory=False,
            ):
                chunk = chunk.fillna("")

                # Scores sobre RAZON_SOCIAL
                sc_rs = best_scores_chunk(query_norm, chunk["RAZON_SOCIAL"])
                mask = sc_rs >= SCORE_THRESHOLD

                # Scores sobre NOMBRE_FANTASIA si existe
                sc_fn = pd.Series(0.0, index=chunk.index)
                if fantasia_col and fantasia_col in chunk.columns:
                    sc_fn = best_scores_chunk(query_norm, chunk[fantasia_col])
                    mask = mask | (sc_fn >= SCORE_THRESHOLD)

                hits = chunk[mask].copy()
                if hits.empty:
                    continue

                for idx, row in hits.iterrows():
                    rs = row.get("RAZON_SOCIAL", "")
                    fn = row.get(fantasia_col, "") if fantasia_col else ""
                    s_rs = float(sc_rs.get(idx, 0))
                    s_fn = float(sc_fn.get(idx, 0)) if fantasia_col else 0.0
                    best = max(s_rs, s_fn)
                    matched = "RAZON_SOCIAL" if s_rs >= s_fn else fantasia_col

                    results.append({
                        "fuente": f"SRI / {fname}",
                        "ruc": row.get("NUMERO_RUC", ""),
                        "razon_social": rs,
                        "nombre_fantasia": fn,
                        "estado": row.get("ESTADO_CONTRIBUYENTE", ""),
                        "score": round(best, 1),
                        "columna_match": matched,
                    })
                    file_hits += 1

            print(f"{file_hits} hit(s)")

        except Exception as exc:
            print(f"ERROR -> {exc}")

    return results


# ── Búsqueda SCVS ──────────────────────────────────────────────────────────────
def search_scvs(query_norm: str) -> list:
    results = []
    xlsx_files = sorted([
        f for f in glob.glob(os.path.join(SCVS_DIR, "*.xlsx"))
        if "ranking" not in os.path.basename(f).lower()
    ])

    for xlsx_path in xlsx_files:
        fname = os.path.basename(xlsx_path)
        sys.stdout.write(f"  SCVS: {fname} ... ")
        sys.stdout.flush()

        loaded = False
        for header_row in range(8):
            try:
                df = pd.read_excel(xlsx_path, header=header_row, dtype=str)
                df = df.fillna("")
                named_cols = [c for c in df.columns if not str(c).startswith("Unnamed")]
                if len(named_cols) < 3 or "NOMBRE" not in df.columns:
                    continue

                sc = best_scores_chunk(query_norm, df["NOMBRE"])
                mask = sc >= SCORE_THRESHOLD
                hits = df[mask].copy()
                file_hits = 0

                if not hits.empty:
                    id_col = next(
                        (c for c in ["RUC", "IDENTIFICACIÓN", "IDENTIFICACION", "EXPEDIENTE"]
                         if c in df.columns), None
                    )
                    for idx, row in hits.iterrows():
                        nombre = row.get("NOMBRE", "")
                        s = float(sc.get(idx, 0))

                        detail_keys = [
                            c for c in df.columns
                            if c not in ["NOMBRE", "No. FILA", "!CODIGO!"]
                            and not str(c).startswith("Unnamed")
                            and row.get(c, "")
                        ]
                        detalles = {k: row[k] for k in detail_keys[:8]}

                        results.append({
                            "fuente": f"SCVS / {fname}",
                            "id": row.get(id_col, "") if id_col else "",
                            "nombre": nombre,
                            "score": round(s, 1),
                            "columna_match": "NOMBRE",
                            "detalles": detalles,
                        })
                        file_hits += 1

                print(f"{file_hits} hit(s)")
                loaded = True
                break

            except Exception:
                continue

        if not loaded:
            print("no se pudo leer.")

    return results


# ── Display ────────────────────────────────────────────────────────────────────
def display_results(sri_results: list, scvs_results: list, query: str):
    line = "=" * 72

    print(f"\n{line}")
    print(f"  RESULTADOS PARA: \"{query}\"")
    print(line)

    # ── SRI ──
    sri_sorted = sorted(sri_results, key=lambda x: x["score"], reverse=True)[:TOP_N]
    print(f"\n{'─'*72}")
    print(f"  SRI — RUC  |  {len(sri_results)} coincidencias  (mostrando top {len(sri_sorted)})")
    print(f"{'─'*72}")
    if not sri_sorted:
        print("  Sin resultados.")
    else:
        for r in sri_sorted:
            print(f"  [{r['score']:5.1f}%]  RUC: {r['ruc']}")
            print(f"           RAZÓN SOCIAL     : {r['razon_social']}")
            if r["nombre_fantasia"]:
                print(f"           NOMBRE COMERCIAL  : {r['nombre_fantasia']}")
            extras = []
            if r["estado"]:
                extras.append(f"ESTADO: {r['estado']}")
            extras.append(f"match en: {r['columna_match']}")
            print(f"           {' | '.join(extras)}")
            print(f"           Fuente: {r['fuente']}")
            print()

    # ── SCVS ──
    scvs_sorted = sorted(scvs_results, key=lambda x: x["score"], reverse=True)[:TOP_N]
    print(f"\n{'─'*72}")
    print(f"  SCVS — Superintendencia  |  {len(scvs_results)} coincidencias  (mostrando top {len(scvs_sorted)})")
    print(f"{'─'*72}")
    if not scvs_sorted:
        print("  Sin resultados.")
    else:
        for r in scvs_sorted:
            print(f"  [{r['score']:5.1f}%]  ID/RUC: {r['id']}")
            print(f"           NOMBRE: {r['nombre']}")
            for k, v in list(r.get("detalles", {}).items())[:6]:
                if v:
                    print(f"           {k}: {v}")
            print(f"           Fuente: {r['fuente']}")
            print()

    total = len(sri_results) + len(scvs_results)
    print(line)
    print(f"  Total: {len(sri_results)} en SRI  +  {len(scvs_results)} en SCVS  =  {total} coincidencias")
    print(f"  (umbral >= {SCORE_THRESHOLD}%  |  motor: {'rapidfuzz' if USE_RAPIDFUZZ else 'difflib'})")
    print(f"{line}\n")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Busca una empresa en datos SRI y Superintendencia de Compañías"
    )
    parser.add_argument("nombre", nargs="?", help="Nombre de la empresa")
    parser.add_argument(
        "--threshold", type=int, default=60,
        help="Umbral mínimo de score 0-100 (default: 60)"
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="Máximo de resultados por fuente (default: 20)"
    )
    args = parser.parse_args()

    global SCORE_THRESHOLD, TOP_N
    SCORE_THRESHOLD = max(0, min(100, args.threshold))
    TOP_N = max(1, args.top)

    if args.nombre:
        query = args.nombre.strip()
    else:
        query = input("Ingrese el nombre de la empresa a buscar: ").strip()

    if not query:
        print("Error: debe ingresar un nombre.")
        sys.exit(1)

    query_norm = normalize(query)
    engine_name = "rapidfuzz (token_set_ratio)" if USE_RAPIDFUZZ else "difflib (instale rapidfuzz para mejor rendimiento)"

    print(f'\nBuscando: "{query}"')
    print(f"Motor: {engine_name}  |  Umbral: {SCORE_THRESHOLD}%  |  Top: {TOP_N}")
    print("\n[1/2] Escaneando archivos SRI...")
    sri_results = search_sri(query_norm)

    print("\n[2/2] Escaneando archivos SCVS...")
    scvs_results = search_scvs(query_norm)

    display_results(sri_results, scvs_results, query)


if __name__ == "__main__":
    main()
