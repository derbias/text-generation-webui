from modules.loaders import registry


def test_baseloader_registry_minimal():
    assert 'Transformers' in registry
    assert 'llama.cpp' in registry

