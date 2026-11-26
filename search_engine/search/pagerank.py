# implementing this in the search engine temporarily for submission in Lecture 9 partial
# (this implementation will use elements of the posting structure that are not yet
#  implemented; just assume they exist for the purposes of submission)


# we assume the same "PageGraph" structure as was assumed for hits
# (may be different information representation in real implemented version
#  but we know the information will somehow be achievable during this process
#  so this feels unimportant enough to simplify in this way)


# for readability, let's be clear
DocID = int
PageGraph = dict[DocID, set[DocID]]
Scores = dict[DocID, float]

# same defaults/tolerance as for hits
# because i'm not totally sure the convention
DEFAULT_DAMPING_FACTOR = 0.85
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_PAGERANK_TOLERANCE = 1e-8


# assuming damping factor of 0.85 which matches lecture
# and although the formula shown in some of the slides does not
# use total number of pages N for normalization, other slides did
# and google shows it, so i'm going for it under the fair assumption
# that we'll easily access that information
def pagerank(
    graph: PageGraph,
    damping_factor: float = DEFAULT_DAMPING_FACTOR,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    tolerance: float = DEFAULT_PAGERANK_TOLERANCE
) -> Scores:
    # we could have this info without counting or anything
    num_pages: int = len(graph)
    # edge/default case
    if num_pages == 0:
        return {}
    
    # initializing every page with an equal share of pagerank
    initial_rank: float = 1.0 / num_pages
    scores: Scores = {
        doc_id: initial_rank for doc_id in graph
    }
    
    # only retaining links to documents in the graph
    # (this would be the sort of normalization filter needed
    #  and it could occur even before this step realistically)
    outgoing_links: PageGraph = {
        doc_id: {
            destination
            for destination in destinations
            if destination in graph
        }
        for doc_id, destinations in graph.items()
    }
    
    # iterating until we've hit the maximum number of allowed iterations
    for _ in range(max_iterations):
        new_scores: Scores = {
            doc_id: (1.0 - damping_factor) / num_pages
            for doc_id in graph
        }
        
        # collecting rank from dangling nodes and contirbuting
        # (distirbuting equally across pages)
        dangling_rank: float = sum(
            scores[doc_id]
            for doc_id, destinations in outgoing_links.items()
            if not destinations
        )
        dangling_contribution: float = (
            damping_factor * dangling_rank / num_pages
        )
        for doc_id in new_scores:
            new_scores[doc_id] += dangling_contribution
        
        # distributing rank through outgoing links
        for source, destinations in outgoing_links.items():
            if not destinations:
                continue
            
            # basic formula here
            contribution: float = (
                damping_factor * scores[source] / len(destinations)
            )
            
            for destination in destinations:
                new_scores[destination] += contribution
        
        # measuring the total change between iterations
        difference: float = sum(
            abs(new_scores[doc_id] - scores[doc_id])
            for doc_id in graph
        )
        # used for returning the right data and comparing difference
        scores = new_scores
        
        # breaking if we've hit tolerance
        if difference < tolerance:
            break
    
    return scores