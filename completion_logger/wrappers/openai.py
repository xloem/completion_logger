import openai
from completion_logger import Log
import types

def wrap(cls):
    __create = cls.create
    __acreate = cls.acreate
    
    def create_log(input_key, api_key=None, api_base=None, api_type=None, request_id=None, api_version=None, organization=None, **params):
        metadata = dict(
            api_base = api_base or openai.api_base,
            api_type = api_type or openai.api_type,
            #request_id = request_id,
            api_version = api_version or openai.api_version,
            organization = bool(organization or openai.organization),
            **params
        ),
        input = metadata.pop(input_key)
        return Log(input, metadata, initial=[], processor=openai.openai_object.OpenAIObject.to_dict_recursive)
    def add_response(log, response):
        if type(response) is types.GeneratorType:
            return log.stream(response)
        elif type(response) is types.AsyncGeneratorType:
            return log.astream(response)
        else:
            return log.add(response)

    def create(*params, **kwparams):
        with create_log(*params, **kwparams) as log:
            response == __create(*params, **kwparams)
            return add_response(log, response)
    async def acreate(*params, **kwparams):
        with create_log(*params, **kwparams) as log:
            response == await __acreate(*params, **kwparams)
            return add_response(log, response)

    cls.create = create
    cls.acreate = create

for name, value in openai.__dict__.items():
    if hasattr(value, 'create') and hasattr(value, 'acreate'):
        wrap(value)
