import argparse
import json
import os
import sys

from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.llms import ChatMessage


class DeepSeekClientLlama:
    """
    A standalone client for the DeepSeek API using the llama_index library.
    """

    def __init__(self, api_key, model, temperature, max_tokens, base_url):
        """
        Initializes the DeepSeekClientLlama.

        Args:
            api_key (str): The DeepSeek API key.
            model (str): The model to use for completion.
            temperature (float): The generation temperature.
            max_tokens (int): The maximum number of tokens to generate.
            base_url (str): The base URL for the API.
        """
        if api_key is None:
            raise ValueError(
                "API key is not provided. Please set the DEEPSEEK_API_KEY environment variable or use the --api-key argument."
            )

        try:
            self.llm = DeepSeek(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_base=base_url,
            )
        except ImportError as e:
            print(
                f"Error: llama-index is not installed. Please install it with 'pip install llama-index-llms-deepseek'",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing DeepSeek from llama-index: {e}", file=sys.stderr)
            sys.exit(1)

    def complete(self, prompt: str) -> str:
        """
        Provides a single completion for a given prompt using llm.complete().

        Args:
            prompt (str): The prompt to complete.

        Returns:
            str: The completed text.
        """
        try:
            response = self.llm.complete(prompt)
            return response.text
        except Exception as e:
            print(f"Error during 'complete' call: {e}", file=sys.stderr)
            sys.exit(1)

    def chat(self, messages: list[dict]) -> str:
        """
        Handles a multi-turn chat conversation using llm.chat().

        Args:
            messages (list[dict]): A list of message dictionaries, e.g., [{"role": "user", "content": "..."}].

        Returns:
            str: The next message in the chat.
        """
        try:
            chat_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            response = self.llm.chat(chat_messages)
            return response.message.content
        except Exception as e:
            print(f"Error during 'chat' call: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """
    Main function to handle command-line arguments and execute the client.
    """
    parser = argparse.ArgumentParser(
        description="A standalone client for the DeepSeek API using llama-index."
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("DEEPSEEK_API_KEY"),
        help="The DeepSeek API key. Defaults to the DEEPSEEK_API_KEY environment variable.",
    )
    parser.add_argument("--model", default="deepseek-chat", help="The model to use.")
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="The generation temperature."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="The maximum number of tokens to generate.",
    )
    parser.add_argument(
        "--base-url",
        default="https://api.deepseek.com/v1",
        help="The base URL for the API.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command for 'complete'
    complete_parser = subparsers.add_parser(
        "complete", help="Get a single completion for a prompt."
    )
    complete_parser.add_argument(
        "--prompt", required=True, help="The prompt to send to the model."
    )

    # Sub-command for 'chat'
    chat_parser = subparsers.add_parser(
        "chat", help="Have a multi-turn chat session. Reads messages from stdin."
    )

    # Sub-command for 'smoke-test'
    smoke_test_parser = subparsers.add_parser(
        "smoke-test", help="Run a smoke test to check API connectivity."
    )

    args = parser.parse_args()

    try:
        client = DeepSeekClientLlama(
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            base_url=args.base_url,
        )

        if args.command == "complete":
            result = client.complete(args.prompt)
            print(result)
        elif args.command == "chat":
            try:
                messages = json.load(sys.stdin)
                if not isinstance(messages, list):
                    raise ValueError("Input must be a JSON array of message objects.")
            except json.JSONDecodeError:
                print("Error: Invalid JSON received from stdin.", file=sys.stderr)
                sys.exit(1)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

            result = client.chat(messages)
            print(result)
        elif args.command == "smoke-test":
            prompt = "Hello, world!"
            print(f"Running smoke test with prompt: '{prompt}'")
            result = client.complete(prompt)
            print("Result:")
            print(result)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
