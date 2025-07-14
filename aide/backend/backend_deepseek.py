"""Backend for DeepSeek API using the llama-index client."""

import json
import logging
import os
import time

from .utils import FunctionSpec, OutputType, opt_messages_to_list
from funcy import notnone, select_values
from llama_index.core.base.llms.types import ChatMessage
from llama_index.llms.deepseek import DeepSeek

logger = logging.getLogger("aide")

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"


def query(
    system_message: str | None,
    user_message: str | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> tuple[OutputType, float, int, int, dict]:
    """Query the DeepSeek API, optionally with function calling."""

    filtered_kwargs: dict = select_values(notnone, model_kwargs)
    api_key = os.getenv("DEEPSEEK_API_KEY")

    model_name = filtered_kwargs.pop("model", "deepseek-chat")
    llm = DeepSeek(model=model_name, api_key=api_key, api_base=DEFAULT_BASE_URL)

    # Convert system/user messages to llama-index ChatMessage objects
    messages = [
        ChatMessage.from_str(m["content"], role=m["role"])
        for m in opt_messages_to_list(system_message, user_message)
    ]

    if func_spec is not None:
        filtered_kwargs["tools"] = [func_spec.as_openai_tool_dict]
        filtered_kwargs["tool_choice"] = func_spec.openai_tool_choice_dict

    t0 = time.time()
    response = llm.chat(messages, **filtered_kwargs)
    req_time = time.time() - t0

    message = response.message
    output: OutputType = message.content

    # Handle function call outputs if present
    if func_spec is not None:
        fc_info = message.additional_kwargs.get("tool_calls") or message.additional_kwargs.get(
            "function_call"
        )
        if fc_info:
            if isinstance(fc_info, list):
                fc = fc_info[0].get("function", {})
            else:
                fc = fc_info

            if fc.get("name") == func_spec.name:
                try:
                    output = json.loads(fc.get("arguments", "{}"))
                except json.JSONDecodeError as ex:
                    logger.error(
                        "Error decoding function arguments:\n" f"{fc.get('arguments')}"
                    )
                    raise ex
            else:
                logger.warning(
                    f"Function name mismatch: expected {func_spec.name}, got {fc.get('name')}. Fallback to text."
                )

    usage = getattr(response.raw, "usage", None)
    if usage is None:
        in_tokens = out_tokens = 0
    else:
        in_tokens = getattr(usage, "prompt_tokens", usage.get("prompt_tokens", 0))
        out_tokens = getattr(usage, "completion_tokens", usage.get("completion_tokens", 0))

    info = {
        "system_fingerprint": getattr(response.raw, "system_fingerprint", None),
        "model": model_name,
        "created": getattr(response.raw, "created", None),
    }

    return output, req_time, in_tokens, out_tokens, info
