#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
play_stats.py - Comprehensive statistics for a chat/play script.

Primary format (recommended): JSON events list or stream of dicts (can come from DB, stdin, or file)
Event examples:
  { "character": "Organizm(-:", "event_type": "enter" }
  { "character": "Organizm(-:", "to": "", "mood": "confused", "text": "What's going on?", "event_type": "dialogue" }
  { "character": "Organizm(-:", "event_type": "leave" }   # optional
  { "event_type": "day_start" }                            # starts a new day segment (JSON only)

Also supported:
- JSON array of bracketed strings: ["[Character] Text", ...]
- Plain .txt/.md inputs with lines like: "[Character][To whom][Mood] Text"
  - Optional explicit day markers: a line exactly like "Day NN" (case-insensitive) sets the current day to DNN.
  - In .md, keep ONE empty line between dialogue lines (blank lines are ignored).
  - In .txt, each dialogue occupies a single line.
- Legacy "interactions" JSON: list-of-lists of bracketed lines "[Character] text", or dicts with 'events' list.

Day semantics:
- If you see only a single day label (e.g., D00) in the output, it means all content was treated as one day.
- JSON: each {"event_type":"day_start"} increments the current day (D00 -> D01 -> D02 ...).
- TXT/MD: a line "Day NN" switches to DNN for subsequent dialogue lines. If no markers are present, fall back to --split-day.

What it computes:
1) Line size distributions (characters & words):
   - overall & per character: count, mean, median, std, min, max, deciles (0..100 step 10)
2) Number of messages per character: overall and per day
3) Richness metrics (overall & per character):
   - TTR (type-token ratio), MATTR (window=50), Hapax ratio, Yule's K
   - Avg. sentence length (in tokens), punctuation rate
4) "Concurrency" / presence:
   - Active-speaker set size per dialogue step (distribution/mean/max)
   - Join/leave events overall/per character (explicit enter/leave respected; heuristic leave-gap as fallback)
5) Rotation & distribution:
   - Speaker switch rate and average streak length (overall & per day)
   - Per-character share of lines (proportions)
6) Optional comparison to a reference metrics JSON with tolerances
7) Two-source mode: compute stats for A and B from inputs and compare directly (no saved reference needed).

Outputs:
- JSON summary (nested) + optional CSVs:
  - lines.csv
  - per_day_character_counts.csv
  - concurrency.csv
  - concurrency_steps.csv
  - join_events.csv
  - leave_events.csv
  - join_leave.csv (aggregates per-character and per-day totals)

Programmatic API:
- compute_stats_from_events(events: list[dict], *, aliases=None, split_day="none", day_label="D00", leave_gap=40)
  -> summary_dict
This lets you feed DB-fetched event dicts directly without saving files.

CLI usage examples:
  # Two-source compare (A vs B) from raw inputs
  python3 play_stats.py --input-a a_dir/*.json --input-b b_dir/*.json --compare-type bag --export-json out/compare.json

  # Compare using sequence-sensitive profile
  python3 play_stats.py --json-stdin --reference baseline/summary.json --thresholds baseline/thresholds.json --compare-type sequence

  # Compare using order-agnostic (bag) profile
  python3 play_stats.py --json-stdin --reference baseline/summary.json --thresholds baseline/thresholds.json --compare-type bag

CLI usage examples:
  python3 play_stats.py --json-stdin --export-json out/summary.json
  python3 play_stats.py --json-inline '{"events":[{"event_type":"dialogue","character":"A","text":"Hi"}]}'

  python3 play_stats.py --input data/*.md data/*.json \
    --split-day auto \
    --export-json out/summary.json --export-csv-dir out

  # Compare to baseline
  python3 play_stats.py --json-stdin \
    --reference baseline/summary.json --thresholds baseline/thresholds.json \
    --export-json out/summary.json

Author: ChatGPT (GPT-5 Thinking)

Console output now also prints a colored diff of compared metrics (red = outside tolerances).
"""
from __future__ import annotations
import argparse
import csv
import dataclasses
import glob
import json
import math
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from json import JSONDecodeError
from typing import Dict, List, Tuple, Iterable, Any, Optional

# Import dialogue helpers from graph module
from pipelines.graph.extract_dialogue import (
    normalize_name,
    apply_alias,
    extract_from_payload,
)

# Use canonical aliases from local _characters.py
try:
    from game.constants import ALIASES  # deprecated; retained for back-compat if file exists
except Exception:
    try:
        from game.adapters.api.factory import Config, make_content_api  # type: ignore
        ALIASES = make_content_api(Config.from_env()).get_aliases()  # type: ignore
    except Exception:
        ALIASES = {}


def ensure_dir(path: str | os.PathLike):
    """Ensure a directory exists (mkdir -p).

    Provided for compatibility with tests that import tools.play_stats.ensure_dir.
    """
    pass


# Rich bracket line: [Character][To][Mood] Text
BRACKET_RICH_RE = re.compile(
    r'^\s*\[(?P<char>[^\[\]]+?)]\s*'
    r'(?:\[(?P<to>[^\[\]]*?)]\s*)?'
    r'(?:\[(?P<mood>[^\[\]]*?)]\s*)?'
    r'(?P<text>.*\S)\s*$'
)

# Legacy simple bracket line: [Character] Text
BRACKET_SIMPLE_RE = re.compile(r'^\s*\[(?P<char>[^\[\]]+?)]\s*(?P<text>.*\S)\s*$')

# Lines made only of these symbols are chapter separators
CHAPTER_SEP_RE = re.compile(r'^[\s:;\-()]+$')

# Day marker in txt/md: "Day NN"
DAY_MARKER_RE = re.compile(r'^\s*day\s+(\d{1,3})\s*$', re.IGNORECASE)

WORD_RE = re.compile(r'\b\w+\b', re.UNICODE)


def iter_marked_items(lines: Iterable[str]) -> Iterable[Tuple[str, Any]]:
    """
    Yield normalized items from a sequence of raw lines:
    - ('day', 'DNN') when a day marker like "Day 3" is encountered
    - ('dialogue', matchobj) when a bracketed dialogue line is matched (rich or simple)
    Skips blank lines and non-matching content.
    """
    pass


def iter_lines_from_text_rich(text_body: str) -> Iterable[Tuple[str, str, str, str]]:
    """
    Iterate over rich bracket-formatted lines in plaintext/markdown.

    Accepts lines:
    - [Character][To][Mood] Text
    - [Character] Text (legacy simplified)
    """
    pass


def iter_dialogues_from_events(payload: Any) -> Iterable[Tuple[str, str, str, str, str]]:
    """
    Iterate event-like structures and yield normalized dialogue tuples.

    Supports multiple JSON shapes:
    - list[dict]: items with event_type in {"dialogue","enter","leave","day_start"}
    - dict with key 'events' (or legacy 'dialogues'/'lines') containing an events list
    - legacy list[list[str]] or list[str] with bracketed lines
    - NEW: list[str] of bracketed lines ["[Character] Text", ...]
    """
    pass


def infer_day_from_path(path: str) -> Optional[str]:
    """
    Infer a day label (e.g., "D01") from a file path or name.
    Accepts single-digit forms like "D3" and normalizes to "D03".
    """
    pass


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into lowercase word tokens using a simple regex.
    """
    pass


def sentences(text: str) -> List[str]:
    """
    Split text into sentences using punctuation heuristics.
    """
    pass


def richness_metrics(tokens: List[str]) -> Dict[str, float]:
    """
    Compute lexical richness metrics: TTR, MATTR(50), Hapax ratio, Yule's K.
    """
    pass


def punctuation_rate(texts: List[str]) -> float:
    """
    Fraction of punctuation characters across given texts.
    """
    pass


def sentence_length_metrics(texts: List[str]) -> Dict[str, float]:
    """
    Basic sentence length statistics (in tokens).
    """
    pass


def deciles(values: List[float]) -> Dict[str, float]:
    """
    Compute deciles p0..p100 for a numeric vector using linear interpolation.
    """
    pass


@dataclasses.dataclass
class LineRec:
    """
    One dialogue line record with annotations and lengths.
    """
    file: str
    day: str
    index: int
    character: str
    alias: Optional[str]
    to: str
    mood: str
    text: str
    char_len: int
    word_len: int


def parse_file_text(path: str, aliases: Dict[str, str], split_day: str, fixed_day: Optional[str]) -> List[LineRec]:
    """
    Parse a .txt/.md file into LineRec objects.
    Recognizes "Day NN" markers (case-insensitive). If none is present, it falls back to the split_day heuristic.
    """
    pass


def parse_file_json(path: str, aliases: Dict[str, str], split_day: str, fixed_day: Optional[str]) -> Tuple[List[LineRec], List[dict]]:
    """
    Parse a JSON file containing events or legacy structures into records and events (supports 'day_start' and bracket arrays).
    """
    pass


def records_from_json_obj(payload, source_name, aliases, split_day, fixed_day) -> Tuple[List[LineRec], List[dict]]:
    """
    Convert JSON-like object into LineRec records and raw events. Honors 'day_start' events if present.
    """
    pass


def collect_from_sources(file_paths, json_values, text_values, aliases, split_day, day_label) -> Tuple:
    """
    Collect LineRec records and events from files, in-memory JSON, and text inputs.
    """
    pass


def parse_source(aliases: dict, all_events: list, all_records: list, day_label: str, file_path: str, filename: str, split_day: str):
    """
    Parses a source file, either in JSON format or text/markdown format, and extracts event and record
    data, updating the provided lists with new content based on the parsing results.

    The function identifies the correct format of the file based on its extension. Depending on the
    format, it processes the file and appends the parsed records to the `all_records` list and the parsed
    events to the `all_events` list.

    :param aliases: A dictionary mapping alias names to their respective full names or related data.
    :param all_events: A list where new events extracted from the file will be appended.
    :param all_records: A list where new records extracted from the file will be appended.
    :param day_label: A string representation of the day label used during parsing
    :param file_path: The filepath of the source file being parsed.
    :param filename: The name of the file, used to determine the file format (e.g., `.json`, `.txt`, `.md`).
    :param split_day: A string value that used to determine or split records/events based on a specific day or timeframe during parsing.
    """
    pass


def parse_text_inline(text_body: str, aliases: Dict[str,str], fixed_day: Optional[str]) -> List[LineRec]:
    """
    Parse inline text/markdown using explicit 'Day NN' markers when present.
    """
    pass


def parse_line(aliases: dict, m) -> tuple:
    """
    Parses a provided line of text matching a specific pattern and extracts relevant
    elements such as speaker, recipient, mood, text, and their normalized or aliased forms.

    This function normalizes the name of the speaker, extracts the recipient (if available),
    mood (if available), and primary text content. It also determines if an alias was used
    for the speaker's name and the canonical (standardized) name for the speaker.

    :param aliases: A dictionary mapping aliases to their canonical names
    :param m: A match object resulting from parsing text
    :return: A tuple containing the alias used (if any), the canonical speaker name,
        the mood of the speaker (if specified), the text content, and the recipient
        (if specified).
    """
    pass


def basic_stats(values: List[float]) -> Dict[str, float]:
    """
    Compute basic descriptive statistics for a numeric vector.
    """
    pass


def aggregate(all_records: List[LineRec], all_events: List[dict], leave_gap: int = 40) -> Tuple[Dict[str, Any], List[Tuple[str, int, int]], List[Tuple[str, str, int]], List[Tuple[str, str, int]]]:
    """
    Aggregate into a summary metrics dictionary.
    Returns (summary, concurrency_rows, join_events, leave_events).
    """
    pass


def compare_to_reference(current: Dict[str, Any], reference: Dict[str, Any], thresholds: Dict[str, Any], compare_type: str = "sequence") -> Dict[str, Any]:
    """
    Compare a current metrics dict to a reference dict using tolerances.

    Modes:
      - "sequence": compare *all* numeric metrics, including order/sequence-sensitive ones
        (concurrency, join/leave, rotation, per_day, etc.).
      - "bag": compare only order-insensitive metrics suitable for aggregated text: overall line lengths,
        richness, punctuation, sentence lengths, and distributions.per_character_share.*.
        Keys under concurrency.*, join_leave.*, per_day.*, rotation.* are ignored.
    """
    pass


def write_csvs(out_dir: str, all_records: List[LineRec], summary: Dict[str, Any], concurrency_rows: List[Tuple[str, int, int]], join_events: List[Tuple[str, str, int]], leave_events: List[Tuple[str, str, int]]):
    """
    Write detailed CSV exports for deeper analysis.
    """
    pass


def compute_stats_from_events(events, *, aliases = None, split_day = "none", day_label = "D00", leave_gap: int = 40) -> dict:
    """
    Feed DB-fetched events directly (list of dicts). Returns the summary dict.
    If events include {"event_type":"day_start"}, those day boundaries are honored.
    """
    pass


def main():
    """
    :return: system exit code
    """
    pass


if __name__ == "__main__":
    sys.exit(main())
