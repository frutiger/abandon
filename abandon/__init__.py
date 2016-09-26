# abandon.__init__

import itertools
from   datetime import datetime, timedelta
from   typing   import Dict, Iterator, List, Optional, Tuple

Bucket = timedelta
Items  = Dict[datetime, bytes]

def abandon_rest(item_times: List[datetime], items: Items) -> Iterator[bytes]:
    while item_times:
        yield items[item_times.pop(0)]

def abandon(buckets: List[Bucket], items: Items) -> Iterator[bytes]:
    item_times = sorted(items.keys(), key=lambda x: -x.timestamp())

    last_item_time: Optional[datetime] = None
    while True:
        if len(buckets) == 0:
            yield from abandon_rest(item_times, items)
            break
        last_bucket: Bucket = buckets.pop(0)

        if len(item_times) == 0:
            break
        if last_item_time is None:
            last_item_time = item_times.pop(0)

        last_item_time -= last_bucket
        while True:
            if len(item_times) == 0:
                break

            item_time = item_times.pop(0)
            if item_time > last_item_time:
                yield items[item_time]
            else:
                if len(buckets) == 0:
                    yield items[item_time]
                break
        last_item_time = item_time

