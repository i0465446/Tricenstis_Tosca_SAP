# Servidor MCP oficial de Tricentis Tosca (recomendado)

Desde **Tosca 2026.1 (patch 1 o posterior)**, Tricentis incluye un servidor
MCP (Model Context Protocol) integrado directamente en Tosca Commander. Esta
es la vía **recomendada** para conectar un asistente de IA a Tosca: no
requiere instalar Python, Node.js ni ningún paquete adicional — solo
habilitar un addin que ya viene con la instalación de Tosca.

> A diferencia de [`mcp-tosca`](../mcp-tosca/README.md) (el wrapper
> personalizado de este repo sobre `TestExecutionCli`, pensado para disparar
> ExecutionLists desde CI/CD), el servidor oficial se ejecuta dentro de Tosca
> Commander y expone acceso más amplio al workspace: crear, organizar,
> actualizar, usar y ejecutar test assets. Úsalo si tu versión de Tosca lo
> soporta; usa `mcp-tosca` solo si necesitas disparar ejecuciones por CLI en
> un entorno sin Tosca Commander abierto (p.ej. un agente de CI headless).

## Requisitos previos

- Tosca 2026.1 con el patch 1 (o posterior) instalado.
- Un puerto HTTP libre en el rango 1024–65535 en la máquina donde corre Tosca
  Commander.
- Tu asistente de IA debe soportar conectores MCP remotos por HTTP (revisa su
  documentación: los requisitos varían según la app — por ejemplo, algunas
  versiones de Claude Desktop requieren tener Node.js instalado).

## 1. Habilitar el addin del servidor MCP en Tosca Commander

En **cada máquina** donde quieras usar el asistente de IA con Tosca:

1. Abre Tosca Commander.
2. Ve a **Project > Options > McpServerAddin**.
3. Marca **Enabled**.
4. Introduce el **Port** que usará el asistente de IA para comunicarse con el
   servidor MCP de Tosca (debe estar libre, entre 1024 y 65535).

## 2. Configurar la autenticación

Crea una variable de entorno de sistema en Windows:

- **Nombre:** `MCP_LOCAL_AUTH_TOKEN`
- **Valor:** una cadena aleatoria (trátala como una contraseña — no la
  compartas ni la subas a ningún repositorio).

```powershell
setx MCP_LOCAL_AUTH_TOKEN "<cadena-aleatoria-larga>" /M
```

(`/M` la define a nivel de máquina; sin `/M` queda solo a nivel de usuario —
cualquiera de las dos funciona, usa la que tus permisos permitan). Reinicia
Tosca Commander después de definirla para que la recoja.

## 3. Conectar tu asistente de IA

El servidor queda accesible en `http://localhost:<puerto>`, con autenticación
`Bearer <token>` en la cabecera `Authorization`.

### Claude Code (CLI)

```bash
claude mcp add-json httpcommander '{"type":"http","url":"http://localhost:<puerto>","headers":{"Authorization":"Bearer ${MCP_LOCAL_AUTH_TOKEN}"}}'
```

Ejemplo con puerto 1025:

```bash
claude mcp add-json httpcommander '{"type":"http","url":"http://localhost:1025","headers":{"Authorization":"Bearer ${MCP_LOCAL_AUTH_TOKEN}"}}'
```

### Claude Desktop / apps con conector HTTP por URL

Si tu app tiene una sección de **Settings > Connectors** que pide una URL (y
opcionalmente cabeceras), usa:

- **URL:** `http://localhost:<puerto>`
- **Header:** `Authorization: Bearer <valor-real-de-MCP_LOCAL_AUTH_TOKEN>`

Revisa la documentación oficial de tu asistente concreto, porque el soporte
de conectores HTTP locales varía y cambia con frecuencia entre versiones.

## Referencia

Basado en la documentación oficial de Tricentis:
<https://docs.tricentis.com/tosca-2026.1/en-us/content/mcp/connect_mcp_server.htm>
