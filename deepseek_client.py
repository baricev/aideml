import argparse
import json
import os
import sys
import requests


class DeepSeekClient:
    """
    A standalone client for the DeepSeek API.
    """

    def __init__(self, api_key, model, temperature, max_tokens, base_url):
        """
        Initializes the DeepSeekClient.

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
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url.rstrip("/") + "/chat/completions"

    def _make_request(self, messages):
        """
        Makes a request to the DeepSeek API.

        Args:
            messages (list): A list of message objects.

        Returns:
            str: The content of the response from the API.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}", file=sys.stderr)
            sys.exit(1)
        except (KeyError, IndexError) as e:
            print(f"Error parsing API response: {e}", file=sys.stderr)
            sys.exit(1)

    def complete(self, prompt):
        """
        Provides a single completion for a given prompt.

        Args:
            prompt (str): The prompt to complete.

        Returns:
            str: The completed text.
        """
        messages = [{"role": "user", "content": prompt}]
        return self._make_request(messages)

    def chat(self, messages):
        """
        Handles a multi-turn chat conversation.

        Args:
            messages (list): A list of message objects representing the conversation.

        Returns:
            str: The next message in the chat.
        """
        return self._make_request(messages)


def main():
    """
    Main function to handle command-line arguments and execute the client.
    """
    parser = argparse.ArgumentParser(
        description="A standalone client for the DeepSeek API."
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

    args = parser.parse_args()

    try:
        client = DeepSeekClient(
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

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
