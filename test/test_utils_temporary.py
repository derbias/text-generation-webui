import types

from modules.utils import temporary_settings, temporary_attrs


def test_temporary_settings_overwrite_and_restore():
    settings = {"a": 1, "b": 2}

    with temporary_settings(settings, a=10, c=30):
        assert settings["a"] == 10
        assert settings["b"] == 2
        assert settings["c"] == 30

    # restored
    assert settings["a"] == 1
    assert settings["b"] == 2
    assert "c" not in settings


def test_temporary_attrs_overwrite_and_restore():
    ns = types.SimpleNamespace(a=1, b=2)

    with temporary_attrs(ns, a=10, c=30):
        assert ns.a == 10
        assert ns.b == 2
        assert ns.c == 30

    # restored
    assert ns.a == 1
    assert ns.b == 2
    assert not hasattr(ns, "c")

