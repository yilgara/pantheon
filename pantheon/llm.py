"""Provider-agnostic LLM client.

One factory builds a chat model from config, so the provider is a config/env
value — not a code change. Supports the common providers via LangChain; each
provider package is imported lazily so you only install the one you use.

Two tiers, mirroring the reference:
  - deep model  (deep_think_llm)  — for judges/managers that reason hard
  - quick model (quick_think_llm) — for analysts and debaters

Dev tip: set PANTHEON_LLM_PROVIDER=ollama (+ PANTHEON_LLM_BACKEND_URL) for free
local runs, or a free-tier provider, then switch to OpenAI/Anthropic for the demo.
"""

from __future__ import annotations

from typing import Any

from pantheon.config import get_config


def _build(provider: str, model: str, cfg: dict[str, Any]):
    provider = provider.lower()
    common = {"temperature": cfg["temperature"], "max_retries": cfg["llm_max_retries"]}
    base_url = cfg.get("backend_url")

    if provider in ("openai", "openai-compatible"):
        from langchain_openai import ChatOpenAI
        kwargs = {"model": model, **common}
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, **common)

    if provider in ("google", "google-genai", "gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model, temperature=cfg["temperature"])

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        kwargs = {"model": model, "temperature": cfg["temperature"]}
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOllama(**kwargs)

    raise ValueError(
        f"Unsupported llm_provider={provider!r}. "
        "Supported: openai, anthropic, google, ollama."
    )


def get_deep_llm(config: dict[str, Any] | None = None):
    """The heavier reasoning model (managers, judges)."""
    cfg = config or get_config()
    return _build(cfg["llm_provider"], cfg["deep_think_llm"], cfg)


def get_quick_llm(config: dict[str, Any] | None = None):
    """The cheaper/faster model (analysts, debaters)."""
    cfg = config or get_config()
    return _build(cfg["llm_provider"], cfg["quick_think_llm"], cfg)
