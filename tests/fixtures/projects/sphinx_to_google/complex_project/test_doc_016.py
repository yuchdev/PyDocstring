#!/usr/bin/env python3
"""
Graph utilities for the cluster-based narrative layout.

Directory layout (per day):
Days/
  DNN/
    LNXXX/
      DNN-LNXXX-CYYY-PAXXX/         <-- Cluster directory
        cluster.json                <-- meta stub
        DNN-LNXXX-CYYY-PAXXX-a0-<slug>.json
        DNN-LNXXX-CYYY-PAXXX-a4-<slug>.json
        a0-<slug>.md  (TBD)
        a4-<slug>.md  (TBD)

Cluster name format:
  DNN-LNXXX-CYYY-PAXXX
    - DNN   : day number (e.g., D01)
    - LNXXX : lane index zero-based (LN000, LN001, ...)
    - CYYY  : cluster ordinal within lane, left-to-right from 0 (C000, C001, ...)
    - PAXXX : parent cluster ordinal within previous lane (use PA000 at lane 0)

Nodes inside a cluster are addressed as:
  <cluster_full_name>-a<depth>-<slug>.json
  depth: 0..4 (a0 entry, a4 exit gate)

NOTE: Nodes now contain a single "exit" object (not "exits").
      See GRAPH_STRUCT.md §4 for the exit/option schema.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from tools.graph.extract_dialogue import iter_dialogues_from_events

# --------------------------- naming helpers ---------------------------

CLUSTER_DIR_RE = re.compile(r"^(D\d{2})-(LN\d{3})-(C\d{3})-(PA\d{3})$")


def _load_json(p: Path) -> Dict[str, Any]:
    """Read JSON file and return dict.

    :raises ValueError: On invalid JSON or decoding error.
    """
    pass


def _resolve_node_and_cluster(
    node_id_or_path: str | Path, days_root: Optional[Path]
) -> tuple[Path, str, int, Path]:
    """Resolve node JSON path, cluster id, node depth, and cluster dir.

    :param node_id_or_path: Node id like D01-LN000-C000-PA000-a3-slug or a file path.
    :param days_root: Optional Days/ root; auto-discovered if None.
    :returns: Tuple (node_path, cluster_id, depth, cluster_dir)
    :raises FileNotFoundError: If node or cluster cannot be located.
    :raises ValueError: If node id does not contain depth marker.
    """
    pass


def parse_cluster_dir_name(name: str) -> Tuple[str, int, int, int]:
    """
    Parse a cluster directory basename into (day_str, lane_idx, cluster_idx, parent_cluster_idx).

    :raises ValueError if name is invalid.
    """
    pass


def cluster_dir_name(day: int, lane_idx: int, cluster_idx: int, parent_idx: int) -> str:
        pass


def node_file_name(cluster_dir_basename: str, depth: int, slug: str) -> str:
    """Compose a node filename within a cluster.

    :param cluster_dir_basename: Cluster directory basename like `D01-LN003-C004-PA002`.
    :param depth: Node depth within the cluster (0..4, where 0 is entry and 4 is exit/gate).
    :param slug: Human-readable slug for the node, used in file naming.
    :returns: Filename `DNN-LNxxx-Cyyy-PAzzz-a<depth>-<slug>.json`.
    """
    pass


def _a0_stub(cluster_name: str, slug_entry: str) -> Dict[str, Any]:
        pass


def _a3_stub(cluster_name: str, slug_exit: str) -> Dict[str, Any]:
        pass


# --------------------------- cluster & node IO ---------------------------

@dataclass
class ClusterMeta:
    day: int
    lane_idx: int
    cluster_idx: int
    parent_idx: int
    id: str  # repeated full name
    desc: str


class NodeStub:
    id: str
    depth: int  # 0..3
    slug: str
    description: str


def find_days_root(start_in: Optional[Path] = None) -> Path:
    """Locate the `Days/` content root.

    :param start_in: Optional starting directory. If omitted, uses current working directory.
    :returns: Path to the `Days/` directory, either discovered by walking upwards or `<start>/Days` as a fallback.
    """
    pass


def load_cluster_meta(cluster_dir: Path) -> ClusterMeta:
    """Load cluster metadata from a cluster directory.

    Reads `cluster.json` if present to extract a human description.

    :param cluster_dir: Path to a cluster directory `DNN/LNxxx/<cluster_basename>`.
    :returns: `ClusterMeta` with parsed naming components and description.
    :raises ValueError: If the directory name does not match the expected pattern.
    """
    pass


def load_cluster_nodes(cluster_dir: Path) -> List[NodeStub]:
    """Load all node JSONs present in a cluster directory.

    :param cluster_dir: Path to a cluster directory containing `*-a<d>-<slug>.json` files.
    :returns: List of `NodeStub` ordered by `(depth, slug)`.
    """
    pass


# --------------------------- actions ---------------------------

def trace_clusters(cluster_id_or_path: str | Path, days_root: Optional[Path] = None) -> List[ClusterMeta]:
    """
    Trace cluster metas from the selected cluster back to LN000.
    Returns list ordered from selected -> ... -> root.
    """
    pass  # selected -> root order


def trace_nodes(cluster_id_or_path: str | Path, days_root: Optional[Path] = None) -> str:
    """
    Summarize descriptions inside a cluster without enumerating global paths.
    Format:

    Cluster: D01-LN007-C016-PAXXX
    Cluster description: ...
    a0 description: ...
    a1 descriptions:
      - ...
    ...
    a4 descriptions:
      - ...
    a4 branches: A, B
    """
    pass


# --------------------------- generation ---------------------------

def generate_dirs(
        *,
        root: Path,
        day: int,
        lanes: int,
        clusters_per_lane: Optional[List[int]] = None,
        slug_entry: str = "open_doors_confusion",
        slug_exit: str = "branch_gate",
        overwrite: bool = False
) -> List[Path]:
    """
    Create lanes and clusters for a day using the new single-`exit` node structure.

    Default distribution (if clusters_per_lane is None):
      lane i => 2^i clusters (binary fan-out)

    Returns list of created cluster directories.
    """
    pass


def generate_single_cluster(
        *,
        root: Path,
        day: int,
        lane_idx: int,
        cluster_idx: int,
        parent_idx: int,
        slug_entry: str = "open_doors_confusion",
        slug_exit: str = "branch_gate",
        overwrite: bool = False
) -> Path:
    """
    Create exactly one cluster directory with a0/a3 stubs and author pads.
    Returns the created cluster path.
    """
    pass


def _collect_narrative(
    cluster_dir: Path, cluster_id: str, target_depth: int, days_root: Path
) -> tuple[List[Dict[str, Any]], List[Tuple[str, str]], List[str], List[str]]:
    """Collect narrative nodes and dialogues from root to target node.

    :returns: (node_entries, dialogue_pairs, cluster_trail_root_to_target, node_ids_in_order)
    """
    pass
