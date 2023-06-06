# completion_logger

This package mutates the openai-python package so as to log all Python completion
requests made to OpenAI's API, onto the Arweave blockchain.

## installation

```
python3 -m pip install git+https://github.com/xloem/completion_logger
```

## info

URLs to the logged data are output at the `INFO` level via Python's `logging` module.

## caveat

This package mutates the openai package on install, so must be reinstalled if the
openai package is. A more thorough implementation might also mutate pip itself so as
to retain the addition.

More elegant solutions to the task of logging and sharing this information likely also
exist.

## reasoning

It's become a norm for language model interfaces to offer an API that can act as
a partial drop-in replacement for OpenAI's, so that the same applications may be used
with them.

Hence, it is effective to make use of OpenAI's client library for general logging, as
this can now function for other backends as well.
