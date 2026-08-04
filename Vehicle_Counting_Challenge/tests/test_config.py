from utils.config import deep_merge, validate_config


def test_deep_merge_overrides_nested_values():
    base = {'a': {'b': 1, 'c': 2}, 'd': 4}
    overrides = {'a': {'b': 99}}
    merged = deep_merge(base, overrides)
    assert merged['a']['b'] == 99
    assert merged['a']['c'] == 2
    assert merged['d'] == 4


def test_validate_config_accepts_valid_payload():
    cfg = {
        'model': {'weights': 'yolo11n.pt'},
        'inference': {'conf': 0.3, 'iou': 0.4},
        'line': {'position_ratio': 0.5},
    }
    validate_config(cfg)
