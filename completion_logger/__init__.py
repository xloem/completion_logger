import datetime
import sys
import logging

# service loggers for larger data
from .loggers import Arweave
DEFAULT_LOGGER = Arweave

# python logger for user information
logger = logging.getLogger(__name__)

class Log:
    def __init__(self,
        input,
        metadata,
        logger = None,
        processor = None,
        stream_constructor = str,
        stream_processor = None,
    ):
        self.logger = logger or DEFAULT_LOGGER
        self.input = input
        self.metadata = metadata
        self.metadata['timestamp'] = datetime.datetime.now().isoformat()
        if processor is not None:
            self.processor = processor
        self.stream_constructor = stream_constructor
        self.stream_processor = stream_processor or self.processor
    def stream(self, output):
        if self.output is None:
            self.output = self.stream_constructor()
        for token in output:
            processed_token = self.stream_processor(token)
            self.output += processed_token
            yield token
    async def astream(self, output):
        if self.output is None:
            self.output = self.stream_constructor()
        async for token in output:
            processed_token = self.stream_processor(token)
            self.output += processed_token
            yield token
    def complete(self, output):
        assert self.output is None
        processed_output = self.processor(output)
        self.output = processed_output
        return output

    @staticmethod
    def processor(text):
        return text
    def __enter__(self):
        self.output = None
        return self
    async def __aenter__(self):
        self.output = None
        return self
    def __exit__(self, *exc):
        if self.logger is not None:
            if self.output is not None:
                locator = self.logger._log_completion(self.input, self.output, self.metadata)
                logger.info(f'Logged {locator}')
        del self.output
    async def __aexit__(self, *exc):
        if self.logger is not None:
            if self.output is not None:
                locator = await self.logger._alog_completion(self.input, self.output, self.metadata)
                logger.info(f'Logged {locator}')
        del self.output
