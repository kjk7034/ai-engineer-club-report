import json
import urllib.error
import urllib.request

import dotenv
import openai
from openai.types.chat import ChatCompletionMessage

dotenv.load_dotenv()

BASE_URL = "https://nomad-movies-2.nomadcoders.workers.dev"

client = openai.OpenAI()
messages: list[dict] = []


def _fetch(path: str) -> str:
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"User-Agent": "movie-expert-agent/1.0"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.read().decode()
    except urllib.error.HTTPError as error:
        return json.dumps({"error": error.reason, "status": error.code})


def get_popular_movies() -> str:
    return _fetch("/movies")


def get_movie_details(id: int) -> str:
    return _fetch(f"/movies/{id}")


def get_movie_credits(id: int) -> str:
    return _fetch(f"/movies/{id}/credits")


FUNCTION_MAP = {
    "get_popular_movies": get_popular_movies,
    "get_movie_details": get_movie_details,
    "get_movie_credits": get_movie_credits,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_popular_movies",
            "description": "Fetch currently popular movies from the movie database.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_details",
            "description": "Fetch detailed information about a specific movie by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The numeric movie ID.",
                    }
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_credits",
            "description": "Fetch cast and crew credits for a specific movie by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The numeric movie ID.",
                    }
                },
                "required": ["id"],
            },
        },
    },
]


def process_ai_response(message: ChatCompletionMessage) -> None:
    if message.tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print(f"Calling function: {function_name} with {arguments}")

            try:
                parsed_arguments = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_arguments = {}

            function_to_run = FUNCTION_MAP.get(function_name)
            if function_to_run is None:
                result = json.dumps({"error": f"Unknown function: {function_name}"})
            else:
                result = function_to_run(**parsed_arguments)

            print(f"Ran {function_name} with args {parsed_arguments}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result,
                }
            )

        call_ai()
    else:
        messages.append({"role": "assistant", "content": message.content})
        print(f"AI: {message.content}")


def call_ai() -> None:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )
    process_ai_response(response.choices[0].message)


def ask(user_message: str) -> None:
    messages.append({"role": "user", "content": user_message})
    print(f"User: {user_message}")
    call_ai()


def run_tests() -> None:
    test_inputs = [
        "지금 인기 있는 영화가 무엇인지 알려줘",
        "movie ID 550에 해당하는 영화가 무엇인지 알려줘",
        "movie ID 550에 해당하는 영화에 누가 출연하는지 알려줘",
    ]

    for index, user_message in enumerate(test_inputs, start=1):
        print(f"\n=== Test {index} ===")
        ask(user_message)
        print()


def chat_loop() -> None:
    while True:
        user_message = input("Send a message to the LLM... ")
        if user_message in {"quit", "q"}:
            break
        ask(user_message)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_tests()
    else:
        chat_loop()
