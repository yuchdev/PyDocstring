"""Voiceover filename construction and parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pipelines.voice.utils.text_normalizer import normalize_text


@dataclass
class VoiceoverNameParts:
    """Decomposed parts of a voiceover filename."""
    index: int
    character_slug: str
    text_slug: str
    duration_ms: int
    hash_suffix: Optional[str] = None


class VoiceoverNamer:
    """Utility responsible for constructing and parsing voiceover filenames.

    New canonical format:

        NNN.character-slug.first-words-slug.duration_ms[.hash].ext

    Example:

        023.romeo-y-cohiba.well-i-m-in-a-room.54243.wav
    """

    _RE = re.compile(
        r"^(?P<idx>\d{3,})\.(?P<char>[^.]+)\.(?P<text>[^.]+)\.(?P<dur>\d+)(?:\.(?P<hash>[0-9a-f]{6}))?\.(?P<ext>wav|ogg)$",
        re.IGNORECASE,
    )

    @staticmethod
    def slugify(s: str) -> str:
        """Normalize an arbitrary string into a lowercase hyphenated slug.

        :param s: Source string to slugify.
        :type s: str
        :returns: Slug with only `a-z0-9` and single hyphens.
        :rtype: str
        """
        pass

    def slugify_first_words(self, text: str, max_words: int = 5) -> str:
        """Create a slug from the first `max_words` tokens of `text`.

        :param text: Source phrase to shorten and slugify.
        :type text: str
        :param max_words: How many words to keep from the beginning.
        :type max_words: int
        :returns: Hyphenated slug of up to `max_words` words.
        """
        pass

    def make_name(
        self,
        idx: int,
        character: str,
        text: str,
        duration_ms: int,
        ext: str,
        hash_suffix: Optional[str] = None,
    ) -> str:
        """Construct a canonical voiceover filename.

        :param idx: 1-based index of the line in the script.
        :type idx: int
        :param character: Speaking character's display name.
        :type character: str
        :param text: Dialogue text to derive a short slug from.
        :type text: str
        :param duration_ms: Audio duration in milliseconds.
        :type duration_ms: int
        :param ext: File extension, with or without leading dot.
        :type ext: str
        :param hash_suffix: Optional short hash to disambiguate variants.
        :type hash_suffix: Optional[str]
        :returns: Canonical filename like `023.romeo-y-cohiba.hello.54243.wav`.
        :rtype: str
        """
        pass

    def parse(self, name: str | Path) -> Optional[VoiceoverNameParts]:
        """Parse a canonical filename into its constituent parts.

        :param name: Filename or full path to parse.
        :type name: str | pathlib.Path
        :returns: Decomposed parts when the pattern matches, otherwise `None`.
        :rtype: Optional[VoiceoverNameParts]
        """
        pass


def slugify_line(line: str, slug_length: int = 5, slugify_spaces: bool = True) -> str:
    """Produce a short slug from the beginning of a dialogue line.

    Uses the same normalization and tokenization rules as voiceover filenames.

    :param line: Original dialogue text line.
    :type line: str
    :param slug_length: Number of words to keep from the beginning.
    :type slug_length: int
    :param slugify_spaces: If True, return hyphen-separated slug; if False,
        return a space-separated phrase. In both cases, if the source line
        contains more words than `slug_length`, an ellipsis ("...") is
        appended.
    :type slugify_spaces: bool
    :returns: A shortened slug or phrase derived from `line`.
    :rtype: str
    """
    pass
