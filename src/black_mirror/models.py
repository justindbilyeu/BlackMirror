"""Shared enums and dataclasses."""

from enum import Enum
from dataclasses import dataclass


class BreakType(Enum):
    FRACTURE = "fracture"
    ANOMALY = "anomaly"
    SMOOTHING = "smoothing"
    COMPRESSION_SCAR = "compression_scar"


class NodeType(Enum):
    OBSERVATION = "observation"
    HYPOTHESIS = "hypothesis"
    CLAIM = "claim"
    SOURCE = "source"
    MODEL = "model"
    HUMAN = "human"
    ANOMALY = "anomaly"
    LINEAGE = "lineage"


class EdgeType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVES_FROM = "derives_from"
    CONSTRAINS = "constrains"
    SMOOTHED_OVER = "smoothed_over"
    FALSIFIES = "falsifies"


@dataclass
class Scar:
    scar_id: str
    lineage_id: str
    break_type: str
    the_break: str
    the_blade: str
    the_smith: str
    the_nutrient: str
    the_grain: str
    timestamp: str
