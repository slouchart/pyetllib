from toolz import curry


from .core import (
    fremove as fremove_,
    fextract as fextract_,
    frename as frename_,
    freverse_lookup as freverse_lookup_,
    flookup as flookup_,
    fmap as fmap_,
    fsplit as fsplit_
)


fremove = curry(fremove_)
fextract = curry(fextract_)
frename = curry(frename_)
freverse_lookup = curry(freverse_lookup_)
flookup = curry(flookup_)
fmap = curry(fmap_)
fsplit = curry(fsplit_)
