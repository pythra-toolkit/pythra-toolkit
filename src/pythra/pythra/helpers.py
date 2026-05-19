

def to_px(value):
    if isinstance(value, (int, float)):
        return f"{value}px"
    elif isinstance(value, str):
        return value
    else:
        raise TypeError("Value must be an int, float, or str")