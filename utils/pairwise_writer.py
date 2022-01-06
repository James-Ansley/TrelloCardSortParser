from collections import defaultdict
from csv import DictWriter
from typing import TextIO, TypeVar, Callable

T = TypeVar("T")
T1 = TypeVar("T1")
V = TypeVar("V")
V1 = TypeVar("V1")

header_mapping = Callable[[T], T1]
data_mapping = Callable[[V], V1]


def map_pairs(pairs: dict[T, dict[T, V]],
              header: header_mapping = lambda x: x,
              data: data_mapping = lambda x: x) -> dict[T1, dict[T1, V1]]:
    """
    Converts nested dictionaries to string representations via the header and
    data mapping functions.
    """
    string_pairs = defaultdict(dict)
    for key, values in pairs.items():
        for key1, value in values.items():
            string_pairs[header(key)][header(key1)] = data(value)
    return string_pairs


def write_pairs(f: TextIO, pairs: dict[T, dict[T, V]]) -> None:
    """
    Writes nested dictionaries in CSV matrix format. A header row and column
    is added with the top left cell being empty.

    If the default str values for types T and V are inappropriate, use the
    map_pairs function to map these values to the desired data.
    """
    fieldnames = ['', *pairs.keys()]
    writer = DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for key, row_values in pairs.items():
        row = {'': key, **row_values}
        writer.writerow(row)
