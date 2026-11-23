"""Non-destructive English sentence segmentation for previously unsegmented text.

Requires pysbd==0.3.4. Existing GROBID sentence units should bypass this helper.
This adapter protects URL/DOI tokens from punctuation-based false boundaries and
repairs common missing spaces after sentence-ending punctuation for segmentation
only. Output consists exclusively of exact slices of the supplied source text.

This is a general rule-based boundary detector, not a guarantee of grammatical
sentences. Ambiguous initials/abbreviations and fragments still require evaluation.
"""
import re
from copy import deepcopy

from pysbd import Segmenter


_LINK = re.compile(r"(?:https?://|www\.)[^\s<>]+|\b(?:doi:\s*)?10\.\d{4,9}/[^\s<>]+", re.I)


def _protected_end(text, start, end):
    """Leave ordinary trailing prose punctuation outside the protected token."""
    while end > start:
        char = text[end - 1]
        if char in '.,;:!?"\'':
            end -= 1
        elif char in ')]}' and text[start:end].count(char) > text[start:end].count({')': '(', ']': '[', '}': '{'}[char]):
            end -= 1
        else:
            break
    return end


def _segmentation_view(text):
    """Return temporary text and a boundary-index map back to the original."""
    masked = list(text)
    for match in _LINK.finditer(text):
        end = _protected_end(text, match.start(), match.end())
        # Same-length masking needs no literal placeholder replacement on output.
        # Only offsets are used, so existing literal 'x' characters cannot collide.
        for index in range(match.start(), end):
            if not masked[index].isspace():
                masked[index] = 'x'

    view = []
    original_boundary = [0]
    for index, char in enumerate(masked):
        view.append(char)
        original_boundary.append(index + 1)
        # PDF extraction can join 'needed.The' or '2015.The'. Do not insert within
        # URLs/DOIs (already masked), decimals, or uppercase initial sequences.
        # PySBD still decides whether an abbreviation such as 'Dr.' ends a sentence.
        if (char in '.!?' and index > 0 and index + 1 < len(masked)
                and (masked[index - 1].islower() or masked[index - 1].isdigit())
                and masked[index + 1].isupper()):
            view.append(' ')
            original_boundary.append(index + 1)
    return ''.join(view), original_boundary


def split_sentences(text):
    """Return [{text, start, end}], with exact source slices and contiguous spans.

    Whitespace is retained in the slices. Nonempty output joins exactly to input.
    Raises ValueError if PySBD omits non-whitespace text, instead of silently
    submitting an unsplit paragraph or dropping text. Whitespace-only input has
    no sentence records. Constructing a segmenter per call avoids sharing PySBD's
    mutable ``original_text`` field between concurrent conversions.
    """
    if not isinstance(text, str):
        raise TypeError('Sentence segmentation input must be a string.')
    if not text.strip():
        return []
    view, boundary_map = _segmentation_view(text)
    spans = Segmenter(language='en', clean=False, char_span=True).segment(view)
    if not spans:
        raise ValueError('Sentence segmentation returned no spans for nonempty text.')

    previous = 0
    ends = []
    for span in spans:
        if not (previous <= span.start < span.end <= len(view)):
            raise ValueError('Sentence segmentation returned invalid or overlapping spans.')
        if view[previous:span.start].strip() or span.sent != view[span.start:span.end]:
            raise ValueError('Sentence segmentation did not cover the source text exactly.')
        previous = span.end
        ends.append(boundary_map[span.end])
    if view[previous:].strip():
        raise ValueError('Sentence segmentation omitted trailing source text.')
    ends[-1] = len(text)  # Include any trailing whitespace with the final unit.

    result = []
    start = 0
    for end in ends:
        if end <= start or not text[start:end].strip():
            raise ValueError('Sentence segmentation produced an empty source-text unit.')
        result.append({'text': text[start:end], 'start': start, 'end': end})
        start = end
    if start != len(text) or ''.join(unit['text'] for unit in result) != text:
        raise ValueError('Sentence segmentation changed or omitted source text.')
    return result


def split_text_unit(unit):
    """Split one recovered text block; preserve original GROBID sentence units.

    Offsets refer to the normalized source block, not PDF positions. The source
    block/coordinates remain available in JSON provenance, but derived sentences
    do not inherit paragraph-sized boxes in the model's coordinates column.
    """
    provenance = unit.get('provenance') or {}
    if provenance.get('segmentation') != 'unsegmented_text':
        return [unit]
    text = unit.get('sentence', '')
    rows = []
    for span in split_sentences(text):
        raw = span['text']
        sentence = raw.strip()
        start = span['start'] + len(raw) - len(raw.lstrip())
        end = span['end'] - (len(raw) - len(raw.rstrip()))
        child = deepcopy(unit)
        child['sentence'] = sentence
        child['coords'] = None
        child['provenance'] = {
            **deepcopy(provenance),
            'source_segmentation': 'unsegmented_text',
            'segmentation': 'pysbd_sentence',
            'sentence_splitter': 'pysbd==0.3.4 (English, with source-offset adapter)',
            'source_text': text,
            'source_text_start': start,
            'source_text_end': end,
            'source_coords': unit.get('coords'),
            'source_coordinate_element': provenance.get('coordinate_source'),
            'coordinate_source': None,
            'coordinate_status': 'unavailable_for_sentence',
        }
        assert text[start:end] == sentence
        rows.append(child)
    return rows
