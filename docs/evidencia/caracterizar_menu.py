import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.getcwd()
MAIN = os.path.join(RAIZ, "src", "main.py")

ESCENARIOS = {
    "A_con_datos_de_ejemplo": (
        True,
        "2\nA001\n2\n\n2\nA001\n1\nVIP01\n3\nA002\n20\n4\n5\n6\n7\n8\n",
    ),
    "B_ampliada_sin_archivo": (
        False,
        "1\nZ001\nProducto zeta\nabc\n0.5\n4.9\n1\nZ001\nDup\n10\n1\n1\nZ002\nBarato\n10\n100\n"
        "9\n2\nZ001\n1000\nVIP9\n2\nZ002\n21\nVIP1\n2\nZ002\n1.9\nvip\n2\n\n1\n\n"
        "3\nNOPE\n1\n3\nZ001\n0\n3\nZ002\n50\n4\n6\n7\n5\n8\n",
    ),
    "C_reportes_vacios": (False, "4\n5\n6\n7\n\nx\n8\n"),
}

for nombre, (con_datos, entrada) in ESCENARIOS.items():
    with tempfile.TemporaryDirectory() as tmp:
        if con_datos:
            shutil.copy(os.path.join(RAIZ, "datos_ejemplo.json"), tmp)
        r = subprocess.run(
            [sys.executable, MAIN], input=entrada, capture_output=True,
            text=True, encoding="utf-8", cwd=tmp,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        print(f"===== {nombre} (codigo de salida {r.returncode})")
        print(r.stdout)
        if r.stderr:
            print("--- stderr\n" + r.stderr)
        ruta = os.path.join(tmp, "datos_ejemplo.json")
        print("--- datos_ejemplo.json guardado (sin fechas)")
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                print("".join(ln for ln in f if '"fecha"' not in ln))
        else:
            print("(no se genero archivo)")