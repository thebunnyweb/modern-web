# addons/redis_information_retrieval.py
class RedisVectorStore(InformationRetrieval):
    def __init__(
        self,
        text_field: str = "text",
        vector_field: str = "embedding",
        metadata_fields: tuple[str, ...] = ("title", "source", "page_id"),
    ) -> None:
        super().__init__()
        self.text_field = text_field
        self.vector_field = vector_field
        self.metadata_fields = metadata_fields
        self._r = None
        self._index = ""
        self._top_k = 5

    # unchanged except ↓↓↓ uses the variables above
    def connect(self, config: EndpointConfig) -> None:
        host = config.kwargs.get("host", "localhost")
        port = int(config.kwargs.get("port", 6379))
        pwd  = config.kwargs.get("password")
        self._index = config.kwargs.get("index_name", "glass_vector_index")
        self._top_k = int(config.kwargs.get("top_k", 5))

        self._r = redis.Redis(host=host, port=port, password=pwd)

    async def search(self, query: Text, tracker_state: Dict[Text, Any], threshold: float = 0.0):
        q_vec = self.embeddings.embed_query(query)

        q = (
            Query(f"*=>[KNN $K @{self.vector_field} $BLOB]")
            .return_fields(self.text_field, "__vec_score", *self.metadata_fields)
            .sort_by("__vec_score")
            .dialect(2)
        )
        params = {"K": self._top_k, "BLOB": vec_to_blob(q_vec)}
        res = self._r.ft(self._index).search(q, query_params=params)

        results = []
        for doc in res.docs:
            score = 1.0 - float(doc.__vec_score)
            if score >= threshold:
                meta = {f: getattr(doc, f, "") for f in self.metadata_fields}
                results.append(SearchResult(text=getattr(doc, self.text_field), metadata=meta, score=score))

        return SearchResultList(results=results, metadata={})