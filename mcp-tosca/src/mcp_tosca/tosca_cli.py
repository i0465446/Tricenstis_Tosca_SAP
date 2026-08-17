"""Wrapper sobre TestExecutionCli, el CLI de Tricentis Tosca Commander/TBox
usado para disparar ExecutionLists desde procesos externos (CI/CD, agentes, etc.)."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

REQUIRED_ENV_VARS = (
    "TOSCA_CLI_PATH",
    "TOSCA_DB_TYPE",
    "TOSCA_DB_SERVER",
    "TOSCA_SERVER",
    "TOSCA_LOGIN",
    "TOSCA_PASSWORD_ENV",
    "TOSCA_PROJECT",
)


@dataclass
class ToscaConnectionConfig:
    cli_path: str
    database_type: str
    database_server: str
    server: str
    login: str
    password_env: str
    project: str
    tcp: str | None = None

    @classmethod
    def from_env(cls) -> "ToscaConnectionConfig":
        missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
        if missing:
            raise RuntimeError(
                "Faltan variables de entorno para conectar con Tosca: "
                + ", ".join(missing)
                + ". Revisa mcp-tosca/.env.example."
            )
        if not os.environ.get(os.environ["TOSCA_PASSWORD_ENV"]):
            raise RuntimeError(
                f"TOSCA_PASSWORD_ENV apunta a '{os.environ['TOSCA_PASSWORD_ENV']}' "
                "pero esa variable no está definida o está vacía."
            )
        return cls(
            cli_path=os.environ["TOSCA_CLI_PATH"],
            database_type=os.environ["TOSCA_DB_TYPE"],
            database_server=os.environ["TOSCA_DB_SERVER"],
            server=os.environ["TOSCA_SERVER"],
            login=os.environ["TOSCA_LOGIN"],
            password_env=os.environ["TOSCA_PASSWORD_ENV"],
            project=os.environ["TOSCA_PROJECT"],
            tcp=os.environ.get("TOSCA_TCP"),
        )

    def base_args(self) -> list[str]:
        args = [
            self.cli_path,
            "-DatabaseType", self.database_type,
            "-DatabaseServer", self.database_server,
            "-Server", self.server,
            "-Login", self.login,
            "-Password_env", self.password_env,
            "-Project", self.project,
        ]
        if self.tcp:
            args += ["-TCP", self.tcp]
        return args


def run_execution_list(
    config: ToscaConnectionConfig,
    execution_list: str,
    timeout_seconds: int = 3600,
) -> dict:
    """Lanza TestExecutionCli.exe contra la ExecutionList indicada.

    La contraseña nunca se pasa por línea de comandos: TestExecutionCli la lee
    de la variable de entorno señalada por -Password_env, así que no aparece
    en logs de proceso ni en la salida de esta herramienta.
    """
    args = config.base_args() + ["-ExecutionList", execution_list]
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"No se encontró el ejecutable de Tosca en '{config.cli_path}'. "
            "Comprueba TOSCA_CLI_PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timed_out": False,
    }
