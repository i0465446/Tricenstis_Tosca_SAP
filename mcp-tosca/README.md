# mcp-tosca

Servidor MCP (Model Context Protocol) que expone herramientas para disparar
ejecuciones de Tricentis Tosca Commander/TBox mediante `TestExecutionCli`, el
CLI oficial que Tosca instala para integraciones de CI/CD.

## Herramientas expuestas

- `get_tosca_config_status`: comprueba si las variables de entorno de conexión
  están correctamente configuradas.
- `run_tosca_execution_list(execution_list, timeout_seconds=3600)`: ejecuta una
  ExecutionList de Tosca y devuelve `returncode`, `stdout`, `stderr`.

## Requisitos

- Windows con Tosca Commander/TBox instalado (el CLI `TestExecutionCli.exe`
  solo existe en instalaciones de Tosca).
- Python 3.10+.
- Acceso de red al servidor/repositorio Tosca configurado.

## Instalación

```bash
cd mcp-tosca
pip install -e .
```

Esto instala el paquete y crea el comando `tosca-mcp-server`.

## Configuración de credenciales

1. Copia `.env.example` a `.env` (o define las variables directamente en tu
   entorno de usuario de Windows).
2. Rellena `TOSCA_CLI_PATH`, `TOSCA_DB_TYPE`, `TOSCA_DB_SERVER`,
   `TOSCA_SERVER`, `TOSCA_LOGIN` y `TOSCA_PROJECT` con los datos de tu
   repositorio Tosca.
3. `TOSCA_PASSWORD_ENV` debe contener el **nombre** de otra variable de
   entorno (por ejemplo `TOSCA_PASSWORD`) donde guardes la contraseña real.
   Así la contraseña nunca se pasa por línea de comandos ni queda en logs de
   proceso.

## Registrar el servidor en Claude Code (alcance de usuario)

Una vez instalado, regístralo para que esté disponible en todos tus proyectos:

```bash
claude mcp add tosca --scope user -- tosca-mcp-server
```

Verifica que quedó registrado:

```bash
claude mcp list
```

Y que las variables de entorno estén disponibles en la sesión donde arranques
Claude Code (o defínelas en el propio comando de registro con `--env`):

```bash
claude mcp add tosca --scope user \
  --env TOSCA_CLI_PATH="C:\Program Files (x86)\TRICENTIS\Tosca Testsuite\TestExecutionCli\TestExecutionCli.exe" \
  --env TOSCA_DB_TYPE=MSSQL_TOSCACI \
  --env TOSCA_DB_SERVER="mi-servidor-sql\INSTANCIA" \
  --env TOSCA_SERVER=mi-servidor-tosca \
  --env TOSCA_LOGIN=mi.usuario \
  --env TOSCA_PASSWORD_ENV=TOSCA_PASSWORD \
  --env TOSCA_PASSWORD=******** \
  --env TOSCA_PROJECT=MiProyecto \
  -- tosca-mcp-server
```

## Extender a SAP

Este servidor solo cubre Tosca por ahora. Cuando se necesite integrar SAP
(OData o RFC/BAPI), se puede añadir un módulo `mcp_tosca/sap_client.py` con
sus propias herramientas `@mcp.tool()` dentro de `server.py`, siguiendo el
mismo patrón de configuración vía variables de entorno.
