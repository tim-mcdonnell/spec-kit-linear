# ABOUTME: HTTP client for Linear GraphQL API with token authentication
# Handles all API communication and response parsing

import os
import json
import httpx
from typing import Any, Optional

from .types import LinearConfig


class LinearClientError(Exception):
    """Raised when Linear API returns an error."""

    def __init__(self, message: str, errors: Optional[list[dict]] = None):
        super().__init__(message)
        self.errors = errors or []


class LinearClient:
    """HTTP client for Linear GraphQL API."""

    API_URL = "https://api.linear.app/graphql"

    def __init__(
        self,
        token: Optional[str] = None,
        config: Optional[LinearConfig] = None,
        config_path: Optional[str] = None,
    ):
        """
        Initialize Linear client.

        Args:
            token: Linear API token. If not provided, reads from LINEAR_TOKEN env var.
            config: LinearConfig object with team/label/state IDs.
            config_path: Path to linear-config.json file.
        """
        self.token = token or os.environ.get("LINEAR_TOKEN")
        if not self.token:
            raise LinearClientError(
                "LINEAR_TOKEN environment variable not set. "
                "Get your token from Linear Settings > API > Personal API keys."
            )

        self._config = config
        self._config_path = config_path

        self._http = httpx.Client(
            headers={
                "Authorization": self.token,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    @property
    def config(self) -> Optional[LinearConfig]:
        """Get configuration, loading from file if needed."""
        if self._config is None and self._config_path:
            self._config = self._load_config(self._config_path)
        return self._config

    def _load_config(self, path: str) -> LinearConfig:
        """Load configuration from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return LinearConfig.from_dict(data)

    def execute(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Execute a GraphQL query or mutation.

        Args:
            query: GraphQL query string.
            variables: Query variables.

        Returns:
            Response data dictionary.

        Raises:
            LinearClientError: If the API returns errors.
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = self._http.post(self.API_URL, json=payload)
        response.raise_for_status()

        result = response.json()

        if "errors" in result:
            error_messages = [e.get("message", str(e)) for e in result["errors"]]
            raise LinearClientError(
                f"Linear API error: {'; '.join(error_messages)}",
                errors=result["errors"],
            )

        return result.get("data", {})

    def close(self):
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
