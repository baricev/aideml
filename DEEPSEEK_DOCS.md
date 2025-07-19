# DeepSeek documentation excerpts:

### **Source: https://api-docs.deepseek.com/api/create-chat-completion/**

Skip to main content
English
DeepSeek Platform

API ReferenceChatCreate Chat Completion
Create Chat Completion
POST
https://api.deepseek.com/chat/completions
Creates a model response for the given chat conversation.

Request
application/json
Body

required

messages

object[]

required

model
string
required
Possible values: [deepseek-chat, deepseek-reasoner]

ID of the model to use. You can use deepseek-chat.

frequency_penalty
number
nullable
Possible values: >= -2 and <= 2

Default value: 0

Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.

max_tokens
integer
nullable
Possible values: > 1

Integer between 1 and 8192. The maximum number of tokens that can be generated in the chat completion.

The total length of input tokens and generated tokens is limited by the model's context length.

If max_tokens is not specified, the default value 4096 is used.

presence_penalty
number
nullable
Possible values: >= -2 and <= 2

Default value: 0

Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.

response_format

object

nullable

stop

object

nullable

stream
boolean
nullable
If set, partial message deltas will be sent. Tokens will be sent as data-only server-sent events (SSE) as they become available, with the stream terminated by a data: [DONE] message.

stream_options

object

nullable

temperature
number
nullable
Possible values: <= 2

Default value: 1

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

We generally recommend altering this or top_p but not both.

top_p
number
nullable
Possible values: <= 1

Default value: 1

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

tools

object[]

nullable

tool_choice

object

nullable

logprobs
boolean
nullable
Whether to return log probabilities of the output tokens or not. If true, returns the log probabilities of each output token returned in the content of message.

top_logprobs
integer
nullable
Possible values: <= 20

An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability. logprobs must be set to true if this parameter is used.

Responses
200 (No streaming)
200 (Streaming)
OK, returns a chat completion object

application/json
Schema
Example (from schema)
Example
{
  "id": "string",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "string",
        "reasoning_content": "string",
        "tool_calls": [
          {
            "id": "string",
            "type": "function",
            "function": {
              "name": "string",
              "arguments": "string"
            }
          }
        ],
        "role": "assistant"
      },
      "logprobs": {
        "content": [
          {
            "token": "string",
            "logprob": 0,
            "bytes": [
              0
            ],
            "top_logprobs": [
              {
                "token": "string",
                "logprob": 0,
                "bytes": [
                  0
                ]
              }
            ]
          }
        ]
      }
    }
  ],
  "created": 0,
  "model": "string",
  "system_fingerprint": "string",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 0,
    "prompt_tokens": 0,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 0,
    "total_tokens": 0,
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}

curl
python
go
nodejs
ruby
csharp
php
java
powershell
OpenAI SDK
from openai import OpenAI

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="<your API key>", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
  ],
    max_tokens=1024,
    temperature=0.7,
    stream=False
)

print(response.choices[0].message.content)


REQUESTS
HTTP.CLIENT
import requests
import json

url = "https://api.deepseek.com/chat/completions"

payload = json.dumps({
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "frequency_penalty": 0,
  "max_tokens": 2048,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": None,
  "stream": False,
  "stream_options": None,
  "temperature": 1,
  "top_p": 1,
  "tools": None,
  "tool_choice": "none",
  "logprobs": False,
  "top_logprobs": None
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)


Request
Collapse all
Base URL
https://api.deepseek.com
Auth
Bearer Token
Bearer Token
Body
 required
{
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "frequency_penalty": 0,
  "max_tokens": 2048,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": null,
  "stream": false,
  "stream_options": null,
  "temperature": 1,
  "top_p": 1,
  "tools": null,
  "tool_choice": "none",
  "logprobs": false,
  "top_logprobs": null
}
Send API Request
Response
Clear
Click the Send API Request button above and see the response here!

Previous
Introduction
Next
Create FIM Completion (Beta)

---

### **Source: https://api-docs.deepseek.com/guides/function_calling**

Function Calling
Function Calling allows the model to call external tools to enhance its capabilities.

Sample Code
Here is an example of using Function Calling to get the current weather information of the user's location, demonstrated with complete Python code.

For the specific API format of Function Calling, please refer to the Chat Completion documentation.

from openai import OpenAI

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou?"}]
message = send_messages(messages)
print(f"User>\t {messages[0]['content']}")

tool = message.tool_calls[0]
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
message = send_messages(messages)
print(f"Model>\t {message.content}")


The execution flow of this example is as follows:

User: Asks about the current weather in Hangzhou
Model: Returns the function get_weather({location: 'Hangzhou'})
User: Calls the function get_weather({location: 'Hangzhou'}) and provides the result to the model
Model: Returns in natural language, "The current temperature in Hangzhou is 24°C."
Note: In the above code, the functionality of the get_weather function needs to be provided by the user. The model itself does not execute specific functions.


