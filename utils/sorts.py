import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from itertools import permutations
from typing import TypeVar, Iterable, Collection

from munkres import make_cost_matrix, Munkres

T = TypeVar('T')


@dataclass(frozen=True)
class Sort:
    """
    A sort with an ID, a list of groups, a set of all cards used in the sort
    and optionally a timedelta for measuring the time taken to perform the
    sort.

    Sort IDs should be unique and are used when hashing and checking
    equality.
    """
    id: str
    groups: list['Group']
    cards: set
    time: timedelta = None

    def __str__(self):
        return (f'{self.id}: '
                f'[{", ".join(str(group) for group in self.groups)}]')

    def __repr__(self):
        # Often more useful to just use the ID when printing nested data
        # structures of sorts.
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


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


def co_occurrence_matrix(
        sorts: Collection[Sort], cards: set) -> dict[T, dict[T, float]]:
    """
    Returns the co-occurrence matrix of cards in the given sort list as a
    nested dictionary mapping two card IDs to the co-occurrence of the two
    cards.

    This is simply a count of how many times any two cards are put together
    in the same group.
    """
    occurrences = {card1: {card2: 0 for card2 in cards} for card1 in cards}
    for sort in sorts:
        for group in sort.groups:
            for card in group.cards:
                occurrences[card][card] += 1

            card_pairs = permutations(group.cards, 2)
            for card1, card2 in card_pairs:
                occurrences[card1][card2] += 1
    return occurrences


def co_occurrence_distance(
        sorts: Collection[Sort], cards: set) -> dict[T, dict[T, float]]:
    """
    Returns the co-occurrence distance matrix of cards in the given sort list
    as a nested dictionary mapping two card IDs to the co-occurrence distance
    of the two cards.

    This is simply a count of how many times any two cards are NOT put together
    in the same group.
    """
    co_occurrence = co_occurrence_matrix(sorts, cards)
    for card1 in cards:
        for card2 in cards:
            distance = len(sorts) - co_occurrence[card1][card2]
            co_occurrence[card1][card2] = distance
    return co_occurrence


def co_edit_distance(sorts: Iterable[Sort]) -> dict[Sort, dict[Sort, int]]:
    """
    Returns the pairwise edit distance matrix of cards in the given sort list
    as a nested dictionary mapping two sort names to the edit distance of the
    two sorts.
    """
    pairwise_distances = defaultdict(dict)
    for sort1 in sorts:
        for sort2 in sorts:
            distance = edit_distance(sort1, sort2)
            pairwise_distances[sort1][sort2] = distance
    return pairwise_distances


def find_neighbourhood(
        sort: Sort, sorts: Iterable[Sort], max_dist: int) -> set[Sort]:
    """
    Returns the d-neighbourhood of a sort as a list of sorts. The given sort
    may be a probe sort not included in the sorts list; however, the returned
    neighbourhood will not include the probe sort.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    return {s for s in sorts if edit_distance(sort, s) <= max_dist}


def _get_new_candidates(v, sorts, max_dist):
    clique_candidates = find_neighbourhood(v, sorts, max_dist)
    clique_candidates.discard(v)
    return clique_candidates


def _greedy_select(current_candidates, sorts, max_dist):
    max_pairs = []
    max_len = 0
    for v in current_candidates:
        new_candidates = _get_new_candidates(v, sorts, max_dist)
        new_candidates &= current_candidates
        candidate_size = len(new_candidates)
        if candidate_size > max_len:
            max_len = candidate_size
            max_pairs = [(v, new_candidates)]
        elif candidate_size == max_len:
            max_pairs.append((v, new_candidates))
    return max_pairs


def find_clique_random(sort: Sort,
                       sorts: Iterable[Sort],
                       max_dist: int) -> set[Sort]:
    """
    Returns the d-clique of a sort as a list of sorts using a random heuristic.
    The given sort may be a probe sort not included in the sorts list;
    however, the returned clique will not include the probe sort.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    clique = {sort} if sort in sorts else set()
    candidates = _get_new_candidates(sort, sorts, max_dist)
    while candidates:
        v = random.sample(candidates, 1)[0]
        clique.add(v)
        new_candidates = _get_new_candidates(sort, sorts, max_dist)
        candidates &= new_candidates
    return clique


def find_clique_greedy(sort: Sort,
                       sorts: Iterable[Sort],
                       max_dist: int) -> set[Sort]:
    """
    Returns the d-clique of a sort as a list of sorts using the greedy
    heuristic described by Deibel et al. The given sort may be a probe sort
    not included in the sorts list; however, the returned clique will not
    include the probe sort.

    **See:** Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit
    distance to analyze card sorts. Expert Systems, 22(3), 129-138.
    """
    clique = {sort} if sort in sorts else set()
    candidates = _get_new_candidates(sort, sorts, max_dist)
    while candidates:
        # In cases where several sorts satisfy the greedy rule,
        # one is chosen randomly
        best_candidates = _greedy_select(candidates, sorts, max_dist)
        v, candidates = random.choice(best_candidates)
        clique.add(v)
    return clique
