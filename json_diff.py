"""Offline structural JSON comparison. Values are never included in reports."""
import argparse
from decimal import Decimal
import itertools
import json
from pathlib import Path

VERSION = '0.2.0'
MAX_BYTES = 16 * 1024 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate object key')
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError('Nonstandard JSON number')


def load(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Input too large')
    return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object,
                      parse_float=Decimal, parse_constant=reject_constant)


def kind(value):
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, (int, Decimal)):
        return 'number'
    return type(value).__name__


def pointer(path, part):
    return path + '/' + str(part).replace('~', '~0').replace('/', '~1')


def walk(left, right, path=''):
    if kind(left) != kind(right):
        yield {'type': 'type_changed', 'path': path}
    elif isinstance(left, dict):
        for key in sorted(left.keys() | right.keys()):
            child = pointer(path, key)
            if key not in left:
                yield {'type': 'added', 'path': child}
            elif key not in right:
                yield {'type': 'removed', 'path': child}
            else:
                yield from walk(left[key], right[key], child)
    elif isinstance(left, list):
        for index in range(max(len(left), len(right))):
            child = pointer(path, index)
            if index >= len(left):
                yield {'type': 'added', 'path': child}
            elif index >= len(right):
                yield {'type': 'removed', 'path': child}
            else:
                yield from walk(left[index], right[index], child)
    elif left != right:
        yield {'type': 'value_changed', 'path': path}


def compare(left, right, show_paths=False, max_changes=1000):
    if max_changes < 1:
        raise ValueError('max_changes must be positive')
    changes = list(itertools.islice(walk(left, right), max_changes + 1))
    truncated = len(changes) > max_changes
    changes = changes[:max_changes]
    counts = {name: 0 for name in ('added', 'removed', 'type_changed', 'value_changed')}
    for change in changes:
        counts[change['type']] += 1
    report = {'equal': not changes, 'recorded_changes': len(changes),
              'truncated': truncated, 'counts': counts}
    if show_paths:
        report['changes'] = changes
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compare JSON without printing values')
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('--show-paths', action='store_true', help='Include JSON Pointer paths; keys may contain private data')
    parser.add_argument('--max-changes', type=int, default=1000)
    parser.add_argument('--quiet', action='store_true', help='Use exit status only')
    parser.add_argument('left')
    parser.add_argument('right')
    args = parser.parse_args(argv)
    if args.max_changes < 1:
        parser.error('--max-changes must be positive')
    try:
        result = compare(load(args.left), load(args.right), args.show_paths, args.max_changes)
    except (ValueError, OSError, RecursionError):
        parser.exit(2, 'Cannot compare input. Use valid UTF-8 JSON up to 16 MiB per file.\n')
    if not args.quiet:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result['equal'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
