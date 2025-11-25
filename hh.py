def _normalize_schema_enums(obj):
    if isinstance(obj, dict):
        # Fix enum
        if "enum" in obj and isinstance(obj["enum"], list):
            obj["enum"] = [str(v) for v in obj["enum"]]
        # Recurse into all keys
        for k, v in obj.items():
            obj[k] = _normalize_schema_enums(v)
        return obj
    elif isinstance(obj, list):
        return [_normalize_schema_enums(i) for i in obj]
    else:
        return obj