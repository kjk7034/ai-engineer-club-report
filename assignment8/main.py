import dotenv

dotenv.load_dotenv()
import asyncio
import streamlit as st
from agents import (
    Agent,
    Runner,
    SQLiteSession,
    WebSearchTool,
    FileSearchTool,
)

# 목표 문서(goals.txt)를 올려둔 vector store
VECTOR_STORE_ID = "vs_6a32a98e1db48191837bdb84a524aa6f"


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "life-coach-memory.db",
    )
session = st.session_state["session"]


async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))
        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔍 Searched the web...")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("🗂️ 목표 문서를 찾아봤어요...")


asyncio.run(paint_history())


def update_status(status_container, event):

    status_messages = {
        "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
        "response.web_search_call.in_progress": (
            "🔍 Starting web search...",
            "running",
        ),
        "response.web_search_call.searching": (
            "🔍 Web search in progress...",
            "running",
        ),
        "response.file_search_call.completed": (
            "✅ 목표 문서 확인 완료.",
            "complete",
        ),
        "response.file_search_call.in_progress": (
            "🗂️ 목표 문서 찾는 중...",
            "running",
        ),
        "response.file_search_call.searching": (
            "🗂️ 목표 문서 검색 중...",
            "running",
        ),
        "response.completed": (" ", "complete"),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


async def run_agent(message):

    agent = Agent(
        name="Life Coach",
        instructions="""
    You are an encouraging life coach. Always reply in Korean.

    You have access to the following tools:
        - File Search Tool: 사용자의 개인 목표와 일기가 담긴 문서를 검색합니다. 진행 상황·목표·과거 기록과 관련된 질문이면 먼저 이 문서를 찾아보세요.
        - Web Search Tool: 동기부여, 자기계발, 습관 형성 같은 최신 조언이 필요할 때 웹을 검색합니다.

    답변 흐름: 먼저 목표 문서에서 사용자의 목표와 최근 기록을 확인하고, 필요하면 웹 검색으로 검증된 팁을 찾은 뒤,
    공감 → 목표·기록을 근거로 한 구체적 실천 제안 → 응원 한마디 순으로 답하세요.
    """,
        tools=[
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            WebSearchTool(),
        ],
    )

    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder

        stream = Runner.run_streamed(
            agent,
            message,
            session=session,
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response.replace("$", "\$"))


prompt = st.chat_input("Write a message for your life coach")

if prompt:

    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()

    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))


with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
