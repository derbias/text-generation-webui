import importlib


def test_import_server_and_build_interface_without_model():
    # This ensures imports succeed and create_interface is present
    server = importlib.import_module('server')
    assert hasattr(server, 'create_interface')

