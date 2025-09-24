import types

import pytest

from modules.loaders import load_via_baseloader
from modules.hardware import suggest_gpu_layers, detect_vram_gb


def test_load_via_baseloader_unknown():
    with pytest.raises(ValueError):
        load_via_baseloader('dummy', 'UnknownLoader')


def test_suggest_gpu_layers_uses_vram(monkeypatch):
    # Force VRAM 12GB
    monkeypatch.setattr('modules.hardware.detect_vram_gb', lambda: 12.0)
    base = 100
    out = suggest_gpu_layers('dummy', base, 8192)
    assert 0 <= out <= base

    # Low VRAM should reduce layers further
    monkeypatch.setattr('modules.hardware.detect_vram_gb', lambda: 4.0)
    out_low = suggest_gpu_layers('dummy', base, 8192)
    assert out_low <= out

