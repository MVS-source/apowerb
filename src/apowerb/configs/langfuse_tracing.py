"""Send agent traces to Langfuse, when a Langfuse project is configured.

ADK already traces every invocation through OpenTelemetry — agent runs, model
calls with their token usage, tool calls — under the instrumentation scope
``gcp.vertex.agent``, on the global ``TracerProvider`` it installs when the
server starts. This module hangs Langfuse's span processor on that same
provider rather than adding a second instrumentation layer: one set of spans,
two possible destinations (the OTLP collector, if any, and Langfuse).

* **Opt-in.** Active only when ``LANGFUSE_PUBLIC_KEY``, ``LANGFUSE_SECRET_KEY``
  and ``LANGFUSE_HOST`` are all set. None of them: nothing happens. Some but
  not all: a warning naming the missing ones (never a value), then nothing.
* **Optional dependency.** The SDK is an extra (``apowerb[langfuse]``).
  Absent, the application boots and says what to install.
* **Never fatal.** Every path swallows its exception and says so.
* **Order matters.** Call it *after* ADK's startup. Called before, Langfuse
  would install the global provider itself and ADK's own would be refused,
  taking ADK's in-memory trace exporters (``/debug/trace``) with it.

``LANGFUSE_HOST`` must be reachable from the process, not from the operator's
machine. In a container, ``127.0.0.1`` is the container itself: a Langfuse
exposed on the host's loopback only (an SSH tunnel, for instance) needs
``network_mode: host``, or a listener on an address the container can route
to (``host.docker.internal`` resolves to the bridge gateway, not to the
host's loopback).

Langfuse v4 ingests OpenTelemetry only; its legacy ``/api/public/ingestion``
endpoint is refused. The v4 SDK exports over OTLP, so nothing here touches it.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from opentelemetry.sdk.trace import SpanProcessor

from apowerb.configs.th2logger import setup_logging

_logger = setup_logging(__name__)

_REQUIRED_VARS = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST")

# ADK's tracer scope. Its root ``invocation`` span carries no ``gen_ai.*``
# attribute, so Langfuse's default filter (Langfuse spans, GenAI spans, known
# LLM instrumentation scopes) would drop it and orphan every child span.
_ADK_SCOPE = "gcp.vertex.agent"

# ADK (2.9, both telemetry schemas) wraps every model call twice: a
# ``call_llm`` span carrying the request, the response and the token usage,
# and a ``generate_content {model}`` child carrying the same usage again.
# Langfuse types both as generations, so exporting both doubles the cost of
# every call. The child is dropped only while its ``call_llm`` parent exists:
# ADK plans to remove ``call_llm``, and ``generate_content`` must then remain.
_CALL_LLM = "call_llm"
_GENERATE_CONTENT = "generate_content"

_client: Any = None
_open_call_llm_spans: set[int] = set()


class _CallLlmTracker(SpanProcessor):
    """Span processor remembering which ADK ``call_llm`` spans are open.

    A child always ends before its parent, so when the export filter sees a
    ``generate_content`` span end, its ``call_llm`` parent is still here.
    """

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        if _is_adk(span) and span.name == _CALL_LLM:
            _open_call_llm_spans.add(span.context.span_id)

    def on_end(self, span: Any) -> None:
        if _is_adk(span) and span.name == _CALL_LLM:
            _open_call_llm_spans.discard(span.context.span_id)

    def shutdown(self) -> None:
        _open_call_llm_spans.clear()


def _is_adk(span: Any) -> bool:
    scope = getattr(span, "instrumentation_scope", None)
    return scope is not None and scope.name == _ADK_SCOPE


def _missing_vars() -> list[str]:
    return [name for name in _REQUIRED_VARS if not os.getenv(name, "").strip()]


def _export_filter(is_default_export_span: Callable[[Any], bool]) -> Callable[[Any], bool]:
    """Langfuse's default selection, plus every span ADK emits."""

    def should_export(span: Any) -> bool:
        if not _is_adk(span):
            return is_default_export_span(span)
        if span.name.startswith(_GENERATE_CONTENT):
            parent = getattr(span, "parent", None)
            return parent is None or parent.span_id not in _open_call_llm_spans
        return True

    return should_export


def enable_langfuse_tracing() -> bool:
    """Export ADK's spans to the configured Langfuse project.

    Returns ``True`` when the export is active, ``False`` when it is
    deliberately off (no configuration), incomplete, unavailable (extra not
    installed) or failed. Never raises.
    """
    global _client

    if _client is not None:
        return True

    missing = _missing_vars()
    if len(missing) == len(_REQUIRED_VARS):
        _logger.info("langfuse: not configured, agent traces are not sent to Langfuse")
        return False
    if missing:
        _logger.warning(
            "langfuse: incomplete configuration, missing %s; agent traces are "
            "NOT sent to Langfuse",
            ", ".join(missing),
        )
        return False

    try:
        from langfuse import Langfuse
        from langfuse.span_filter import is_default_export_span
    except ImportError:
        _logger.warning(
            "langfuse: LANGFUSE_* is set but the Langfuse SDK is not installed, "
            "so agent traces are NOT sent. Install the 'langfuse' extra."
        )
        return False

    host = os.environ["LANGFUSE_HOST"].strip()
    try:
        _client = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"].strip(),
            secret_key=os.environ["LANGFUSE_SECRET_KEY"].strip(),
            base_url=host,
            should_export_span=_export_filter(is_default_export_span),
        )
    except Exception as exc:  # noqa: BLE001 - booting matters more than telemetry
        _logger.warning("langfuse: client init failed, continuing: %s", exc)
        _client = None
        return False

    try:
        from opentelemetry import trace

        trace.get_tracer_provider().add_span_processor(_CallLlmTracker())
    except Exception as exc:  # noqa: BLE001 - duplicates beat no traces
        _logger.warning(
            "langfuse: cannot track model-call spans, each call may be "
            "counted twice: %s",
            exc,
        )

    _logger.info("langfuse: agent traces exported to %s", host)
    return True


def flush_langfuse_tracing() -> None:
    """Send what is buffered and stop the exporter. Never raises."""
    global _client

    if _client is None:
        return
    try:
        _client.shutdown()
    except Exception as exc:  # noqa: BLE001 - shutdown must not fail
        _logger.warning("langfuse: flush on shutdown failed: %s", exc)
    finally:
        _client = None


__all__ = ["enable_langfuse_tracing", "flush_langfuse_tracing"]
