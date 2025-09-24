from pathlib import Path
import tempfile

from modules.config import load_and_validate


def test_load_and_validate_defaults_when_missing():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "settings.yaml"
        result = load_and_validate(p)
        assert result.get("mode") == "chat"
        assert result.get("preset") == "None"
        assert result.get("default_extensions") == []


def test_load_and_validate_normalizes_aliases():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "settings.yaml"
        p.write_text("prompt-notebook: true\nmode: instruct\n", encoding="utf-8")
        result = load_and_validate(p)
        # alias preserved
        assert result.get("prompt-notebook") is True
        assert result.get("mode") == "instruct"


