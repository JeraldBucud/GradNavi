"""
Provider-independent embedding contract for GradNavi.

Semantic AI features use this boundary instead of importing a concrete
external provider directly.

The contract supports batches so multiple Career contexts can be embedded
in one provider request while preserving input order.
"""

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable


@dataclass(frozen=True)
class EmbeddingBatchResult:
    """
    Normalized result returned by a GradNavi embedding provider.

    vectors
        One embedding vector for each supplied input text.

    model
        Provider model identifier used for the request.

    prompt_tokens
        Input tokens reported by the provider.

    total_tokens
        Total tokens reported by the provider.
    """

    vectors: tuple[
        tuple[float, ...],
        ...
    ]

    model: str

    prompt_tokens: int
    total_tokens: int

    @property
    def vector_count(self) -> int:
        """
        Number of returned embedding vectors.
        """

        return len(
            self.vectors
        )

    @property
    def dimensions(self) -> int | None:
        """
        Embedding dimensions when vectors exist.
        """

        if not self.vectors:
            return None

        return len(
            self.vectors[0]
        )


@runtime_checkable
class EmbeddingProvider(Protocol):
    """
    Provider-independent contract for semantic embeddings.
    """

    def embed_texts(
        self,
        *,
        texts: Sequence[str],
    ) -> EmbeddingBatchResult:
        """
        Embed one or more texts while preserving input order.
        """
        ...
