class Logger:
    @classmethod
    def _log_completion(cls: Logger, input: list, output: str, metadata: dict):
        return
    @classmethod
    async def _alog_completion(cls: Logger, input: list, output: str, metadata: dict):
        import asyncio
        return await asyncio.to_thread(cls._log_completion, input, output, metadata)
