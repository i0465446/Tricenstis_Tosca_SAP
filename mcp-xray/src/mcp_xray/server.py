"""Servidor MCP para integrar con Xray Cloud (Jira Test Management).

Expone herramientas para importar resultados de ejecución (por ejemplo,
generados por Tosca) y consultar Tests/Test Executions mediante la API
GraphQL de Xray.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver import MCPServer

from mcp_xray.xray_client import XrayClient, XrayConfig

mcp = MCPServer("xray")


def _client() -> XrayClient:
    return XrayClient(XrayConfig.from_env())


@mcp.tool()
def get_xray_config_status() -> dict:
    """Comprueba si las variables de entorno necesarias para conectar con Xray Cloud están configuradas."""
    try:
        XrayConfig.from_env()
        return {"configured": True}
    except RuntimeError as exc:
        return {"configured": False, "error": str(exc)}


@mcp.tool()
def import_execution_junit(
    project_key: str,
    junit_xml_path: str,
    test_exec_key: str | None = None,
) -> dict:
    """Importa un reporte JUnit XML (p.ej. exportado desde Tosca) como resultados de ejecución en Xray.

    Args:
        project_key: Clave del proyecto Jira (p.ej. "ABC").
        junit_xml_path: Ruta local al fichero JUnit XML con los resultados.
        test_exec_key: Clave de un Test Execution existente a actualizar; si se omite, Xray crea uno nuevo.
    """
    junit_xml = Path(junit_xml_path).read_text(encoding="utf-8")
    return _client().import_execution_junit(project_key, junit_xml, test_exec_key)


@mcp.tool()
def import_execution_results(execution: dict) -> dict:
    """Importa resultados de ejecución usando el formato JSON nativo de Xray.

    Args:
        execution: Diccionario con la forma
            {"info": {"summary": "...", "project": "ABC"},
             "tests": [{"testKey": "ABC-1", "status": "PASSED"}, ...]}
    """
    return _client().import_execution_json(execution)


_TESTS_QUERY = """
query GetTests($jql: String!, $limit: Int!) {
  getTests(jql: $jql, limit: $limit) {
    total
    results {
      issueId
      testType { name }
      jira(fields: ["key", "summary", "status"])
    }
  }
}
"""


@mcp.tool()
def search_tests(jql: str, max_results: int = 50) -> dict:
    """Busca Test issues en Xray usando JQL (p.ej. 'project = ABC AND labels = tosca')."""
    return _client().graphql(_TESTS_QUERY, {"jql": jql, "limit": max_results})


_TEST_EXECUTION_QUERY = """
query GetTestExecution($jql: String!) {
  getTestExecutions(jql: $jql, limit: 1) {
    total
    results {
      issueId
      jira(fields: ["key", "summary"])
      tests(limit: 100) {
        total
        results {
          issueId
          jira(fields: ["key", "summary"])
          status { name }
        }
      }
    }
  }
}
"""


@mcp.tool()
def get_test_execution_results(test_exec_key: str) -> dict:
    """Obtiene el estado de cada Test dentro de un Test Execution de Xray (p.ej. 'ABC-123')."""
    jql = f'key = "{test_exec_key}"'
    return _client().graphql(_TEST_EXECUTION_QUERY, {"jql": jql})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
