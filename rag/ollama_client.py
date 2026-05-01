from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class Ollama:
    host: str

    def _url(self, path: str) -> str:
        return f"{self.host.rstrip('/')}{path}"

    def embeddings(self, *, model: str, prompt: str) -> list[float]:
        r = requests.post(
            self._url("/api/embeddings"),
            json={"model": model, "prompt": prompt},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        emb = data.get("embedding")
        if not isinstance(emb, list) or not emb:
            raise RuntimeError(f"Unexpected embeddings response: {data}")
        return [float(x) for x in emb]

    def embed_many(self, *, model: str, inputs: list[str]) -> list[list[float]]:
        if not inputs:
            return []
        r = requests.post(
            self._url("/api/embed"),
            json={"model": model, "input": inputs},
            timeout=300,
        )
        r.raise_for_status()
        data = r.json()
        embs = data.get("embeddings")
        if not isinstance(embs, list) or not embs:
            raise RuntimeError(f"Unexpected embed-many response: {data}")
        out: list[list[float]] = []
        for emb in embs:
            if not isinstance(emb, list) or not emb:
                raise RuntimeError(f"Invalid embedding item in response: {data}")
            out.append([float(x) for x in emb])
        return out

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        r = requests.post(
            self._url("/api/generate"),
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=300,
        )
        r.raise_for_status()
        data: dict[str, Any] = r.json()
        resp = data.get("response")
        if not isinstance(resp, str):
            raise RuntimeError(f"Unexpected generate response: {data}")
        return resp.strip()

