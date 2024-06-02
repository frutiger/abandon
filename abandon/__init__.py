# abandon.__init__

import itertools
from   datetime import datetime, timedelta
from   typing   import Dict, Iterator, List, Optional, Tuple

Bucket = Tuple[str, timedelta]
Items  = Dict[datetime, bytes]

class Decision:
    item:    bytes
    time:    datetime
    abandon: bool
    bucket:  Optional[Bucket]

    def __init__(self,
                 item:    bytes,
                 time:    datetime,
                 abandon: bool,
                 bucket:  Optional[Bucket]) -> None:
        assert(abandon or bucket is not None)
        self.item    = item
        self.time    = time
        self.abandon = abandon
        self.bucket  = bucket

def abandon(buckets: List[Bucket], items: Items) -> Iterator[Decision]:
    item_times = sorted(items.keys(), key=lambda x: -x.timestamp())

    last_item_time: Optional[datetime] = None
    while True:
        if len(buckets) == 0:
            while item_times:
                item_time = item_times.pop(0)
                yield Decision(items[item_time], item_time, True, None)
            break
        last_bucket: Bucket = buckets.pop(0)

        if len(item_times) == 0:
            break
        if last_item_time is None:
            last_item_time = item_times.pop(0)
            yield Decision(items[last_item_time],
                           last_item_time,
                           False,
                           last_bucket)

        last_item_time -= last_bucket[1]
        while True:
            if len(item_times) == 0:
                break

            item_time = item_times.pop(0)
            if item_time > last_item_time:
                yield Decision(items[item_time], item_time, True, None)
            else:
                yield Decision(items[item_time], item_time, False, last_bucket)
                if len(buckets) == 0:
                    yield Decision(items[item_time], item_time, True, None)
                break
        last_item_time = item_time

