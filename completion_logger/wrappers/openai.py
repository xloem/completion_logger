import openai
from completion_logger import Log
import types

def wrap(cls, input_keys):
    __create = cls.create
    __acreate = cls.acreate
    
    def create_log(api_key=None, api_base=None, api_type=None, request_id=None, api_version=None, organization=None, **params):
        metadata = dict(
            api_base = api_base or openai.api_base,
            api_type = api_type or openai.api_type,
            #request_id = request_id,
            api_version = api_version or openai.api_version,
            organization = bool(organization or openai.organization),
            **params
        )
        if len(input_keys) == 1:
            input = metadata.pop(input_keys[0], None)
        else:
            input = {
                input_key: metadata.pop(input_key, None)
                for input_key in input_keys
            }
        return Log(
            input,
            metadata,
            processor=openai.openai_object.OpenAIObject.to_dict_recursive,
            stream_constructor=list,
            stream_processor=lambda line: [line.to_dict_recursive()],
        )
    def add_response(log, response):
        if type(response) is types.GeneratorType:
            return log.stream(response)
        elif type(response) is types.AsyncGeneratorType:
            return log.astream(response)
        else:
            return log.complete(response)

    def create(*params, **kwparams):
        with create_log(*params, **kwparams) as log:
            response = __create(*params, **kwparams)
            return add_response(log, response)
    async def acreate(*params, **kwparams):
        async with create_log(*params, **kwparams) as log:
            response = await __acreate(*params, **kwparams)
            return add_response(log, response)

    cls.create = create
    cls.acreate = acreate

for name, value in openai.__dict__.items():
    input_keys = {
        'completions': ['prompt'],
        'chat.completions': ['messages'],
        'edits': ['input', 'instruction'],
        'images.generations': ['prompt'],
        'images.edits': ['image'],
        'images.variations': ['image'],
        'embeddings': ['input'],
        'audio.transcriptions': ['file'],
        'audio.translations': ['file'],
        'moderations': ['input'],
    }.get(getattr(value, 'OBJECT_NAME', None))
    if input_keys is not None and hasattr(value, 'create') and hasattr(value, 'acreate'):
        wrap(value, input_keys)
