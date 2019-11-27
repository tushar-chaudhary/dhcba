def compare(obj):
    if isinstance(obj, dict):
        return sorted((k, compare(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(compare(x) for x in obj)
    else:
        return obj