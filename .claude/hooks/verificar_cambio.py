"""Hook PostToolUse: corre pytest y ruff después de editar un .py de src/."""

import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(
    os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]
)


def correr(*args: str) -> subprocess.CompletedProcess:
    """Ejecuta un módulo de Python del venv en la raíz del proyecto."""
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", *args], cwd=RAIZ, capture_output=True,
        text=True, encoding="utf-8", errors="replace", env=entorno,
    )


def main() -> None:
    """Verifica el cambio y avisa a Claude; código 2 si pytest falla."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    evento = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    ruta = evento.get("tool_input", {}).get("file_path", "").replace("\\", "/")
    if "/src/" not in ruta or not ruta.endswith(".py"):
        return

    pruebas = correr("pytest", "-q")
    ruff = correr("ruff", "check", "src", "--statistics")
    resumen_pytest = (pruebas.stdout.strip().splitlines() or ["(sin salida)"])[-1]
    resumen_ruff = ruff.stdout.strip() or "0 errores"

    if pruebas.returncode != 0:
        print(f"pytest FALLA tras editar {ruta}:\n{pruebas.stdout[-3000:]}",
              file=sys.stderr)
        sys.exit(2)

    contexto = (f"Verificación automática tras editar {ruta}:\n"
                f"pytest: {resumen_pytest}\nruff check src:\n{resumen_ruff}")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse", "additionalContext": contexto}}))


if __name__ == "__main__":
    main()
