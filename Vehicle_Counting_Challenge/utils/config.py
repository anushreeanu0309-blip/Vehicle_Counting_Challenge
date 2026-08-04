from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from utils.exceptions import ConfigurationError


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigurationError(f'Configuration at {path} must be a mapping.')
    return data


def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: str | Path = 'config/default.yaml', overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = load_yaml(config_path)
    if overrides:
        cfg = deep_merge(cfg, overrides)
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict[str, Any]) -> None:
    required = [('model', 'weights'), ('inference', 'conf'), ('line', 'position_ratio')]
    for section, key in required:
        if section not in cfg or key not in cfg[section]:
            raise ConfigurationError(f'Missing configuration key: {section}.{key}')

    conf = float(cfg['inference']['conf'])
    iou = float(cfg['inference']['iou'])
    line_ratio = float(cfg['line']['position_ratio'])

    if not 0.0 <= conf <= 1.0:
        raise ConfigurationError('inference.conf must be between 0 and 1')
    if not 0.0 <= iou <= 1.0:
        raise ConfigurationError('inference.iou must be between 0 and 1')
    if not 0.0 < line_ratio < 1.0:
        raise ConfigurationError('line.position_ratio must be between 0 and 1')
