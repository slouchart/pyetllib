# `etllib.publish` — data publication to IO streams
---

## function `publish_to_stream`
`publish_to_stream(*iterators, **ctx)`
 iterates over the list of `iterators` and exhausts all their items to
a stream that defaults to `sys.stdout`. The following context parameters
can be specified:

* `stream`: an instance of `io.TextIOBase` (or basically anything that implements a `write` method accepting Unicode strings)

* `record_delimiter`: a string added as a newline character

* `record_converter`: a `Callable` that accepts any type and returns a string.