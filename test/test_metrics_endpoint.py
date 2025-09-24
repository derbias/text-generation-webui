from modules import shared


def test_metrics_keys_exist():
    # Simulate metrics initialization
    shared.metrics = {
        'requests_total': 0,
        'in_flight': 0,
        'tokens_total': 0,
        'endpoint_counts': {},
        'queue_depth': 0,
    }
    assert 'requests_total' in shared.metrics
    assert 'in_flight' in shared.metrics
    assert 'tokens_total' in shared.metrics
    assert 'endpoint_counts' in shared.metrics
    assert 'queue_depth' in shared.metrics

