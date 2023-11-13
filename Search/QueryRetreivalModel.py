from Classes.Query import Query
from Classes.Document import Document
from IndexingWithWhoosh.MyIndexReader import MyIndexReader
from math import prod


class QueryRetrievalModel:
    indexReader = []

    def __init__(self, ixReader: MyIndexReader):
        self.indexReader = ixReader
        self.collection_len = self.indexReader.searcher.reader().field_length(
            "doc_content"
        )  # get the word count in the index
        return

    # query:  The query to be searched for.
    # topN: The maximum number of returned documents.
    # The returned results (retrieved documents) should be ranked by the score (from the most relevant to the least).
    # You will find our IndexingLucene.Myindexreader provides method: docLength().
    # Returned documents should be a list of Document.
    def retrieveQuery(self, query: Query, topN):
        words = set(query.getQueryContent().split())
        posts = set()
        wordsPostingList: dict[str, dict] = {}
        pmles: dict[str, dict] = {}
        for word in words:
            wordsPostingList[word] = self.indexReader.getPostingList(word)
            posts.update(wordsPostingList[word].keys())  # save the docId to a set
            pmles[word] = (
                self.indexReader.CollectionFreq(word) / self.collection_len
            )  # Prob of MLE of a word
        ranks = []
        mu = 2000
        for post in posts:
            wordProbs = []
            docLength = self.indexReader.getDocLength(post)
            for word in words:
                prob = (
                    # In Professor Chengxiang Zhai’s work in SIGIR 2001: A Study of Smoothing Methods for Language Models.
                    # prob will be the equation below if a word is unseen
                    (mu / (docLength + mu)) * pmles[word]
                    if (freq := wordsPostingList[word].get(post)) is None
                    else (docLength / (docLength + mu)) * (freq / docLength)
                    + (mu / (docLength + mu)) * pmles[word]
                )
                # Skip words with prob equals 0 since we don't have a fallback model.
                if prob == 0:
                    continue
                wordProbs.append(prob)
            ranks.append((prod(wordProbs), post))
        ranks.sort(reverse=True)
        results = []
        for score, docId in ranks[:topN]:
            d = Document()
            d.setDocId(docId)
            d.setDocNo(self.indexReader.getDocNo(docId))
            d.setScore(score)
            results.append(d)
        assert len(results) == topN
        return results
