def deep_equals(obj1, obj2) -> bool:
    """
    Recursively compares two objects for deep equality.
    Handles nested lists, dictionaries, tuples, and sets.
    """
    # Check if types are the same
    if type(obj1) is not type(obj2):
        return False

    # Compare dictionaries
    if isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False
        if obj1.keys() != obj2.keys():
            return False
        for key in obj1:
            if not deep_equals(obj1[key], obj2[key]):
                return False
        return True

    # Compare lists or tuples
    if isinstance(obj1, (list, tuple)):
        if len(obj1) != len(obj2):
            return False
        for item1, item2 in zip(obj1, obj2):
            if not deep_equals(item1, item2):
                return False
        return True

    # Compare sets
    if isinstance(obj1, set):
        # Standard set comparison is inherently deep for its elements
        return obj1 == obj2

    # For all other types (primitives, custom objects with __eq__), use standard comparison
    return obj1 == obj2
