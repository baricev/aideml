"""Backend for DeepSeek API."""

import json
import logging
import os
import time

from .utils import FunctionSpec, OutputType, opt_messages_to_list, backoff_create
from funcy import notnone, once, select_values
import openai

logger = logging.getLogger("aide")

_client: openai.OpenAI = None  # type: ignore

DEEPSEEK_TIMEOUT_EXCEPTIONS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
)


@once
def _setup_deepseek_client():
    global _client
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is required")

    _client = openai.OpenAI(
        base_url="https://api.deepseek.com", api_key=api_key, max_retries=0
    )


def query(
    system_message: str | None,
    user_message: str | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> tuple[OutputType, float, int, int, dict]:
    """
    Query the DeepSeek API, optionally with function calling.
    If the model doesn't support function calling, gracefully degrade to text generation.
    """
    _setup_deepseek_client()
    filtered_kwargs: dict = select_values(notnone, model_kwargs)

    # Convert system/user messages to the format required by the client
    messages = opt_messages_to_list(system_message, user_message)

    # If function calling is requested, attach the function spec
    if func_spec is not None:
        filtered_kwargs["tools"] = [func_spec.as_openai_tool_dict]
        filtered_kwargs["tool_choice"] = func_spec.openai_tool_choice_dict

    t0 = time.time()

    # Attempt the API call
    try:
        response = backoff_create(
            _client.chat.completions.create,
            DEEPSEEK_TIMEOUT_EXCEPTIONS,
            messages=messages,
            **filtered_kwargs,
        )
    except openai.BadRequestError as e:
        # Check whether the error indicates that function calling is not supported
        if "function calling" in str(e).lower() or "tools" in str(e).lower():
            logger.warning(
                "Function calling was attempted but is not supported by this DeepSeek model. "
                "Falling back to plain text generation."
            )
            # Remove function-calling parameters and retry
            filtered_kwargs.pop("tools", None)
            filtered_kwargs.pop("tool_choice", None)

            # Retry without function calling
            response = backoff_create(
                _client.chat.completions.create,
                DEEPSEEK_TIMEOUT_EXCEPTIONS,
                messages=messages,
                **filtered_kwargs,
            )
        else:
            # If it's some other error, re-raise
            raise

    req_time = time.time() - t0

    # Parse the response
    choice = response.choices[0]
    message = choice.message

    # Handle tool calls if present
    if func_spec is not None and hasattr(message, "tool_calls") and message.tool_calls:
        tool_call = message.tool_calls[0]
        if tool_call.function.name == func_spec.name:
            try:
                output = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as ex:
                logger.error(
                    "Error decoding function arguments:\n"
                    f"{tool_call.function.arguments}"
                )
                raise ex
        else:
            # Function name mismatch
            logger.warning(
                f"Function name mismatch: expected {func_spec.name}, "
                f"got {tool_call.function.name}. Fallback to text."
            )
            output = message.content
    else:
        # No function call, use regular text output
        output = message.content

    in_tokens = response.usage.prompt_tokens
    out_tokens = response.usage.completion_tokens

    info = {
        "system_fingerprint": getattr(response, "system_fingerprint", None),
        "model": response.model,
        "created": getattr(response, "created", None),
    }

    return output, req_time, in_tokens, out_tokens, info
