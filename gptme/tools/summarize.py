import logging
from functools import lru_cache

from ..llm import summarize as _summarize
from ..message import Message, format_msgs
from ..util import len_tokens

logger = logging.getLogger(__name__)


def summarize(msg: Message | list[Message]) -> Message:
    """Uses a cheap LLM to summarize long outputs."""
    # construct plaintext from message(s)
    msgs = msg if isinstance(msg, list) else [msg]
    content = "\n".join(format_msgs(msgs))
    summary = _summarize_helper(content)
    # construct message from summary
    summary_msg = Message(
        role="system", content=f"Summary of the conversation:\n{summary})"
    )
    return summary_msg


@lru_cache(maxsize=128)
def _summarize_helper(s: str, tok_max_start=500, tok_max_end=500) -> str:
    """
    Helper function for summarizing long outputs.

    Trims long outputs to 200 tokens, then summarizes.
    """
    if len_tokens(s) > tok_max_start + tok_max_end:
        beginning = " ".join(s.split()[:tok_max_start])
        end = " ".join(s.split()[-tok_max_end:])
        summary = _summarize(beginning + "\n...\n" + end)
    else:
        summary = _summarize(s)
    return summary
