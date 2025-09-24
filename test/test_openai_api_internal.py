import os
import json
import socket
import urllib.request
import urllib.error
import pytest

API_BASE = os.environ.get("OPENEDAI_TEST_BASE", "http://127.0.0.1:5006")


def _reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.mark.skipif(not _reachable(f"{API_BASE}/v1/internal/health"), reason="OpenAI API not running")
class TestInternalEndpoints:
    def _get(self, path: str):
        with urllib.request.urlopen(f"{API_BASE}{path}", timeout=2) as resp:
            assert resp.status == 200
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{API_BASE}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            assert resp.status == 200
            return json.loads(resp.read().decode("utf-8"))

    def test_health(self):
        data = self._get("/v1/internal/health")
        assert data.get("status") == "ok"

    def test_api_keys_configured_and_validate(self):
        info = self._get("/v1/internal/api-keys")
        assert "configured" in info
        assert set(info["configured"].keys()) == {"api_key", "admin_key"}
        # validation should always return boolean
        out = self._post("/v1/internal/api-keys/validate", {"type": "api", "key": "invalid"})
        assert isinstance(out.get("valid"), bool)
