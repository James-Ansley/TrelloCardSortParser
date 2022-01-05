import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from itertools import permutations
from typing import TypeVar

from munkres import make_cost_matrix, Munkres

T = TypeVar('T')


@dataclass(frozen=True)
class Sort:
    """
    Creates a list of sorts with a name, a list of groups, and optionally a
    timedelta for measuring the time taken to perform the sort.

    Sort names should be unique and are used when hashing and checking
    equality.
    """
    name: str
    groups: list['Group']
    time: timedelta = None

    @property
    def cards(self):
        return set.union(*(group.cards for group in self.groups))

    def __str__(self):
        return (f'{self.name}: '
                f'[{", ".join(str(group) for group in self.groups)}]')

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class Group:
    name: str
    cards: set[T] = field(default_factory=set)

    def __str__(self):
        return f'{self.name}: [{", ".join(map(str, self.cards))}]'


def edit_distance(sort1: Sort, sort2: Sort) -> int:
    """
    Returns the edit distance between two Sorts using the method described by
    Deibel et al.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    matching_weights = [[] for _ in range(len(sort1.groups))]
    for i, group1 in enumerate(sort1.groups):
        for group2 in sort2.groups:
            intersection = len(group1.cards & group2.cards)
            matching_weights[i].append(intersection)

    cost_matrix = make_cost_matrix(matching_weights)

    running_sum = 0
    for row, col in Munkres().compute(cost_matrix):
        running_sum += matching_weights[row][col]

    return len(sort1.cards) - running_sum


def co_occurrence_matrix(sorts: list[Sort]) -> dict[T, dict[T, float]]:
    """
    Returns the co-occurrence matrix of cards in the given sort list as a
    nested dictionary mapping two card IDs to the co-occurrence of the two
    cards.

    Co-occurrences are scaled to be between 0 and 1.
    """
    cards = sorted(sorts[0].cards)
    occurrences = {card1: {card2: 0 for card2 in cards} for card1 in cards}
    for sort in sorts:
        for group in sort.groups:
            for card in group.cards:
                occurrences[card][card] += 1

            card_pairs = permutations(group.cards, 2)
            for card1, card2 in card_pairs:
                occurrences[card1][card2] += 1

    for card1, row in occurrences.items():
        for card2, value in row.items():
            occurrences[card1][card2] = value / len(sorts)
    return occurrences


def co_occurrence_distance(sorts: list[Sort]) -> dict[T, dict[T, float]]:
    """
    Returns the co-occurrence distance matrix of cards in the given sort list
    as a nested dictionary mapping two card IDs to the co-occurrence distance
    of the two cards.

    Co-occurrence distances are scaled to be between 0 and 1.
    """
    cards = sorted(sorts[0].cards)
    co_occurrence = co_occurrence_matrix(sorts)
    for card1 in cards:
        for card2 in cards:
            co_occurrence[card1][card2] = 1 - co_occurrence[card1][card2]
    return co_occurrence


def co_edit_distance(sorts: list[Sort]) -> dict[str, dict[str, int]]:
    """
    Returns the pairwise edit distance matrix of cards in the given sort list
    as a nested dictionary mapping two sort names to the edit distance of the
    two sorts.
    """
    pairwise_distances = defaultdict(dict)
    for sort1 in sorts:
        for sort2 in sorts:
            distance = edit_distance(sort1, sort2)
            pairwise_distances[sort1.name][sort2.name] = distance
    return pairwise_distances


def find_neighbourhood(sort: Sort, sorts: list[Sort], d: int) -> list[Sort]:
    """
    Returns the d-neighbourhood of a sort as a list of sorts. The given sort
    may be a probe sort not included in the sorts list; however, the returned
    neighbourhood will not include the probe sort.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    neighbourhood = []
    for other in sorts:
        if edit_distance(sort, other) <= d:
            neighbourhood.append(other)
    return neighbourhood


def _cull(s_c, v, sorts, d):
    """
    Lines 6 and 7 from Figure 2, Deibel et al. Removes sort `v` from `s_c`
    and any sorts outside the max distance `d` from `v`

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    s_v = {x for x in sorts if x != v and edit_distance(v, x) <= d}
    return s_c & s_v


def _max_culled(s_c, sorts, d):
    """
    Returns all `v` and resulting `s_c` such that `s_c` is the maximum length
    after s_c is culled.
    """
    max_pairs = []
    max_len = 0
    for i, v in enumerate(s_c):
        new_s_c = _cull(s_c, v, sorts, d)
        if len(new_s_c) > max_len:
            max_len = len(new_s_c)
            max_pairs = [(v, new_s_c)]
        elif len(new_s_c) == max_len:
            max_pairs.append((v, new_s_c))
    return max_pairs


def find_clique_random(sort: Sort, sorts: list[Sort], d: int) -> set[Sort]:
    """
    Returns the d-clique of a sort as a list of sorts using a random heuristic.
    The given sort may be a probe sort not included in the sorts list;
    however, the returned clique will not include the probe sort.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    clique = {sort} if sort in sorts else set()
    s_c = {x for x in sorts if x != sort and edit_distance(sort, x) <= d}
    while s_c:
        v = random.sample(s_c, 1)[0]
        clique.add(v)
        s_c = _cull(s_c, v, sorts, d)
    return clique


def find_clique_greedy(sort: Sort, sorts: list[Sort], d: int) -> set[Sort]:
    """
    Returns the d-clique of a sort as a list of sorts using the greedy
    heuristic described by Deibel et al. The given sort may be a probe sort
    not included in the sorts list; however, the returned clique will not
    include the probe sort.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    clique = {sort} if sort in sorts else set()
    s_c = {x for x in sorts if x != sort and edit_distance(sort, x) <= d}
    while s_c:
        # In cases where several sorts satisfy the greedy rule,
        # one is chosen randomly
        possible_vs = _max_culled(s_c, sorts, d)
        v, s_c = random.choice(possible_vs)
        clique.add(v)
    return clique
