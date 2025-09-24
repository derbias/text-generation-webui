from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Dict, Any

import yaml

from pydantic import BaseModel, Field


class SettingsModel(BaseModel):
    # Minimal subset; expand as needed
    mode: str = Field(default="chat")
    preset: str = Field(default="None")
    character: str = Field(default="None")
    default_extensions: List[str] = Field(default_factory=list)
    prompt_notebook: bool = Field(default=False, alias="prompt-notebook")

    class Config:
        populate_by_name = True


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    return yaml.safe_load(content) or {}


def load_and_validate(settings_file: Optional[Path]) -> Dict[str, Any]:
    raw: Dict[str, Any] = {}
    if settings_file is not None and settings_file.exists():
        raw = _load_yaml(settings_file)

    model = SettingsModel.model_validate(raw)
    normalized: Dict[str, Any] = model.model_dump(by_alias=True)

    # Preserve unknown keys pass-through while normalizing known ones
    for k, v in raw.items():
        if k not in normalized:
            normalized[k] = v

    return normalized


