"""Standard-library SD2 CLIP tokenizer and Nuke prompt callback.

Uses NFC normalization, not ftfy: corrupted encoding, HTML entities, typography
and other ftfy repairs are deliberately not reproduced. Assets live beside this
file. No Nuke graph construction or model packaging is performed here.
"""
import json
from pathlib import Path
import re
import unicodedata

DATA = Path(__file__).resolve().parent


def category(char):
    if char in '\t\n\v\f\r \x85\xa0\u1680\u2028\u2029\u202f\u205f\u3000' or '\u2000' <= char <= '\u200a':
        return 3
    kind = unicodedata.category(char)
    # The reference's case-insensitive negated class excludes U+0345, while
    # its positive letter class does not consume it; preserve that omission.
    if char == '\u0345':
        return 0
    return 1 if kind.startswith('L') else 2 if kind.startswith('N') else 4


def pieces(text):
    text = unicodedata.normalize('NFC', text)
    text = ''.join(' ' if category(c) == 3 else c for c in text).strip().lower()
    i = 0
    while i < len(text):
        kind = category(text[i])
        if kind in (0, 3):
            i += 1
            continue
        match = next((s for s in ("'s", "'t", "'re", "'ve", "'m", "'ll", "'d")
                      if text.startswith(s, i)), None)
        if match:
            yield match
            i += len(match)
            continue
        end = i + 1
        if kind != 2:
            while end < len(text) and category(text[end]) == kind:
                end += 1
        yield text[i:end]
        i = end


class Tokenizer:
    def __init__(self, directory=DATA):
        directory = Path(directory)
        self.vocab = json.loads((directory / 'vocab.json').read_text(encoding='utf-8'))
        merges = (directory / 'merges.txt').read_text(encoding='utf-8').strip().splitlines()[1:48895]
        self.ranks = {tuple(line.split()): i for i, line in enumerate(merges)}
        base = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
        extra = [b for b in range(256) if b not in base]
        self.byte_map = dict(zip(base + extra, map(chr, base + list(range(256, 256 + len(extra))))))
        self.cache = {}

    def bpe(self, token):
        if token in self.cache:
            return self.cache[token]
        word = list(token[:-1]) + [token[-1] + '</w>']
        while len(word) > 1:
            pairs = list(zip(word, word[1:]))
            pair = min(pairs, key=lambda p: self.ranks.get(p, float('inf')))
            if pair not in self.ranks:
                break
            merged, i = [], 0
            while i < len(word):
                if i + 1 < len(word) and (word[i], word[i + 1]) == pair:
                    merged.append(word[i] + word[i + 1])
                    i += 2
                else:
                    merged.append(word[i])
                    i += 1
            word = merged
        result = [self.vocab[p] for p in word]
        if len(self.cache) >= 8192:
            self.cache.clear()
        self.cache[token] = result
        return result

    def encode(self, text):
        if not isinstance(text, str):
            raise TypeError('Prompt must be a string')
        if len(text) > 32768:
            raise ValueError('Prompt exceeds the 32768-character safety limit')
        for char in text:
            if unicodedata.category(char) in ('Cn', 'Cs'):
                raise ValueError('Unsupported Unicode character U+%04X in this Python runtime' % ord(char))
        tokens = []
        for part in re.split(r'(<\|startoftext\|>|<\|endoftext\|>|!)', text):
            if part in ('<|startoftext|>', '<|endoftext|>', '!'):
                tokens.append(self.vocab[part])
            else:
                for piece in pieces(part):
                    tokens.extend(self.bpe(''.join(self.byte_map[b] for b in piece.encode('utf-8'))))
        ids = [49406] + tokens[:75] + [49407]
        return {'input_ids': ids + [0] * (77 - len(ids)),
                'content_tokens': len(tokens), 'truncated': len(tokens) > 75}


def update_group(group):
    """Update existing prompt knobs; does not create nodes or import Nuke."""
    prompt = group['prompt'].value()
    result = Tokenizer().encode(prompt)
    knob = group['id_lut']
    knob.clearAnimated()
    knob.setAnimated()
    for i, value in enumerate(result['input_ids']):
        knob.setValueAt(value, i)
    group['encoded_prompt'].setValue(prompt)
    group['status'].setValue('Encoded %d content tokens%s' % (
        result['content_tokens'], ' — TRUNCATED to 75' if result['truncated'] else ''))
    return result