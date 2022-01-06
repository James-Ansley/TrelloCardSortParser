import os
from csv import DictReader

import list2csv

from utils.pairwise_writer import write_pairs, map_pairs
from utils.sorts import edit_distance, co_occurrence_distance, co_edit_distance
from utils.trello_parser import parse_sorts_in_dir

CARD_ID_PATH = 'resources/question_data.csv'
SORT1_JSONS_PATH = 'resources/sort1'
SORT2_JSONS_PATH = 'resources/sort2'
PROBE_JSONS_PATH = 'resources/probes'
OUT_DIR = 'resources/out'


def main():
    card_ids = get_card_ids(CARD_ID_PATH)
    sort1 = parse_sorts_in_dir(SORT1_JSONS_PATH, card_ids)
    sort2 = parse_sorts_in_dir(SORT2_JSONS_PATH, card_ids)
    probe_sorts = parse_sorts_in_dir(PROBE_JSONS_PATH, card_ids)

    # Write simple stats such as number of groups, time taken, and edit distance
    # to probe sorts.
    with open(os.path.join(OUT_DIR, 'stats.csv'), 'w', newline='') as f:
        write_simple_stats(f, sort1 + sort2, probe_sorts)

    for sort_num, sort in (1, sort1), (2, sort2):
        # Co-occurrence distance matrix
        co_edit_distance_path = get_csv_path('pairwise_edit_distance', sort_num)
        with open(co_edit_distance_path, 'w', newline='') as f:
            write_pairwise_edit_distance(f, sort)

        # Pairwise edit distance matrix
        co_distance_path = get_csv_path('co_distance_matrix', sort_num)
        with open(co_distance_path, 'w', newline='') as f:
            write_co_occurrence_distance(f, sort)


def get_card_ids(path, prompt_header='prompt', id_header='id'):
    """
    Returns a dictionary mapping card prompts to their corresponding IDs from
    the CSV at the given path.
    """
    with open(path) as f:
        reader = DictReader(f)
        return {row[prompt_header]: row[id_header] for row in reader}


def get_csv_path(file_name, sort_num):
    """
    Returns the path {OUT_DIR}/{file_name}_{sort_num}.csv.
    """
    file_name = f'{file_name}_{sort_num}.csv'
    path = os.path.join(OUT_DIR, file_name)
    return path


def write_simple_stats(f, sorts, probe_sorts):
    """
    Writes basic statistics about each sort to a CSV file including the sort
    id, number of groups, time taken, and edit distance to probe sorts.
    """
    writer = list2csv.Writer(f)
    writer.add_column('Sort ID', 'id')
    writer.add_column('Num Groups', lambda s: len(s.groups))
    writer.add_column('Time (sec)', lambda s: s.time.seconds)
    for probe in probe_sorts:
        writer.add_column(probe.id, lambda s, p=probe: edit_distance(s, p))

    writer.write_header()
    writer.write_all(sorts)


def write_co_occurrence_distance(f, sorts):
    """
    Writes the pairwise co-occurrence distance between each sort to a CSV file.
    """
    co_distance = co_occurrence_distance(sorts)
    write_pairs(f, co_distance)


def write_pairwise_edit_distance(f, sorts):
    """
    Writes the pairwise edit distance between each sort to a CSV file.
    """
    pairwise_edit_distance = co_edit_distance(sorts)
    pairs = map_pairs(pairwise_edit_distance, header=lambda s: s.id)
    write_pairs(f, pairs)


if __name__ == '__main__':
    main()
