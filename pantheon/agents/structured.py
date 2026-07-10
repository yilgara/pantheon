"""Structured-output helpers.

Wrap an LLM for structured output, and invoke with a graceful plain-text
fallback if the provider/model can't produce a valid schema instance.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


def bind_structured(llm: Any, schema: type, agent_name: str):
    """Return llm.with_structured_output(schema), or None if unsupported."""
    try:
        return llm.with_structured_output(schema)
    except (NotImplementedError, AttributeError):
        logger.warning("%s: provider lacks structured output; will use free text", agent_name)
        return None


def invoke_structured_or_freetext(
    structured_llm: Any | None,
    plain_llm: Any,
    prompt: Any,
    render: Callable[[T], str],
    agent_name: str,
) -> str:
    """Try structured; on any failure fall back to a plain-text LLM call."""
    if structured_llm is not None:
        try:
            result = structured_llm.invoke(prompt)
            if result is None:
                raise ValueError("structured output returned nothing")
            return render(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("%s: structured invoke failed (%s); retrying as free text", agent_name, exc)
    return plain_llm.invoke(prompt).content
