def map(key: str, value: str):
    words = value.replace(",", " ").replace(".", "").replace(":", "").split()
    result = []
    for word in words:
        yield word.lower(), 1


def reduce(key: str, values: list) -> str:
    return len(values)


def partitioner(key: str, partition_count: int) -> int:
    hash_value = 0
    for i, char in enumerate(key):
        hash_value = (hash_value * base + ord(char)) % partition_count
    return hash_value