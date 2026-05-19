#!/usr/bin/env python
r"""
convert_notebooks_to_pdf.py
============================
Convierte todos los notebooks .ipynb del proyecto a PDF y los guarda en:
    E:\TESIS MAESTRIA\Desarrollo_clustering_maestria\00_Documentacion\IPYNB_PROYECTO_PDF

Orden de recorrido: alfabético por carpeta, luego alfabético por nombre de archivo.
Nomenclatura de salida: {secuencia_global:03d}__{carpeta}__{nombre_original}.pdf
  Ejemplo:
    001__01_data_ingestion_enrichment__01_profiling_fuentes_validacion_join.pdf
    002__02_data_cleaning__01_staging_empresas_normalizadas.pdf
    003__02_data_cleaning__02_matching_exacto_scvs.pdf
    ...

Método de conversión (en orden de preferencia):
  1. nbconvert --to pdf     (requiere LaTeX / MiKTeX — disponible en el sistema)
  2. nbconvert --to html    (respaldo sin dependencias externas)

Requisitos:
  pip install nbconvert
  MiKTeX o TeX Live instalado en el sistema
"""

import subprocess
import sys
from pathlib import Path

# Timeout por notebook en segundos (5 minutos). Aumentar si los notebooks son muy pesados.
NBCONVERT_TIMEOUT = 300

# ── Configuración ─────────────────────────────────────────────────────────────

ROOT = Path(r"E:\TESIS MAESTRIA\Desarrollo_clustering_maestria")

OUTPUT_DIR = Path(
    r"E:\TESIS MAESTRIA\Desarrollo_clustering_maestria"
    r"\00_Documentacion\IPYNB_PROYECTO_PDF"
)

# Carpetas de primer nivel que se EXCLUYEN del recorrido
EXCLUDE_FOLDERS = {
    "00_Documentacion",
    "venv",
    ".venv",
    ".git",
    "__pycache__",
    "node_modules",
}

# Notebooks sueltos en la raíz que se EXCLUYEN (copias, borradores, etc.)
EXCLUDE_ROOT_NOTEBOOKS = {
    "copia_01_profiling_empresas_profesional_con_matching - copia.ipynb",
}

# Mostrar solo outputs (True) u outputs + código (False)
HIDE_CODE = False

# ── Recopilación de notebooks ─────────────────────────────────────────────────

def collect_notebooks() -> list[dict]:
    """
    Devuelve lista ordenada de dicts con {path, label} donde label es
    la carpeta de origen para usarla en el nombre del PDF.
    Orden: carpetas raíz primero (00_..., 01_..., ...) → dentro de cada
    carpeta, notebooks ordenados alfabéticamente.
    """
    entries = []

    # 1) Notebooks en la raíz del proyecto (excluir copias/borradores)
    root_nbs = sorted(
        p for p in ROOT.glob("*.ipynb")
        if p.name not in EXCLUDE_ROOT_NOTEBOOKS
    )
    for nb in root_nbs:
        entries.append({"path": nb, "folder_label": "00_raiz"})

    # 2) Subcarpetas de primer nivel, en orden alfabético
    for folder in sorted(f for f in ROOT.iterdir() if f.is_dir()):
        if folder.name in EXCLUDE_FOLDERS or folder.name.startswith("."):
            continue
        nbs = sorted(folder.glob("*.ipynb"))
        for nb in nbs:
            entries.append({"path": nb, "folder_label": folder.name})

    return entries


# ── Conversión ────────────────────────────────────────────────────────────────

def build_output_name(seq: int, folder_label: str, nb_stem: str) -> str:
    """Construye el nombre de archivo de salida con prefijo secuencial."""
    return f"{seq:03d}__{folder_label}__{nb_stem}"


def run_nbconvert(python_exe: str, fmt: str, nb_path: Path, out_stem: str, out_dir: Path) -> bool:
    """Ejecuta jupyter nbconvert y retorna True si tiene éxito."""
    cmd = [
        python_exe, "-m", "jupyter", "nbconvert",
        "--to", fmt,
        "--output", out_stem,
        "--output-dir", str(out_dir),
        str(nb_path),
    ]
    if HIDE_CODE and fmt in ("pdf", "html"):
        cmd.insert(4, "--no-input")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=NBCONVERT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        print(f"        [TIMEOUT] La conversión superó {NBCONVERT_TIMEOUT}s y fue cancelada.")
        return False

    if result.returncode != 0:
        stderr_tail = "\n".join(result.stderr.strip().splitlines()[-6:])
        print(f"        [stderr] {stderr_tail}")
    return result.returncode == 0


def convert_notebook(nb_path: Path, out_stem: str, python_exe: str) -> str:
    """
    Intenta convertir el notebook a PDF via LaTeX.
    Si falla, genera HTML como respaldo.
    Retorna: 'pdf' | 'html' | 'error' según el método que funcionó.
    """
    # Intento 1: pdf estándar (requiere LaTeX / MiKTeX)
    if run_nbconvert(python_exe, "pdf", nb_path, out_stem, OUTPUT_DIR):
        return "pdf"

    print(f"        → PDF falló, generando HTML de respaldo…")

    # Respaldo: HTML (sin dependencias externas)
    if run_nbconvert(python_exe, "html", nb_path, out_stem, OUTPUT_DIR):
        return "html"

    return "error"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    python_exe = sys.executable
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    notebooks = collect_notebooks()
    if not notebooks:
        print("No se encontraron notebooks en el proyecto.")
        return

    total = len(notebooks)
    print(f"Notebooks encontrados: {total}")
    print(f"Directorio de salida : {OUTPUT_DIR}\n")
    print("=" * 72)

    results = {"pdf": [], "html": [], "error": []}

    for i, entry in enumerate(notebooks, start=1):
        nb: Path = entry["path"]
        folder_label: str = entry["folder_label"]
        out_stem = build_output_name(i, folder_label, nb.stem)

        print(f"[{i:03d}/{total}] {nb.relative_to(ROOT)}")
        print(f"         → {out_stem}.pdf")

        status = convert_notebook(nb, out_stem, python_exe)
        results[status].append(out_stem)

        icon = {"pdf": "✓", "html": "⚠ (HTML)", "error": "✗"}[status]
        print(f"         {icon} {status.upper()}\n")

    # ── Resumen ───────────────────────────────────────────────────────────────
    print("=" * 72)
    ok_count = len(results["pdf"])
    html_count = len(results["html"])
    err_count = len(results["error"])

    print(f"Resumen: {ok_count} PDF OK | {html_count} HTML (respaldo) | {err_count} errores")

    if results["html"]:
        print("\nConvertidos a HTML (respaldo — verifica instalación de LaTeX/MiKTeX):")
        for name in results["html"]:
            print(f"  ⚠  {name}.html")

    if results["error"]:
        print("\nFallaron completamente:")
        for name in results["error"]:
            print(f"  ✗  {name}")

    if ok_count == total:
        print("\n✓ Todos los notebooks convertidos exitosamente a PDF.")
    elif results["html"] or results["error"]:
        print(
            "\nAlgunos notebooks no se convirtieron a PDF.\n"
            "Verifica que MiKTeX esté instalado y accesible desde la terminal:\n"
            "  xelatex --version"
        )


if __name__ == "__main__":
    main()
