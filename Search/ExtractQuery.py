from Classes.Query import Query
from Classes.Path import TopicDir, StopWordDir
import string
from nltk.stem import PorterStemmer


class ExtractQuery:
    def __init__(self):
        # 1. you should extract the 4 queries from the Path.TopicDir
        # 2. the query content of each topic should be 1) tokenized, 2) to lowercase, 3) remove stop words, 4) stemming
        # 3. you can simply pick up title only for query.
        self.__file = open(TopicDir, "r")
        self.__stopwords = [line.strip() for line in open(StopWordDir, "r")]
        self.__stemmer = PorterStemmer()
        return

    # Return extracted queries with class Query in a list.
    def getQuries(self):
        quries = []
        while line := self.__file.readline():
            if line.startswith("<top>"):
                q = Query()
                topicId = self.__file.readline().split(":")[1].strip()
                q.setTopicId(topicId)
                title = self.__file.readline().removeprefix("<title>").strip()
                q.setQueryContent(self.__prepare_content(title))
                quries.append(q)
        return quries

    def __prepare_content(self, content: str):
        """A function to tokenize, lowercase, remove stopwords, and stemming.
        return query:str"""
        translator = str.maketrans("", "", string.punctuation + string.digits)
        result = []
        for word in content.translate(translator).lower().split():
            if word not in self.__stopwords:
                result.append(self.__stemmer.stem(word, to_lowercase=False))
        return " ".join(result)
