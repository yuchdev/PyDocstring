from __future__ import annotations
from typing import Any, Dict, List, Mapping, Union
from game.emotions import Emotions


class Character:
    """
    Durable character storage with a dynamic attribute bag and relationship impacts.

    Everything behavioral is in JS; this class only keeps data and ensures that
    a small set of canonical fields mirror into the bag, and vice versa.

    Canonical fields are:
      - name (str)
      - leadership (int 0..100)
      - intelligence (int 0..100)
      - resilience (int 0..100)
      - description (str)
      - friends (list[str])
      - enemies (list[str])

    Additional fields live in `attributes` and are entirely controlled by JS.
    Relationship impacts are stored in `relation_impact` as a mapping
    target-name -> `friendly|neutral|hostile` (values decided by JS).
    """

    CANON_KEYS = {
        "name",
        "leadership",
        "intelligence",
        "resilience",
        "description",
        "friends",
        "enemies",
    }

    def __init__(self, name: str, emotions: Emotions, stats: Mapping[str, Any]):
        """
        Store canonical identity & catalog reference; set canonical defaults (will be overridden by `stats`).
        Store dynamic attribute bag (+ includes canonical keys), and relation impacts.
        Seed bag from canonical defaults, then overlay required stats.
        :param name: Canonical character name.
        :param emotions: Emotion catalog; exposed for UI, not for logic here.
        :param stats: Initial attribute map to overlay (bag-first).
        """
        pass

    def _sync_canon_to_attrs(self):
        """
        Mirror canonical fields into the attribute bag (preserves extra keys).
        """
        pass

    def _sync_attrs_to_canon(self):
        """
        Pull canonical keys from the bag back into typed fields.
        """
        pass

    def update_from_stats(self, stats: Mapping[str, Any]):
        """
        Merge a mapping into the bag, preserving order; then sync canon.
        """
        pass

    def to_stats_dict(self) -> Dict[str, Any]:
        """
        Export a JSON-ready dict of ALL properties (canonical + dynamic).
        """
        pass

    def get_attr(self, key: str, default: Any = None) -> Any:
        """
        Direct bag accessor.
        """
        pass

    def set_attr(self, key: str, value: Any):
        """
        Direct bag setter. If a canonical key is changed, re-sync typed fields.

        :param key: Attribute name.
        :param value: Value to assign.
        """
        pass

    def has_attr(self, key: str) -> bool:
        """
        Return True if the attribute exists in the bag.
        """
        pass

    def del_attr(self, key: str):
        """
        Delete an attribute from the bag. Canonical key deletions will
        re-synchronize canonical defaults back into the bag.
        """
        pass

    def set_emotion(self, emotion: Union[str, object]):
        """
        Set the general/current emotion label decided by JS.
        """
        pass

    def set_relation_impact(self, other_name: str, impact: str):
        """
        Set per-target emotional impact ('friendly'|'neutral'|'hostile').

        :param other_name: Target canonical name.
        :param impact: One of 'friendly', 'neutral', or 'hostile'.
        """
        pass

    def bulk_set_relation_impacts(self, mapping: Mapping[str, str]):
        """
        Overlay multiple per-target impacts.
        """
        pass

    def clear_relation_impacts(self):
        """
        Remove all per-target impacts.
        """
        pass

    def get_aliases(self) -> List[str]:
        """
        Return a list of known aliases for this character (empty if none).
        """
        pass

    def get_friends(self) -> List[str]:
        """
        Return a list of known friends for this character.
        """
        pass

    def get_enemies(self) -> List[str]:
        """
        Return a list of known enemies for this character.
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Return a dict of canonical stats for this character.
        """
        pass

    def as_group_snapshot(self) -> Dict[str, Any]:
        """
        Minimal read-only snapshot used by containers/UI.

        Contains the canonical name, current_emotion, and a shallow copy of the
        per-target relation impacts (as they currently stand).
        """
        pass

    def __repr__(self) -> str:
        """
        Representation for logs and dumps
        """
        pass

    def __str__(self) -> str:
        """
        String representation
        """
        pass

    def __eq__(self, other: object) -> bool:
        """
        Compare characters
        """
        pass

    def __hash__(self) -> int:
        """
        Use characters as dict keys and set items.
        """
        pass
