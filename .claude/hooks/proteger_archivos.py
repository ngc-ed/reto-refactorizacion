"""Hook PreToolUse: bloquea comandos de shell que escriben en archivos protegidos."""

import json
import re
import sys

# Rutas que solo se pueden leer (alineadas con permissions.deny de settings.json).
PROTEGIDOS = re.compile(
    r"(?<![\w.-])(tests(?:[/\\]|(?=[\s\"']|$))|pyproject\.toml"
    r"|datos_ejemplo\.json|docs[/\\]|CLAUDE\.md|\.claude[/\\])"
)

# Comandos que escriben, mueven o borran archivos (bash y PowerShell).
ESCRITURA = re.compile(
    r"\bsed\s+-i|\btee\b|\brm\b|\bmv\b|\bcp\b|\btouch\b|\btruncate\b"
    r"|\bSet-Content\b|\bAdd-Content\b|\bOut-File\b|\bClear-Content\b"
    r"|\bRemove-Item\b|\bMove-Item\b|\bCopy-Item\b|\bNew-Item\b|\bRename-Item\b"
    r"|\bgit\s+(checkout|restore|reset|rm|mv|apply|stash)\b"
    r"|--fix\b|open\(|write_text|write_bytes",
    re.IGNORECASE,
)

# Redirección a un archivo: > ruta  o  >> ruta (no cuenta 2>&1 ni >/dev/null).
REDIRECCION = re.compile(r"\d?>{1,2}\s*(?!&)[\"']?([^\s\"';|&]+)")

# Reformatea archivos completos (prohibido en CLAUDE.md).
RUFF_FORMAT = re.compile(r"\bruff\s+format\b")

# El usuario hace los commits y el push (CLAUDE.md).
GIT_PROHIBIDO = re.compile(r"\bgit\b[^|;&\n]*?\s(commit|push)\b")


def motivo_de_bloqueo(comando: str) -> str | None:
    """Devuelve por qué se bloquea el comando, o None si se permite."""
    if RUFF_FORMAT.search(comando):
        return "no ejecutar ruff format: rompe los commits atómicos (CLAUDE.md)."
    if GIT_PROHIBIDO.search(comando):
        return "git commit/push los hace el usuario: propón el mensaje."
    for destino in REDIRECCION.findall(comando):
        if PROTEGIDOS.search(destino):
            return f"redirección hacia un archivo protegido ({destino})."
    if PROTEGIDOS.search(comando) and ESCRITURA.search(comando):
        return "el comando escribe en tests/, pyproject.toml u otro archivo protegido."
    return None


def main() -> None:
    """Lee el evento del hook y sale con código 2 si hay que bloquear."""
    sys.stderr.reconfigure(encoding="utf-8")
    evento = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    comando = evento.get("tool_input", {}).get("command", "")
    motivo = motivo_de_bloqueo(comando)
    if motivo:
        print(f"Bloqueado por .claude/hooks/proteger_archivos.py: {motivo}",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
