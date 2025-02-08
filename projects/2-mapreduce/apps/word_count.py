def map(key: str, value: str) -> list:
    words = value.replace(",", " ").replace(".", "").replace(":", "").split()
    result = []
    for word in words:
        result.append((word.lower(), 1))
    return result


def reduce(key: str, values: list) -> str:
    return len(values)


def partitioner(key: str) -> int:
    return ord(
        key[0]
    )  # very simple partitioning key using the number value of the first char of the key
