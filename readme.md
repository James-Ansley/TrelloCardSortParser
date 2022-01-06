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

An example `main` module has been included to demonstrate the basic use of some
available functions.

#### Edit Distance

The edit distance between two sorts can be calculated using the
`edit_distance` function[^1]. And the pairwise edit distance of a list of sorts
can be calculated using the `co_edit_distance` function which produces a nested
dictionary mapping two sorts to their respective edit distance.

[^1]: Deibel, K., Anderson, R., & Anderson, R. (2005). Using edit distance to
analyze card sorts. Expert Systems, 22(3), 129-138.

#### Co-Occurrence

The co-occurrence matrix[^2] of two sorts can be calculated using the
`co_occurrence_matrix` function. Which produces the co-occurrence values scaled
between 0 and 1 for each pair of cards. The matrix is represented as a nested
dictionary mapping two card IDs to their respective co-occurrence.

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

#### Clustering

While most of the analysis has been done in Python, R scripts are used to
perform the Partitioning Around Medoids (PAM) and Hierarchical Clustering. This
is mostly because I do not trust Python implementations of these methods; it was
hard enough to find an implementation of the Hungarian algorithm that wasn't
completely broken so, I decided not to risk it with clustering.

##### Hierarchical Clustering

`hiearchical-clustering.R` reads in a co-occurrence distance matrix from a CSV
and produces a dendrogram of the resulting hierarchical clustering and produces
the clusters resulting from cutting the dendrogram at a specified number of
clusters.

##### Partitioning Around K-Medoids

`k-medoids-clustering.R` reads in a pairwise edit distance matrix from a CSV and
produces the resulting clusters from partitioning around k-medoids.

### Writing Data

Two helper functions are provided in the `pairwise_writer` module to help write
the results of the nested dictionary co-occurrence and pairwise edit distance
matrices to CSV files.

`write_pairs` will write a nested dictionary of type `dict[T, dict[T, V]]` to a
CSV file. For example:

```python
co_distance = co_occurrence_distance(sorts)
write_pairs(f, co_distance)
```

will write the co-occurrence distance matrix to the file `f`. The header row and
column of the resulting file will be the card IDs and the values will be the
co-occurrence distance floats.

`map_pairs` will map the headers (keys) and data (nested values) of a nested
dictionary to values using the `header` and `data` function parameters
respectively. By default, these functions map values to themselves. For example:

```python
pairwise_edit_distance = co_edit_distance(sorts)
pairs = map_pairs(pairwise_edit_distance, header=lambda s: s.id)
```

will map the sorts (headers/keys) of the nested dictionary of pairwise edit
distances (of type `dict[Sort, dict[Sort, int]]`) to their respective IDs. These
pairs can then be used to write the pairwise edit distance matrix to a CSV file
using `write_pairs` which will now use the sort IDs as headers.
