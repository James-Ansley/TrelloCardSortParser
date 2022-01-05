# Trello Card Sort Parser

This is a small set of scripts to help analyse card sort data and parse boards
from card sorts performed on Trello.

This isn't intended to be a whizzy-dizzy out-of-the-box solution, but rather a
set of tools and demonstration of methods to help with the process of analysing
card sorting data. Feel free to mosey around and pick out the functions that
might be of most use to you.

## Features

### Parsing Card Sorts

Trello Board json files can be parsed to create Sort objects. An example set of
card sorts can be found at https://trello.com/examplecardsort.

A [sort prototype][sort-prototype] board containing a single list of predefined
cards was constructed and copied for each individual sorting exercise. It is
important the sort prototype board is copied as this removes any list creation
and card actions which are used to set up the board. These actions are used to
interpret the time it takes for each participant to perform a sorting exercise
so these initial setup actions must be removed. However, this is only relevant
if this is the only method of timing sorts.

[sort-prototype]: https://trello.com/b/ekRIKOc1/sort-prototype

Each sort can then be downloaded as a json file and parsed using the
`parse_board` function in the `trello_parser` module. Convenience functions,
`parse_sorts_in_dir` and `get_paths_to_jsons_in_dir` to parse or get all json
files in a directory are also provided.

Sort IDs, Groups, and Cards are all parsed from the board json file. The Board
name is used for the sort ID.

An optional mapping from card prompts to card IDs can be provided. Using unique
tags to represent cards is often more useful and concise for item analysis.

### Item Analysis

The `sorts` module provides several functions to aid with the item analysis of
card sorts. It is important that sort IDs are unique as these are used to hash
and check equality between sorts. Card prompts or Card IDs should also be unique
as these are used to identify cards.

#### Edit Distance

The edit distance between two sorts can be calculated using the
`edit_distance` function[^1]. And the pairwise edit distance of a list of sorts
can be calculated using the `co_edit_distance` function which produces a nested
dictionary mapping two sorts to their respective edit distance.

[^1]: Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit distance to
analyze card sorts. Expert Systems, 22(3), 129-138.

#### Co-Occurrence

The co-occurrence matrix[^2] of two sorts can be calculated using the
`co_occurrence` function. Which produces the co-occurrence values scaled between
0 and 1 for each pair of cards. The matrix is represented as a nested dictionary
mapping two card IDs to their respective co-occurrence.

The co-occurrence distance matrix[^3] can be calculated using
the `co_occurrence_distance` function. Which produces the co-occurrence distance
values scaled between 0 and 1 for each pair of cards. The matrix is represented
as a nested dictionary.

[^2]: Kathy Baxter, Catherine Courage, and Kelly Caine. 2015. Chapter 11 - Card
Sorting. In Understanding your Users (Second Edition) (second edition ed.),
Kathy Baxter, Catherine Courage, and Kelly Caine (Eds.). Morgan Kaufmann,
Boston, 302–337. https://doi.org/10.1016/B978-0-12-800232-2.00011-0

[^3]: Tom Tullis and Bill Albert. 2013. Chapter 9 - Special Topics. In Measuring
the User Experience (Second Edition) (second edi ed.), Tom Tullis and Bill
Albert (Eds.). Morgan Kaufmann, Boston,
209–236. https://doi.org/10.1016/B978-0-12-415781-1.00009-1

#### Neighborhoods

d-neighborhoods[^1] of sorts can be calculated using the `find_neighbourhood`
function. The sort used as the center of the neighbourhood can be a probe sort
not in the set of sorts being analysed but will not be included in the resulting
neighbourhood.

#### Cliques

d-cliques[^1] of sorts can be calculated using the `find_clique_random` and
`find_clique_greedy` functions. The random algorithm randomly selects a sort to
add to the clique and the greedy algorithm selects the sort that reduces the
size of the set of possible sorts that can still be added to the clique by the
smallest amount.

The sort used as the center of the clique can be a probe sort not in the set of
sorts being analysed but will not be included in the resulting clique.
