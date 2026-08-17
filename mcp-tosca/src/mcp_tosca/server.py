"""Servidor MCP para Tricentis Tosca Commander/TBox.

Expone herramientas que permiten a un agente disparar ExecutionLists de Tosca
a través de TestExecutionCli y comprobar la configuración de conexión.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from mcp_tosca.tosca_cli import ToscaConnectionConfig, run_execution_list

mcp = MCPServer("tosca")


@mcp.tool()
def get_tosca_config_status() -> dict:
    """Comprueba si las variables de entorno necesarias para conectar con Tosca están configuradas."""
    try:
        ToscaConnectionConfig.from_env()
        return {"configured": True}
    except RuntimeError as exc:
        return {"configured": False, "error": str(exc)}


@mcp.tool()
def run_tosca_execution_list(execution_list: str, timeout_seconds: int = 3600) -> dict:
    """Ejecuta una ExecutionList de Tricentis Tosca mediante TestExecutionCli.

    Args:
        execution_list: Ruta o nombre completo de la ExecutionList dentro del proyecto Tosca.
        timeout_seconds: Tiempo máximo de espera antes de abortar la ejecución.
    """
    config = ToscaConnectionConfig.from_env()
    return run_execution_list(config, execution_list, timeout_seconds=timeout_seconds)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
