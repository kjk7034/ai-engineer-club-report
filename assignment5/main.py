import json
import urllib.error
import urllib.request

import dotenv
import openai
from openai.types.chat import ChatCompletionMessage

dotenv.load_dotenv()

BASE_URL = "https://nomad-movies-2.nomadcoders.workers.dev"
MODEL = "gpt-4o-mini"
MAX_STEPS = 5  # 무한 루프 방지용 안전장치

SYSTEM_PROMPT = """\
당신은 영화 전문가 에이전트입니다. 모든 답변은 한국어로 합니다.

사용 가능한 도구:
- get_popular_movies: 현재 인기 영화 목록을 가져온다.
- get_movie_details(id): 특정 영화의 상세 정보를 가져온다.
- get_similar_movies(id): 특정 영화와 비슷한 영화 목록을 가져온다.

규칙:
- 사용자가 특정 영화를 언급하면, 앞선 대화에서 파악한 영화 ID를 활용한다.
- 영화 ID를 모르면 먼저 get_popular_movies로 목록을 확인해 ID를 찾는다.

출력 형식:
- 인기 영화 목록(get_popular_movies)은 각 항목을 "제목 (ID: 숫자) - 평점: 숫자" 한 줄로만 간결하게 보여준다. 줄거리와 포스터 이미지는 넣지 않는다.
- 비슷한 영화(get_similar_movies)는 목록을 나열하지 말고 추천 문장으로 풀어 쓴다. 예: "OOO을 좋아하셨다면 이런 영화를 추천드립니다: 제목A, 제목B, 제목C ..." 처럼 자연스럽게 제목을 이어서 소개한다.
- 사용자가 특정 영화 "한 편"의 상세 정보를 물으면(get_movie_details), 키-값 목록을 나열하지 말고 자연스러운 한국어 문장으로 풀어서 설명한다. 예: "Obsession은 2026년 개봉한 미국·영국 합작 호러·스릴러 영화로, 평점은 7.9입니다. 이야기는 ... 입니다." 처럼 줄거리·장르·개봉연도·평점 등을 문단형으로 녹여 쓴다.
"""

client = openai.OpenAI()

# 대화 기록 = 에이전트의 메모리. 멀티턴 동안 계속 누적된다.
messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]


# --------------------------------------------------------------------------- #
# 실제 API 호출 도구
# --------------------------------------------------------------------------- #
def _fetch(path: str) -> str:
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"User-Agent": "movie-agent/1.0"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.read().decode()
    except urllib.error.HTTPError as error:
        return json.dumps({"error": error.reason, "status": error.code})


def get_popular_movies() -> str:
    """GET /movies — 현재 인기 영화 목록."""
    return _fetch("/movies")


def get_movie_details(id: int) -> str:
    """GET /movies/:id — 특정 영화 상세 정보."""
    return _fetch(f"/movies/{id}")


def get_similar_movies(id: int) -> str:
    """GET /movies/:id/similar — 비슷한 영화 목록."""
    return _fetch(f"/movies/{id}/similar")


FUNCTION_MAP = {
    "get_popular_movies": get_popular_movies,
    "get_movie_details": get_movie_details,
    "get_similar_movies": get_similar_movies,
}

# OpenAI tools 파라미터 (수동 프롬프팅이 아닌 tools 스키마 사용)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_popular_movies",
            "description": "현재 인기 있는 영화 목록을 가져온다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_details",
            "description": "특정 영화의 상세 정보(줄거리, 개봉일, 평점 등)를 ID로 가져온다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "영화의 숫자 ID."}
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_similar_movies",
            "description": "특정 영화와 비슷한 영화 목록을 ID로 가져온다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "기준이 되는 영화의 숫자 ID."}
                },
                "required": ["id"],
            },
        },
    },
]


# --------------------------------------------------------------------------- #
# 에이전트 루프
# --------------------------------------------------------------------------- #
def _run_tool_calls(message: ChatCompletionMessage) -> None:
    """모델이 요청한 tool_calls를 실제로 실행하고 결과를 messages에 추가한다."""
    # 1. 모델의 tool_calls 요청을 그대로 기록 (tool 결과와 짝을 맞추기 위함).
    messages.append(
        {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        }
    )

    # 2. 각 tool_call에 대해 실제 함수를 실행하고 결과를 반환한다.
    for call in message.tool_calls:
        name = call.function.name
        try:
            arguments = json.loads(call.function.arguments)
        except json.JSONDecodeError:
            arguments = {}

        arg_str = ", ".join(str(value) for value in arguments.values())
        print(f"Agent: [{name}({arg_str}) 호출]")

        function = FUNCTION_MAP.get(name)
        if function is None:
            result = json.dumps({"error": f"Unknown function: {name}"})
        else:
            result = function(**arguments)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": name,
                "content": result,
            }
        )


def ask(user_message: str) -> str:
    """사용자 질문을 받아 최종 답변이 나올 때까지 에이전트 루프를 돈다."""
    messages.append({"role": "user", "content": user_message})
    print(f"\nUser: {user_message}")

    for _ in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        message = response.choices[0].message

        # 도구 호출이 없으면 최종 답변 -> 루프 종료.
        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content})
            print(f"Agent: {message.content}")
            return message.content

        # 도구 호출이 있으면 실행하고 결과를 넣은 뒤 루프를 계속한다.
        _run_tool_calls(message)

    fallback = "죄송합니다. 답변을 정리하지 못했습니다. 다시 질문해 주세요."
    messages.append({"role": "assistant", "content": fallback})
    print(f"Agent: {fallback}")
    return fallback


# --------------------------------------------------------------------------- #
# 실행 진입점
# --------------------------------------------------------------------------- #
def chat_loop() -> None:
    """대화형 모드. quit/q 입력 시 종료."""
    print("Movie Agent에 오신 것을 환영합니다. (종료: quit / q)")
    while True:
        user_message = input("\nSend a message... ")
        if user_message.strip().lower() in {"quit", "q"}:
            break
        ask(user_message)


if __name__ == "__main__":
    chat_loop()
