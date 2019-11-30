# abandon.__main__

import argparse
import itertools
import sys
from   datetime import datetime, timedelta, timezone
from   typing   import BinaryIO, Dict, List, Tuple

from abandon import abandon, Bucket, Items

def split_item(line: bytes) -> Tuple[datetime, bytes]:
    timestamp_str, data = line.split(maxsplit=1)
    timestamp = datetime.fromtimestamp(float(timestamp_str), tz=timezone.utc)
    return timestamp, data

def parse_items(infile: BinaryIO) -> Items:
    result: Items = {}
    for line in infile:
        key, value = split_item(line)
        if key in result:
            raise RuntimeError(f'Duplicate item: {key}')
        result[key] = value
    return result

def parse_duration(duration_spec: str) -> timedelta:
    duration = int(duration_spec[:-1])
    unit     = duration_spec[-1]
    if unit == 'y':
        return timedelta(days=365 * duration)
    if unit == 'm':
        return timedelta(days=30 * duration)
    if unit == 'd':
        return timedelta(days=duration)
    if unit == 'h':
        return timedelta(hours=duration)
    raise RuntimeError('Unknown unit: ' + unit)

def parse_bucket(bucket_spec: str) -> List[Bucket]:
    num_str, duration_spec = bucket_spec.split('@')
    num = int(num_str)
    if num <= 0:
        raise RuntimeError(f'Number of buckets ({num_str}) must be positive')
    return num * [(duration_spec, parse_duration(duration_spec))]

def parse_buckets(bucket_specs: List[str]) -> List[Bucket]:
    result = []
    for buckets in [parse_bucket(spec) for spec in bucket_specs]:
        result.extend(buckets)
    return result

def parse_args() -> Tuple[bool, List[Bucket]]:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('buckets', nargs='*')
    args = parser.parse_args()
    return args.verbose, parse_buckets(args.buckets)

def main() -> None:
    verbose, buckets = parse_args()
    items            = parse_items(sys.stdin.buffer)

    for decision in abandon(buckets, items):
        if not verbose:
            if decision.abandon:
                sys.stdout.buffer.write(decision.item)
        else:
            if not decision.abandon:
                assert(decision.bucket is not None)
                sys.stdout.buffer.write(str(decision.bucket[0]).encode('ascii'))
            else:
                sys.stdout.buffer.write(b' ')
            sys.stdout.buffer.write(b'\t')
            sys.stdout.buffer.write(str(decision.time).encode('ascii'))
            sys.stdout.buffer.write(b'\t')
            sys.stdout.buffer.write(decision.item)

if __name__ == '__main__':
    main()

