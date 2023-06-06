# completion_logger

This package mutates the openai-python package so as to log requests made via Python to
OpenAI's API onto the Arweave blockchain.

## installation

```
python3 -m pip install git+https://github.com/xloem/completion_logger
```

## info

URLs to the logged data are output at the `INFO` level via Python's `logging` module.
