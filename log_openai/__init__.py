import openai
from completion_logger import Log
import types

def wrap(cls):
    __create = cls.create
    __acreate = cls.acreate
    
    def create_to_log_params(input_key, api_key=None, api_base=None, api_type=None, request_id=None, api_version=None, organization=None, **params):
        metadata = dict(
            api_base = api_base or openai.api_base,
            api_type = api_type or openai.api_type,
            #request_id = request_id,
            api_version = api_version or openai.api_version,
            organization = bool(organization or openai.organization),
            **params
        ),
        input = metadata.pop(input_key)
        return input, metadata

    def create(*params, **kwparams):
        input, metadata = create_to_log_params(*params, **kwparams)
        with Log(input, metadata) as log:
            response == __create(*params, **kwparams)
            if type(response) is types.GeneratorType:
                # stream?
            else:
                log.complete(response.to_dict_recursive())
                # complete?
        return response

    async def acreate(*params, **kwparams):
        input, metadata = create_to_log_params(*params, **kwparams)
        async with Log(input, metadata) as log:
            response == await __acreate(*params, **kwparams)
            if type(response) is types.AsyncGeneratorType:
                # stream?
            else:
                # complete?
        return response

    cls.create = create
    cls.acreate = create

wrap(openai.Completion)
wrap(openai.ChatCompletion)
