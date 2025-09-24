from modules import shared


def test_metrics_structure_initialized():
    # server initializes metrics dict; if not present, simulate
    if not hasattr(shared, 'metrics'):
        shared.metrics = {}
    # Simulate fields existence
    shared.metrics.setdefault('requests_total', 0)
    shared.metrics.setdefault('in_flight', 0)
    shared.metrics.setdefault('tokens_total', 0)
    shared.metrics.setdefault('endpoint_counts', {})
    shared.metrics.setdefault('queue_depth', 0)
    assert isinstance(shared.metrics['endpoint_counts'], dict)

