# Tricenstis_Tosca_SAP

Herramientas de integración entre Tricentis Tosca y SAP.

- [`docs/tosca-official-mcp-server.md`](docs/tosca-official-mcp-server.md):
  **cómo conectar el servidor MCP oficial** incluido en Tosca 2026.1 (patch
  1+) — la vía recomendada, sin instalar nada.
- [`mcp-tosca`](mcp-tosca/README.md): servidor MCP alternativo para disparar
  ExecutionLists de Tosca Commander/TBox por CLI (CI/CD headless o versiones
  de Tosca sin soporte MCP nativo).
- [`mcp-xray`](mcp-xray/README.md): servidor MCP para importar resultados de
  ejecución (p.ej. desde Tosca) y consultar Tests/Test Executions en Xray
  Cloud (Jira).
