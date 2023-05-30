# wrapped via completion_logger

import pkgutil
__all__ = []
for modobj in pkgutil.iter_modules(imported_module.__path__):
    modname = modobj.name
    mod = modobj.module_finder.find_module(modname).load_module(modname)
    objname = modobj.name.title().replace('_','')
    try:
        globals()[objname] = getattr(mod, objname)
    except AttributeError:
        continue
    __all__.append(objname)

import completion_logger.openai
