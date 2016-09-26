# abandon.__main__

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
    return num * [parse_duration(duration_spec)]

def parse_buckets(bucket_specs: List[str]) -> List[Bucket]:
    result = []
    for buckets in [parse_bucket(spec) for spec in bucket_specs]:
        result.extend(buckets)
    return result

def main() -> None:
    buckets = parse_buckets(sys.argv[1:])
    items   = parse_items(sys.stdin.buffer)

    for item in abandon(buckets, items):
        sys.stdout.buffer.write(item)

if __name__ == '__main__':
    main()

