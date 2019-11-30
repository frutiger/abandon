# tests.abandon

from datetime import datetime, timedelta
from typing   import Any, Dict, Iterator, List, Tuple
from unittest import TestCase

from abandon import abandon, Bucket, Decision, Items

def parse_buckets(buckets: str) -> List[Bucket]:
    result = []
    end   = buckets.rfind('|')
    index = end - 1
    while index >= 0:
        if buckets[index] == '|':
            delta = end - index
            result.append((str(delta), timedelta(seconds=delta)))
            end = index
        index -= 1
    return result

def parse_items(items: str) -> Items:
    result = {}
    count  = 0
    for index, char in enumerate(items):
        if char == '*':
            result[datetime.fromtimestamp(index)] = bytes(f'i{count}', 'ascii')
            count += 1
        elif char == '-':
            count += 1
    return result

def parse_explain(items: str) -> Dict[int, str]:
    result: Dict[int, str] = {}
    for index, char in enumerate(items):
        if char != ' ':
            result[index] = char
    return result

class AbandonTestCase(TestCase):
    def __init__(self, cases: str) -> None:
        TestCase.__init__(self, cases)
        self.input:   Tuple[str, str]
        self.expect:  str
        self.explain: str

    def _check_abandoned(self) -> None:
        buckets = parse_buckets(self.input[0])
        items   = parse_items(self.input[1])

        abandoned = [d.item for d in abandon(buckets, items) if d.abandon]
        expected  = parse_items(self.expect).values()
        self.assertEqual(set(abandoned), set(expected))

    def _check_explain(self) -> None:
        buckets = parse_buckets(self.input[0])
        items   = parse_items(self.input[1])

        explained = parse_explain(self.explain)
        kept = []
        for decision in abandon(buckets, items):
            if not decision.abandon:
                assert(decision.bucket is not None)
                print(decision.item)
                print(decision.time)
                kept.append(decision.bucket[0])
        print(kept)
        print(explained)

    def check(self) -> None:
        self._check_abandoned()
        self._check_explain()

class AllItemsAbandonedWhenNoBuckets(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('                   ',
                        ' * * * * * * * * * ')
        self.expect  =  ' * * * * * * * * * '
        self.explain =  '                   '
        self.check()

class OneItemAlwaysPreservedNewer(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('||',
                        '   * * *')
        self.expect  =  '   * * -'
        self.explain =  '       1'
        self.check()

class OneItemAlwaysPreservedOlder(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('     ||',
                        '* * *  ')
        self.expect  =  '* * -  '
        self.explain =  '    1  '
        self.check()

class OnePerBucket(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('|||||',
                        '****')
        self.expect  =  '----'
        self.explain =  '1111'
        self.check()

class AbandonOldestOneOutOfTwo(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('| |',
                        '**')
        self.expect  =  '*-'
        self.explain =  ' 2'
        self.check()

class AbandonOldestOneOutOfTwoRepeat(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('| | |',
                        '****')
        self.expect  =  '*-*-'
        self.explain =  ' 2 2'
        self.check()

class AbandonOldestThreeOutOfFour(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('|   |   |',
                        '********')
        self.expect  =  '***-***-'
        self.explain =  '   4   4'
        self.check()

class UnallocatedBucketSeeksBackwards(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('    |  |  |  |',
                        '  *     *  *  ')
        self.expect  =  '  -     -  -  '
        self.explain =  '  3     3  3  '
        self.check()

class AllBucketsAreAllocatedIfPossible(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('| | |',
                        '**')
        self.expect  =  '*-'
        self.explain =  ' 2'
        self.check()

class RolloverPossible(AbandonTestCase):
    def test(self) -> None:
        self.input   = ('    |   |   | | |',
                        ' * * * * * * * *')
        self.expect  =  ' * * * - * - - -'
        self.explain =  '       4   2 2 2'
        self.check()

