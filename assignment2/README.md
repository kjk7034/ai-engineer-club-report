# Movie Expert Agent

OpenAI Function Calling을 활용한 영화 전문가 에이전트입니다. 사용자의 자연어 질문을 이해하고, 실제 영화 API를 호출해 답변합니다.

## 과제 설명

OpenAI 클라이언트와 실제 영화 API를 사용하여 Movie Expert Agent를 구축합니다.

- **API 기본 URL**: https://nomad-movies-2.nomadcoders.workers.dev/
- **모델**: `gpt-4o-mini`

에이전트는 다음 3가지 함수를 알고 있으며, 사용자 입력에 따라 올바른 함수를 선택해 호출합니다.

| 함수 | 엔드포인트 | 설명 |
|---|---|---|
| `get_popular_movies()` | `/movies` | 인기 영화 목록을 가져옵니다. |
| `get_movie_details(id)` | `/movies/:id` | 특정 영화의 상세 정보를 가져옵니다. |
| `get_movie_credits(id)` | `/movies/:id/credits` | 특정 영화의 출연진 및 제작진을 가져옵니다. |

### 동작 방식

1. 사용자 메시지를 받아 `gpt-4o-mini`에 전달합니다.
2. 모델이 `TOOLS`에 정의된 함수 설명을 보고 호출할 함수명과 인자(arguments)를 결정합니다.
3. 해당 함수를 실행해 영화 API를 호출하고, 결과를 다시 모델에 전달합니다.
4. 모델이 결과를 바탕으로 사용자에게 최종 답변을 생성합니다.

## 사전 준비

레포 루트에 `.env` 파일을 만들고 OpenAI API 키를 설정합니다.

```env
OPENAI_API_KEY=sk-...
```

> `dotenv.load_dotenv()`가 상위 디렉토리까지 탐색하므로, `.env`는 레포 루트에 두어도 됩니다.

## 설치

[uv](https://docs.astral.sh/uv/)로 의존성을 설치합니다.

```bash
cd assignment2
uv sync
```

## 실행 방법

### 1. 테스트 모드

과제에서 요구하는 3가지 입력을 자동으로 실행합니다.

```bash
cd assignment2
uv run python main.py test
# 또는 venv를 직접 사용
./.venv/bin/python main.py test
```

테스트 입력:

- `"지금 인기 있는 영화가 무엇인지 알려줘"` → `get_popular_movies()`
- `"movie ID 550에 해당하는 영화가 무엇인지 알려줘"` → `get_movie_details(id=550)`
- `"movie ID 550에 해당하는 영화에 누가 출연하는지 알려줘"` → `get_movie_credits(id=550)`

### 2. 대화형 모드

인자 없이 실행하면 직접 메시지를 입력할 수 있습니다. (`quit` 또는 `q` 입력 시 종료)

```bash
cd assignment2
uv run python main.py
```

## 실행 예시

```
=== Test 2 ===
User: movie ID 550에 해당하는 영화가 무엇인지 알려줘
Calling function: get_movie_details with {"id":550}
Ran get_movie_details with args {'id': 550}
AI: 영화 ID 550에 해당하는 영화는 **Fight Club**입니다.
...
```

`Calling function:` 로그를 통해 모델이 사용자 입력에 따라 올바른 함수명과 인자를 출력하는 것을 확인할 수 있습니다.

## 파일 구조

- `main.py` — 에이전트 구현 (함수 정의, 툴 스키마, 호출 루프)
- `pyproject.toml` — 프로젝트 메타데이터 및 의존성

## 결과

```
Send a message to the LLM... 지금 인기 있는 영화가 무엇인지 알려줘
User: 지금 인기 있는 영화가 무엇인지 알려줘
Calling function: get_popular_movies with {}
Ran get_popular_movies with args {}
AI: 현재 인기 있는 영화 목록은 다음과 같습니다:

1. **Obsession**
   - **개요**: 사랑하는 사람의 마음을 얻기 위해 신비로운 "원 위시 윌로우"를 깨트린 절망적인 로맨티스트가 원하는 것을 얻지만, 이 욕망이 어두운 대가를 치르게 되는 이야기입니다.
   - **개봉일**: 2026-05-13
   - **평점**: 7.9
   - ![Obsession](https://image.tmdb.org/t/p/w780/2G249T4Sgu8gXIZpaXWnxHYYNQV.jpg)

2. **Peddi**
   - **개요**: 1980년대 농촌 안드라프라데시에서 한 열정 넘치는 마을 사람이 스포츠를 통해 공동체를 결속시키는 이야기입니다.
   - **개봉일**: 2026-06-03
   - **평점**: 6.3
   - ![Peddi](https://image.tmdb.org/t/p/w780/kJAJNNBYlbqAcpTDxBNnaILSMTy.jpg)

3. **Lee Cronin's The Mummy**
   - **개요**: 기자의 어린 딸이 사라진 후 8년 만에 돌아오고, 즐거운 재회가 살아있는 악몽으로 변하는 이야기입니다.
   - **개봉일**: 2026-04-15
   - **평점**: 8.1
   - ![Lee Cronin's The Mummy](https://image.tmdb.org/t/p/w780/1q308iixueCU4pFtSYugNOevtNx.jpg)

4. **The Mandalorian and Grogu**
   - **개요**: 악의 제국이 무너진 후, 새로운 공화국이 전투에서의 결실을 지키기 위해 전설적인 맨달로리안과 그의 제자 그로구의 도움을 받는 이야기입니다.
   - **개봉일**: 2026-05-20
   - **평점**: 6.8
   - ![The Mandalorian and Grogu](https://image.tmdb.org/t/p/w780/5Vi8dSauVwH1HOsiZceDMbRr1Ca.jpg)

5. **Kara**
   - **개요**: 아버지를 빚으로 괴롭히는 은행 때문에 범죄에 빠지게 된 한 도둑의 이야기입니다.
   - **개봉일**: 2026-04-30
   - **평점**: 6.3
   - ![Kara](https://image.tmdb.org/t/p/w780/6U6i4qhgHR1MWkUb6OGQwNpqcZC.jpg)

이 외에도 많은 인기 영화들이 있으니 더 알고 싶으시면 말씀해 주세요!
Send a message to the LLM... movie ID 550에 해당하는 영화가 무엇인지 알려줘
User: movie ID 550에 해당하는 영화가 무엇인지 알려줘
Calling function: get_movie_details with {"id":550}
Ran get_movie_details with args {'id': 550}
AI: 영화 ID 550에 해당하는 영화는 **"Fight Club"**입니다.

- **개요**: 불면증에 시달리는 주인공과 미끄러운 비누 판매자가 원시적인 남성의 공격성을 새로운 형태의 치료로 전환합니다. 이들의 개념은 번창하게 되고, 각 도시마다 비밀 '파이트 클럽'이 형성되지만, eccentric한 인물이 등장하면서 폭주하는 상황이 벌어집니다.
- **개봉일**: 1999-10-15
- **러닝타임**: 139분
- **장르**: 드라마, 스릴러
- **평점**: 8.4
- **제작 국가**: 미국, 독일
- **제작사**: Fox 2000 Pictures, Regency Enterprises, Linson Entertainment, 20th Century Fox, Taurus Film
- **예산**: 63,000,000 달러
- **수익**: 100,853,753 달러
- **태그라인**: Mischief. Mayhem. Soap.
- **홈페이지**: [Fight Club Official Site](https://www.20thcenturystudios.com/movies/fight-club)

![Fight Club](https://image.tmdb.org/t/p/w780/jSziioSwPVrOy9Yow3XhWIBDjq1.jpg)
Send a message to the LLM... movie ID 550에 해당하는 영화에 누가 출연하는지 알려줘
User: movie ID 550에 해당하는 영화에 누가 출연하는지 알려줘
Calling function: get_movie_credits with {"id":550}
Ran get_movie_credits with args {'id': 550}
AI: 영화 **"Fight Club"**에 출연한 주요 배우들은 다음과 같습니다:

1. **Edward Norton** 
   - **역할**: Narrator
   - ![Edward Norton](https://image.tmdb.org/t/p/w185/8nytsqL59SFJTVYVrN72k6qkGgJ.jpg)

2. **Brad Pitt** 
   - **역할**: Tyler Durden
   - ![Brad Pitt](https://image.tmdb.org/t/p/w185/m09Y1YfPPeNYYUSHnnVqahkrC1o.jpg)

3. **Helena Bonham Carter** 
   - **역할**: Marla Singer
   - ![Helena Bonham Carter](https://image.tmdb.org/t/p/w185/hJMbNSPJ2PCahsP3rNEU39C8GWU.jpg)

4. **Meat Loaf** 
   - **역할**: Robert Paulson
   - ![Meat Loaf](https://image.tmdb.org/t/p/w185/1zkohpaG3my4qQAZGVgzgPuXwZ6.jpg)

5. **Jared Leto** 
   - **역할**: Angel Face
   - ![Jared Leto](https://image.tmdb.org/t/p/w185/ca3x0OfIKbJppZh8S1Alx3GfUZO.jpg)

6. **Zach Grenier** 
   - **역할**: Richard Chesler (Regional Manager)
   - ![Zach Grenier](https://image.tmdb.org/t/p/w185/fSyQKZO39sUsqY283GXiScOg3Hi.jpg)

7. **Holt McCallany** 
   - **역할**: The Mechanic
   - ![Holt McCallany](https://image.tmdb.org/t/p/w185/iRo9YUNMwZg4UCq7dapo0HydDmI.jpg)

8. **Eion Bailey** 
   - **역할**: Ricky
   - ![Eion Bailey](https://image.tmdb.org/t/p/w185/3DW13W47cKk4LQZwS4EvRaNBoVu.jpg)

이외에도 많은 배우들이 출연했으나, 위의 인물들은 가장 주요한 역할을 맡고 있습니다. 추가적인 정보가 필요하거나 특정 배우에 대한 질문이 있으면 말씀해 주세요!
Send a message to the LLM...  q
```