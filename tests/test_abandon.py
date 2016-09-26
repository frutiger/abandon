# tests.abandon

from datetime import datetime, timedelta
from typing   import Any, Dict, Iterator, List, Tuple
from unittest import TestCase

from abandon import abandon, Bucket, Items

def parse_buckets(buckets: str) -> List[Bucket]:
    result = []
    end   = buckets.rfind('|')
    index = end - 1
    while index >= 0:
        if buckets[index] == '|':
            result.append(timedelta(seconds=end-index))
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

class AbandonTestCase(TestCase):
    def __init__(self, cases: str) -> None:
        TestCase.__init__(self, cases)
        self.input:  Tuple[str, str]
        self.expect: str

    def check(self) -> None:
        buckets = parse_buckets(self.input[0])
        items   = parse_items(self.input[1])
        result  = abandon(buckets, items)
        expect  = parse_items(self.expect).values()
        self.assertEqual(set(result), set(expect))

class AllItemsAbandonedWhenNoBuckets(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('                   ',
                       ' * * * * * * * * * ')
        self.expect =  ' * * * * * * * * * '
        self.check()

class OneItemAlwaysPreservedNewer(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('||',
                       '   * * *')
        self.expect =  '   * * -'
        self.check()

class OneItemAlwaysPreservedOlder(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('     ||',
                       '* * *  ')
        self.expect =  '* * -  '
        self.check()

class OnePerBucket(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('|||||',
                       '****')
        self.expect =  '----'
        self.check()

class AbandonOldestOneOutOfTwo(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('| |',
                       '**')
        self.expect =  '*-'
        self.check()

class AbandonOldestOneOutOfTwoRepeat(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('| | |',
                       '****')
        self.expect =  '*-*-'
        self.check()

class AbandonOldestThreeOutOfFour(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('|   |   |',
                       '********')
        self.expect =  '***-***-'
        self.check()

class UnallocatedBucketSeeksBackwards(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('    |  |  |  |',
                       '  *     *  *  ')
        self.expect =  '  -     -  -  '
        self.check()

class AllBucketsAreAllocatedIfPossible(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('| | |',
                       '**')
        self.expect =  '*-'
        self.check()

class RolloverPossible(AbandonTestCase):
    def test(self) -> None:
        self.input  = ('    |   |   | | |',
                       ' * * * * * * * *')
        self.expect =  ' * * * - * - - -'
        self.check()

