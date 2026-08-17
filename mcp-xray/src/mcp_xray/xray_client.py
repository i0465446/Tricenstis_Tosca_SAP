"""Cliente para la API REST v2 y GraphQL de Xray Cloud.

Xray Cloud se autentica con un Client ID/Secret (generado en Jira: Global
Settings > Apps > Xray API Keys) contra /authenticate, que devuelve un JWT
válido durante horas. Este cliente cachea el token y lo renueva con margen.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

import httpx

AUTH_URL = "https://xray.cloud.getxray.app/api/v2/authenticate"
IMPORT_JUNIT_URL = "https://xray.cloud.getxray.app/api/v2/import/execution/junit"
IMPORT_EXECUTION_URL = "https://xray.cloud.getxray.app/api/v2/import/execution"
GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"

REQUIRED_ENV_VARS = ("XRAY_CLIENT_ID", "XRAY_CLIENT_SECRET")

# El token de Xray Cloud dura ~24h; renovamos con bastante margen para no
# arriesgarnos a que caduque a mitad de una llamada larga.
_TOKEN_TTL_SECONDS = 60 * 55


@dataclass
class XrayConfig:
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> "XrayConfig":
        missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
        if missing:
            raise RuntimeError(
                "Faltan variables de entorno para conectar con Xray: "
                + ", ".join(missing)
                + ". Revisa mcp-xray/.env.example."
            )
        return cls(
            client_id=os.environ["XRAY_CLIENT_ID"],
            client_secret=os.environ["XRAY_CLIENT_SECRET"],
        )


class XrayClient:
    def __init__(self, config: XrayConfig):
        self._config = config
        self._token: str | None = None
        self._token_fetched_at: float = 0.0

    def _token_valid(self) -> bool:
        return self._token is not None and (time.monotonic() - self._token_fetched_at) < _TOKEN_TTL_SECONDS

    def _authenticate(self) -> str:
        response = httpx.post(
            AUTH_URL,
            json={"client_id": self._config.client_id, "client_secret": self._config.client_secret},
            timeout=30,
        )
        response.raise_for_status()
        token = response.json()
        self._token = token.strip('"') if isinstance(token, str) else token
        self._token_fetched_at = time.monotonic()
        return self._token

    def _headers(self) -> dict:
        token = self._token if self._token_valid() else self._authenticate()
        return {"Authorization": f"Bearer {token}"}

    def import_execution_junit(
        self,
        project_key: str,
        junit_xml: str,
        test_exec_key: str | None = None,
    ) -> dict:
        params = {"projectKey": project_key}
        if test_exec_key:
            params["testExecKey"] = test_exec_key
        response = httpx.post(
            IMPORT_JUNIT_URL,
            params=params,
            headers={**self._headers(), "Content-Type": "text/xml"},
            content=junit_xml.encode("utf-8"),
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def import_execution_json(self, execution: dict) -> dict:
        response = httpx.post(
            IMPORT_EXECUTION_URL,
            headers={**self._headers(), "Content-Type": "application/json"},
            json=execution,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def graphql(self, query: str, variables: dict) -> dict:
        response = httpx.post(
            GRAPHQL_URL,
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"query": query, "variables": variables},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise RuntimeError(f"Xray GraphQL error: {payload['errors']}")
        return payload["data"]
