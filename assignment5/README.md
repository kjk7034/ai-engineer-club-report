# Movie Agent (완전한 에이전트 루프)

OpenAI `tools` 파라미터와 **완전한 에이전트 루프**를 갖춘 영화 에이전트입니다. 사용자 질문을 받아 → 어떤 도구를 호출할지 LLM이 결정 → 실제 영화 API 호출 → 결과를 다시 LLM에 전달 → **최종 답변이 나올 때까지 루프를 반복**합니다. 대화 기록을 메모리로 사용해 멀티턴 대화를 지원합니다.

## 과제 설명

- **API 기본 URL**: https://nomad-movies-2.nomadcoders.workers.dev
- **모델**: `gpt-4o-mini`

에이전트가 사용하는 3개의 도구 (모두 실제 API 호출):

| 도구 | 엔드포인트 | 설명 |
|---|---|---|
| `get_popular_movies()` | `/movies` | 현재 인기 영화 목록을 가져옵니다. |
| `get_movie_details(id)` | `/movies/:id` | 특정 영화의 상세 정보를 가져옵니다. |
| `get_similar_movies(id)` | `/movies/:id/similar` | 특정 영화와 비슷한 영화 목록을 가져옵니다. |

## 동작 방식 — 완전한 에이전트 루프

`assignment2`가 도구 호출 후 한 번만 응답을 받는 구조였다면, 여기서는 **최종 답변이 나올 때까지 반복**하는 점이 핵심입니다.

1. 사용자 메시지를 `messages`(메모리)에 추가합니다.
2. `tools` 파라미터와 함께 모델을 호출합니다. — 수동 프롬프팅이 아니라 OpenAI `tools` 스키마를 사용합니다.
3. 응답에 `tool_calls`가 있으면:
   - 모델의 호출 요청을 그대로 기록하고,
   - 실제 함수를 실행해 영화 API를 호출한 뒤,
   - 결과를 `role: "tool"` 메시지로 다시 넣고 **2번으로 돌아갑니다.**
4. 응답에 `tool_calls`가 없으면(= 최종 답변) 루프를 종료하고 답변을 반환합니다.

```
while step < MAX_STEPS:
    message = LLM(messages, tools=TOOLS)
    if not message.tool_calls:   # 최종 답변
        return message.content
    run_tool_calls(message)      # 실제 API 호출 후 결과를 messages에 추가 → 다시 루프
```

> `MAX_STEPS`(기본 5)는 무한 루프를 막는 안전장치입니다.

### 출력 형식

도구별로 답변 톤을 다르게 가져갑니다.

| 도구 | 출력 형식 |
|---|---|
| `get_popular_movies` | `제목 (ID: 숫자) - 평점: 숫자` 한 줄 리스트 |
| `get_similar_movies` | "OOO을 좋아하셨다면 이런 영화를 추천드립니다: A, B, C …" 추천 문장 |
| `get_movie_details` | 줄거리·장르·개봉연도·평점을 녹인 서술형 문단 |

## 실행 결과

```
Send a message... 지금 인기 있는 영화 알려줘

User: 지금 인기 있는 영화 알려줘
Agent: [get_popular_movies() 호출]
Agent: 현재 인기 있는 영화 목록은 다음과 같습니다:

1. Obsession (ID: 1339713) - 평점: 7.9
2. Peddi (ID: 1057265) - 평점: 6.8
3. The Unknown Man (ID: 879945) - 평점: 8.1
...

Send a message... Obsession에 대해 더 알려줘

User: Obsession에 대해 더 알려줘
Agent: [get_movie_details(1339713) 호출]
Agent: "Obsession"은 2026년 5월 13일에 개봉한 미국과 영국의 합작 호러·스릴러 영화로, 평점은 7.9입니다. 이 영화는 한 로맨티스트가 사랑을 얻기 위해 신비로운 "One Wish Willow"를 부수고, 그 소원 뒤에 숨겨진 어두운 대가를 깨닫게 되는 이야기를 다룹니다. ...

Send a message... 비슷한 영화 추천해 줄래?

User: 비슷한 영화 추천해 줄래?
Agent: [get_similar_movies(1339713) 호출]
Agent: "Obsession"을 좋아하셨다면 이런 영화를 추천드립니다: "A Nightmare on Elm Street," "The Silence of the Lambs," "Natural Born Killers" ... 이 영화들은 모두 긴장감 넘치는 호러·스릴러 요소를 가지고 있습니다.
```
