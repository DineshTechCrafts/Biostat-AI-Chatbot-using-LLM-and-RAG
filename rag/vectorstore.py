from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import chromadb


@dataclass(frozen=True)
class VectorStore:
    persist_dir: str
    collection_name: str

    def _client(self) -> chromadb.PersistentClient:
        return chromadb.PersistentClient(path=self.persist_dir)

    def get_collection(self):
        client = self._client()
        return client.get_or_create_collection(name=self.collection_name)

    def upsert(
        self,
        *,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
            raise ValueError("ids/documents/embeddings/metadatas must be same length")
        col = self.get_collection()
        col.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self,
        *,
        query_embedding: list[float],
        n_results: int = 6,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        col = self.get_collection()
        return col.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

    def iter_all_ids(self, batch_size: int = 2000) -> Iterable[str]:
        col = self.get_collection()
        offset = 0
        while True:
            got = col.get(include=[], limit=batch_size, offset=offset)
            ids = got.get("ids") or []
            if not ids:
                break
            for _id in ids:
                yield _id
            offset += len(ids)

