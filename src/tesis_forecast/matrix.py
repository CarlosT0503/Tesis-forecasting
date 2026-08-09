"""
run_matrix(): cola minima de experimentos, ejecutados secuencialmente.

No es scheduler ni infraestructura de nube -- es un loop sobre
`run_experiment()` que:
  - salta configs ya completadas (`validar_resultado`);
  - reanuda automaticamente carpetas incompletas/fallidas de una corrida
    anterior (`overwrite=True`, seguro: `run_experiment` ya se niega a
    tocar una carpeta completa aunque se pida overwrite). Reanudar YA NO
    borra la carpeta ni recalcula las 8 regiones desde cero -- cada modelo
    salta, region por region, las que ya tienen un resultado completo y
    valido (ver `checkpoint.py` y docs/CHECKPOINT_RESUME.md);
  - continua con la siguiente config si una falla, registrando el error;
  - al final imprime un resumen de completadas/saltadas/fallidas y el MAPE
    promedio de cada una.

Disparo (cron, notebook programado, etc.) queda fuera de alcance por
ahora -- ver docs/AUTOMATIZACION_FUTURA.md.
"""

import os
import traceback
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from . import io_drive
from .config import ExperimentConfig
from .runner import resolve_run, run_experiment
from .validator import validar_resultado


@dataclass
class MatrixRunRecord:
    config: ExperimentConfig
    run_name: Optional[str]
    status: str  # "completed" | "skipped_ya_completo" | "failed"
    mape_promedio: Optional[float]
    error: Optional[str]
    run_dir: Optional[str]


def run_matrix(
    configs: list,
    data_dir: str = "/content",
    mount_drive: bool = True,
) -> list:
    """Corre una lista de ExperimentConfig, una por una. Devuelve una lista
    de MatrixRunRecord (uno por config, en el mismo orden)."""

    if mount_drive:
        io_drive.mount_drive()

    registros = []

    for i, config in enumerate(configs):
        print("\n" + "#" * 80)
        print(f"# Experimento {i + 1}/{len(configs)}: modelo={config.modelo}")
        print("#" * 80)

        try:
            resolved = resolve_run(config)
        except Exception as e:
            print(f"Config invalida: {type(e).__name__}: {e}")
            registros.append(MatrixRunRecord(config, None, "failed", None, str(e), None))
            continue

        run_dir = resolved.run_dir
        overwrite = False

        if os.path.exists(run_dir):
            reporte = validar_resultado(run_dir)

            if reporte.es_completo:
                print(f"YA COMPLETO, se salta: {resolved.run_name}")
                registros.append(
                    MatrixRunRecord(config, resolved.run_name, "skipped_ya_completo", None, None, run_dir)
                )
                continue

            print(f"Carpeta incompleta detectada para {resolved.run_name}:")
            for problema in reporte.problemas:
                print(f"  - {problema}")
            print("Se reintenta (overwrite=True).")
            overwrite = True

        try:
            resultado = run_experiment(config, data_dir=data_dir, mount_drive=False, overwrite=overwrite)

            registros.append(MatrixRunRecord(
                config, resultado.run_name, "completed",
                resultado.mape_promedio, None, resultado.run_dir,
            ))

        except Exception as e:
            print(f"FALLO: {type(e).__name__}: {e}")
            print(traceback.format_exc())

            registros.append(MatrixRunRecord(
                config, resolved.run_name, "failed", None, f"{type(e).__name__}: {e}", run_dir,
            ))
            continue

    _imprimir_resumen(registros)

    return registros


def _imprimir_resumen(registros: list):
    completadas = [r for r in registros if r.status == "completed"]
    saltadas = [r for r in registros if r.status == "skipped_ya_completo"]
    fallidas = [r for r in registros if r.status == "failed"]

    print("\n" + "=" * 80)
    print("RESUMEN DE LA COLA")
    print("=" * 80)
    print(f"Total:        {len(registros)}")
    print(f"Completadas:  {len(completadas)}")
    print(f"Saltadas:     {len(saltadas)} (ya estaban completas)")
    print(f"Fallidas:     {len(fallidas)}")

    if completadas:
        print("\nCompletadas (MAPE promedio):")
        for r in completadas:
            mape_str = f"{r.mape_promedio:.2f}%" if r.mape_promedio is not None else "N/D"
            print(f"  - {r.run_name}: MAPE={mape_str}")

    if fallidas:
        print("\nFallidas:")
        for r in fallidas:
            nombre = r.run_name or f"modelo={r.config.modelo} (config invalida)"
            print(f"  - {nombre}: {r.error}")

    if saltadas:
        print("\nSaltadas (ya completas):")
        for r in saltadas:
            print(f"  - {r.run_name}")


def resumen_dataframe(registros: list) -> pd.DataFrame:
    """Version tabular del resumen, util para revisar en un notebook."""
    filas = []
    for r in registros:
        filas.append({
            "modelo": r.config.modelo,
            "run_name": r.run_name,
            "status": r.status,
            "mape_promedio": r.mape_promedio,
            "error": r.error,
            "run_dir": r.run_dir,
        })
    return pd.DataFrame(filas)
