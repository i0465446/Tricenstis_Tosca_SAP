# mcp-xray

Servidor MCP (Model Context Protocol) para integrar con **Xray Cloud**, el
plugin de gestión de tests de Jira. Permite importar resultados de ejecución
(por ejemplo, generados por Tosca) y consultar Tests/Test Executions desde
Claude Code u otros clientes MCP.

## Herramientas expuestas

- `get_xray_config_status`: comprueba si las credenciales están configuradas.
- `import_execution_junit(project_key, junit_xml_path, test_exec_key=None)`:
  sube un reporte JUnit XML como resultados de ejecución. Si `test_exec_key`
  se omite, Xray crea un nuevo Test Execution.
- `import_execution_results(execution)`: sube resultados usando el formato
  JSON nativo de Xray (`{"info": {...}, "tests": [...]}`), útil cuando los
  resultados no vienen en JUnit.
- `search_tests(jql, max_results=50)`: busca Test issues por JQL.
- `get_test_execution_results(test_exec_key)`: devuelve el estado de cada
  Test dentro de un Test Execution.

## Requisitos

- Una API Key de Xray Cloud: en Jira, **Global Settings > Apps > Xray > API
  Keys > "+ API Key"**. Genera un Client ID y Client Secret.
- Python 3.10+.

## Instalación

```bash
cd mcp-xray
pip install -e .
```

## Configuración de credenciales

Copia `.env.example` a `.env` (o define las variables en tu entorno) y
rellena `XRAY_CLIENT_ID` y `XRAY_CLIENT_SECRET` con la API Key generada
arriba.

## Registrar el servidor en Claude Code (alcance de usuario)

```bash
claude mcp add xray --scope user \
  --env XRAY_CLIENT_ID=tu-client-id \
  --env XRAY_CLIENT_SECRET=tu-client-secret \
  -- xray-mcp-server
```

Verifica:

```bash
claude mcp list
```

## Flujo combinado con mcp-tosca

1. Ejecuta la ExecutionList con `run_tosca_execution_list` (de `mcp-tosca`).
2. Exporta/localiza el reporte de resultados de Tosca en formato JUnit XML
   (Tosca puede generarlo desde su módulo de Reporting/ToscaCI).
3. Sube ese XML a Xray con `import_execution_junit`, indicando el
   `test_exec_key` si quieres actualizar una ejecución ya creada en el Test
   Plan/Sprint correspondiente.
4. Comprueba el resultado en Jira con `get_test_execution_results`.
