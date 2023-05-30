import datetime
import sys
import logging

# service loggers for larger data
from .loggers import Arweave
DEFAULT_LOGGER = Arweave

# python logger for user information
logger = logging.getLogger(__name__)

class Log:
    def __init__(self, input, metadata, logger = None):
        self.logger = logger or DEFAULT_LOGGER
        self.input = input
        self.metadata = metadata
        self.metadata['timestamp'] = datetime.datetime.now().isoformat()
    def stream(self, output):
        with self:
            for token in output:
                self.output += token
                yield token
    async def astream(self, output):
        async with self:
            async for token in output:
                self.output += token
                yield token
    def complete(self, output):
        with self:
            self.output = ''.join(output)
            return self.output
    async def acomplete(self, output):
        async with self:
            self.output = ''.join(output)
            return self.output
    def __enter__(self):
        self.output = ''
        return self
    async def __aenter__(self):
        self.output = ''
        return self
    def __exit__(self, *exc):
        if self.logger is not None:
            locator = self.logger._log_completion(self.input, self.output, self.metadata)
            logger.info(f'Logged {locator}')
    async def __aexit__(self, *exc):
        if self.logger is not None:
            locator = await self.logger._alog_completion(self.input, self.output, self.metadata)
            logger.info(f'Logged {locator}')
