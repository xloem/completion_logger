import datetime
import sys
import logging

# service loggers for larger data
from .loggers import Arweave
DEFAULT_LOGGER = Arweave

# python logger for user information
logger = logging.getLogger(__name__)

class Log:
    def __init__(self, input, metadata, logger = None, initial = '', processor = None):
        self.logger = logger or DEFAULT_LOGGER
        self.input = input
        self.metadata = metadata
        self.metadata['timestamp'] = datetime.datetime.now().isoformat()
        self.initial = initial
        if processor is not None:
            self.processor = processor
    def stream(self, output):
        with self:
            for token in output:
                self.add(token)
                yield token
    async def astream(self, output):
        async with self:
            async for token in output:
                self.add(token)
                yield token
    def add(self, output):
        processed_output = self.processor(output)
        self.output += processed_output
        return output

    @staticmethod
    def processor(text):
        return text
    def __enter__(self):
        self.output = self.initial
        return self
    async def __aenter__(self):
        self.output = self.initial
        return self
    def __exit__(self, *exc):
        if self.logger is not None:
            if self.output != self.initial:
                locator = self.logger._log_completion(self.input, self.output, self.metadata)
                logger.info(f'Logged {locator}')
        del self.output
    async def __aexit__(self, *exc):
        if self.logger is not None:
            if self.output != self.initial:
                locator = await self.logger._alog_completion(self.input, self.output, self.metadata)
                logger.info(f'Logged {locator}')
        del self.output
