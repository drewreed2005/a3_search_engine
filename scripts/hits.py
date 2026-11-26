# implementing this in the search engine temporarily for submission in Lecture 9 partial
# (this implementation will use elements of the posting structure that are not yet
#  implemented; just assume they exist for the purposes of submission)


# let's say implementation assumes the index create some form of graph structure
# (like a "page graph" as described here)
# that connects pages to their associated linked other pages;
# it will likely not work exactly like this in my final implementation
# but it is a relatively minimal assumed structure that provides the needed info
#
# there will also have to be a step in resolution that occurs to determine the
# document IDs associated with the found hyperlinks, assuming they even exist

# so we will define within this page

from math import sqrt

# for readability, let's be clear
DocID = int
PageGraph = dict[DocID, set[DocID]]
Scores = dict[DocID, float]

DEFAULT_MAX_ITERATIONS = 50
DEFAULT_HITS_TOLERANCE = 1e-8


# (output ends up assuming the same structure; some info is just removed)
def get_incoming_links(graph: PageGraph) -> PageGraph:
    # initializing to all empty sets
    incoming_links: PageGraph = {doc_id: set() for doc_id in graph}
    
    # graph maps sources and their destinations, so we just
    # invert the representation and focus only on incoming links
    for source, destinations in graph.items():
        for destination in destinations:
            if destination in incoming_links:
                incoming_links[destination].add(source)
    
    return incoming_links


# google says L2 is the common "normalization" of a score like this
# (try literally looking up "common normalization of hits ranking")
# so i am using that here

# a_i = a_i / sqrt(Summation_j ((a_j)^2))
# h_i = h_i / sqrt(Summation_j ((h_j)^2))

def normalize_hits_scores(scores: Scores) -> Scores:
    # normalization uses a summation of all data
    # so it can be calculated and defined in this one place
    # (id associated with scores doesn't matter throughout this process)
    normalization: float = sqrt(sum(score ** 2 for score in scores.values()))
    
    # edge case: can't divide by 0
    if normalization == 0:
        return scores
    
    return {
        doc_id: score / normalization
        for doc_id, score in scores.items()
    }


# the core hits algorithm using this defined data
# (returns (hub_scores, authority_scores))
# (who knows if this tolerance is the right level for this?
#  we'll have to tune when i'm actually implementing)
def calculate_hits_scores(
        graph: PageGraph,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        tolerance: float = DEFAULT_HITS_TOLERANCE
    ) -> tuple[Scores, Scores]:
    incoming_links: PageGraph = get_incoming_links(graph)
    
    # initializing scores to 1 as instructed
    hub_scores: Scores = {
        doc_id: 1.0 for doc_id in graph
    }
    authority_scores: Scores = {
        doc_id: 1.0 for doc_id in graph
    }
    
    # iterating only as many times as allowed
    for _ in range(max_iterations):
        # calculating and normalizing immediately for authority
        new_authority: Scores = {
            doc_id: sum(
                hub_scores[source]
                for source in incoming_links[doc_id]
            )
            for doc_id in graph
        }
        new_authority = normalize_hits_scores(new_authority)
        # same for hub
        new_hub: Scores = {
            doc_id: sum(
                new_authority[destination]
                for destination in destinations
            )
            for doc_id, destinations in graph.items()
        }
        new_hub = normalize_hits_scores(new_hub)
        
        # using difference to determine if we should stop calculations now
        difference: float = (
            sum(abs(new_authority[doc_id] - authority_scores[doc_id])
                for doc_id in graph)
            +
            sum(abs(new_hub[doc_id] - hub_scores[doc_id])
                for doc_id in graph)
        )
        # we use these for difference comparison with the previous
        # (defined here so we return the right values)
        authority_scores = new_authority
        hub_scores = new_hub
        
        # we break out if the difference is no longer sufficiently meaningful
        # (we said this should be within 5 iterations in lecture but idk
        #  i just picked arbitrary default values)
        if difference < tolerance:
            break
    
    return hub_scores, authority_scores