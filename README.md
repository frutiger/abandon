# Abandon

Modern filesystems (and backup systems) operate by allowing a user to take
snapshots of their datasets.  A common strategy is to have a cron job (or
similar) to take regular, frequent snapshots (e.g. hourly, or daily).  If left
unchecked, the list of snapshots will grow linearly with time.  For many modern
systems, these snapshots operate on a copy-on-write basis, adding insubstantial
overhead.

However, a large list of snapshots can add to administrative overhead: going
over a list of thousands of snapshots is not very convenient.  Typically, users
want to regularly prune the list of snapshots so that some specification of
snapshots (called *buckets*) remain.  e.g. 10 hourly snapshots, 30 daily
snapshots, 5 quarterly snapshots, 5 yearly snapshots.

`abandon` is a tool that takes the bucket specs as command line parameters, and
the list of snapshot creation time and snapshot name in reverse chronological
order on `stdin` will output the list of snapshot names that should be deleted
to satisfy the bucket specs.

Note that nothing in `abandon` is specific to any particular file nor backup
system, or even to such systems at all, but they are the motivating case for
this tool.

### Usage example

First, we generate a list of timestamps and item names corresponding to the
last 10 hours:

```bash
$ for i in $(seq 0 9); do echo $[ $(date +%s) - $i * 3600 ]	Item $i; done
1480276024	Item 0
1480272424	Item 1
1480268824	Item 2
1480265224	Item 3
1480261624	Item 4
1480258024	Item 5
1480254424	Item 6
1480250824	Item 7
1480247224	Item 8
1480243624	Item 9
```

Then, we ask `abandon` to preserve 5 hourly items, and see that it tells us to
delete the 5 oldest snapshots

```bash
$ for i in $(seq 0 9); do echo $[ $(date +%s) - $i * 3600 ]	Item $i; done \
        | python3 -m abandon 5@h
Item 5
Item 6
Item 7
Item 8
Item 9
```

To make it easier to determine what remains, we can use the `comm` and `sort`
tools:

```bash
$ comm -23 \
         <(seq 0 9 | sed 's/^/Item '/ | sort) \
         <(for i in $(seq 0 9); do echo "$[ $(date +%s) - $i * 3600 ] Item $i"; done \
           | python3 -m abandon 5@1h | sort) \
         | sort -k2n
Item 0
Item 1
Item 2
Item 3
Item 4
```

We can try more complex scenarios.  e.g. 200 hourly items, but only keep 10
hourly and 10 daily snapshots:

```bash
$ comm -23 \
         <(seq 0 199 | sed 's/^/Item '/ | sort) \
         <(for i in $(seq 0 199); do echo "$[ $(date +%s) - $i * 3600 ] Item $i"; done \
           | python3 -m abandon 10@1h 10@1d | sort) \
         | sort -k2n
Item 0
Item 1
Item 2
Item 3
Item 4
Item 5
Item 6
Item 7
Item 8
Item 9
Item 10
Item 34
Item 58
Item 82
Item 106
Item 130
Item 154
Item 178
```

We can see that it kept the 10 most recent items, and then up to 10 more each
separated by 24 hours, as expected.

### Bucket specs

Bucket specs are expected to be of the form `<num_buckets>@<duration><unit>`,
e.g. `5@1h` or `10@3m`.  Expected units are:

| unit | meaning |
| ---- | ------- |
| h    | hour    |
| d    | day     |
| m    | month   |
| y    | year    |

### Input format

Items are expected to be supplied as seconds since the Unix epoch in UTC,
followed by whitespace followed by an item name.  Item names cannot be
duplicated.

# License

Copyright (C) 2016 Masud Rahman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

