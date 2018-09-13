
def multi_getattr(obj, attr, **kwargs):
    attributes = attr.split('.')
    for attribute in attributes:
        try:
            obj = getattr(obj, attribute)
        except AttributeError:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise
    return obj