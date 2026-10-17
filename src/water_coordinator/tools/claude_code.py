"""Proveedor de IA sin API key: usa el Claude Code instalado con la app de escritorio y la sesión de la usuaria.

Expone solo `create()`, que es lo único que usa el sistema (Agente 1 y `estado --comprobar`).
shortcut: llamada de un turno por subproceso (~38k tokens de prompt base, cacheados 1 h); para producción, usar la API.
"""

import asyncio
import json
import os
import shutil
from pathlib import Path

from autogen_core.models import CreateResult, LLMMessage, RequestUsage, SystemMessage


def ruta_claude(configurada: str = "") -> str | None:
    """Ejecutable configurado, el `claude` del PATH o la versión más reciente incluida en la app de escritorio."""
    if configurada:
        return configurada if Path(configurada).is_file() else None
    if encontrado := shutil.which("claude"):
        return encontrado
    base = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude-code"
    candidatos = sorted(base.glob("*/*/claude.exe"), key=lambda p: p.stat().st_mtime) if base.is_dir() else []
    return str(candidatos[-1]) if candidatos else None


class ClaudeCodeClient:
    def __init__(self, ejecutable: str, modelo: str, timeout: float = 120):
        self.ejecutable, self.modelo, self.timeout = ejecutable, modelo, timeout

    async def create(self, messages: list[LLMMessage], **_: object) -> CreateResult:
        sistema = "\n".join(str(m.content) for m in messages if isinstance(m, SystemMessage))
        usuario = "\n".join(str(m.content) for m in messages if not isinstance(m, SystemMessage))
        args = ["-p", "--output-format", "json", "--model", self.modelo, "--tools", "", "--no-session-persistence",
                "--setting-sources", ""]
        if sistema:
            args += ["--system-prompt", sistema]
        datos = await self._ejecutar(args, usuario)
        if datos.get("is_error"):
            raise RuntimeError(f"Claude Code devolvió un error: {str(datos.get('result'))[:200]}")
        u = datos.get("usage", {})
        entrada = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
        return CreateResult(finish_reason="stop", content=str(datos.get("result", "")), cached=False,
                            usage=RequestUsage(prompt_tokens=entrada, completion_tokens=u.get("output_tokens", 0)))

    async def _ejecutar(self, args: list[str], entrada: str) -> dict:
        # Sin ANTHROPIC_API_KEY en el entorno: Claude Code usa la sesión iniciada en la app, no créditos de la API.
        entorno = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        proc = await asyncio.create_subprocess_exec(
            self.ejecutable, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, env=entorno, cwd=os.environ.get("TEMP") or None,
        )
        try:
            salida, error = await asyncio.wait_for(proc.communicate(entrada.encode("utf-8")), self.timeout)
        except TimeoutError:
            proc.kill()
            raise
        if proc.returncode != 0:
            raise RuntimeError(f"Claude Code terminó con código {proc.returncode}: {error.decode('utf-8', 'replace')[:200]}")
        return json.loads(salida.decode("utf-8"))
