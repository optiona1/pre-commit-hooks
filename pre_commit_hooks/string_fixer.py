from __future__ import annotations

import argparse
import io
import re
import tokenize
from typing import Sequence


def handle_match(token_text: str, is_double_quote: bool, start_quote_re: re.Pattern) -> str:
    if '"""' in token_text or "'''" in token_text:
        return token_text

    match = start_quote_re.match(token_text)
    if match is not None:
        meat = token_text[match.end():-1]
        if '"' in meat or "'" in meat:
            return token_text
        else:
            if is_double_quote:
                return match.group().replace("'", '"') + meat + '"'
            else:
                return match.group().replace('"', "'") + meat + "'"
    else:
        return token_text


def get_line_offsets_by_line_no(src: str) -> list[int]:
    # Padded so we can index with line number
    offsets = [-1, 0]
    for line in src.splitlines(True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def fix_strings(filename: str, is_double_quote: bool) -> int:
    with open(filename, encoding='UTF-8', newline='') as f:
        contents = f.read()
    line_offsets = get_line_offsets_by_line_no(contents)

    # Basically a mutable string
    splitcontents = list(contents)

    # Iterate in reverse so the offsets are always correct
    tokens_l = list(tokenize.generate_tokens(io.StringIO(contents).readline))
    tokens = reversed(tokens_l)

    if is_double_quote:
        start_quote_re = re.compile("^[a-zA-Z]*'")
    else:
        start_quote_re = re.compile('^[a-zA-Z]*"')

    for token_type, token_text, (srow, scol), (erow, ecol), _ in tokens:
        if token_type == tokenize.STRING:
            new_text = handle_match(token_text, is_double_quote, start_quote_re)
            splitcontents[
                line_offsets[srow] + scol:
                line_offsets[erow] + ecol
            ] = new_text

    new_contents = ''.join(splitcontents)
    if contents != new_contents:
        with open(filename, 'w', encoding='UTF-8', newline='') as f:
            f.write(new_contents)
        return 1
    else:
        return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    parser.add_argument(
        '--double-quote', action='store_true',
        help='Replaces single quoted strings with double quoted strings.',
    )
    args = parser.parse_args(argv)

    retv = 0

    for filename in args.filenames:
        return_value = fix_strings(filename, args.double_quote)
        if return_value != 0:
            print(f'Fixing strings in {filename}')
        retv |= return_value

    return retv


if __name__ == '__main__':
    raise SystemExit(main())
