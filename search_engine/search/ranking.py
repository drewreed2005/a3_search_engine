"""
ranking.py - functions for calculating TF-IDF scores and ordering results
"""

# for TF-IDF ranking, we use the very standard formula that i think was shown
# in lecture but was at least somewhere at some point:
#
#   with the following defined:
#       IDF(t) = ln(N / df(t))
#   where
#       N is the total number of indexed documents
#       df(t) is the number of documents containing term t
#
#   let:
#       TFIDF(t, d) = TF(t, d) x IDF(t)

# we can also weigh importance in ranking, since we store important term use
#
#   as a potential concept for how to do this, let:
#       TF_weighted(t, d) = TF(t, d) + (b - 1) x important_tf(t, d)
#   where b is an importance multiplier (which can be modified as seen fit)
#       (for example, b = 2 means an important text occurence contributes twice
#        as much as a normal occurrence)

# so for each matching document, the weighted TF-IDF scores of query terms
# can be summed, as in the following:
#       Score(d, q) = ∑_t∈q(TF_weighted(t, d) x IDF(t))
#   where qtf(t) is the number of times the term occurs in the original query
#       (allowing quantity of term occurrence in the original query to matter)



# the document on milestone 2 describes using cosine similarlity computation
# for ranking, which seems to involve measuring the angle between query and
# document vectors in a way that is both complex (and not yet taught) and also
# relies on document vector magnitude, which would need to be either calculated
# off of the existing index information or kept within the index itself through
# some modification to the indexer implementation
#
# i'm willing to do all of these things, but i'm not sure how much it would be
# wise to go off and attempt to learn on my own before the concepts are fully
# taught to us
#
# i may implement a document TF-IDF vector magnitude file calculated off of
# existing index data test the concept of using cosine ranking