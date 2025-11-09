import os
import openai
import tiktoken

from dotenv import load_dotenv
from common.log_utils import api_log, logger
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

# OpenAI API 클라이언트 초기화
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def generate_comment(header: str, content: str) -> str:
    """
    OpenAI GPT-4o-mini를 사용하여 블로그 게시글에 대한 댓글 생성

    제주도에 사는 30대 여성이라는 페르소나를 기반으로,
    자연스럽고 공감 가는 댓글을 생성합니다.

    Args:
        header: 블로그 게시글 제목
        content: 블로그 게시글 본문 (토큰 제한 적용됨)

    Returns:
        str: 생성된 댓글
    """
    # 사용자 프롬프트 구성 (제목 + 본문)
    user_content = f"[제목]\n" f"{header}\n\n" f"[본문]\n" f"{content}"

    # 시스템 프롬프트: 댓글 생성 규칙 정의
    # - 페르소나: 제주도에 사는 30대 여성
    # - 말투: 자연스럽고 부드러운 존댓말
    # - 제한 사항: 이모지, 가족 언급, 반려동물 언급, 장소 방문 가정 금지
    prompt: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "넌 밝고 센스 있는 네이버 블로그 댓글 생성기야.\n"
                "나는 제주도에 사는 30대 여자라는 설정이야.\n"
                "블로그 제목과 본문을 참고해서, 2~3문장으로 작성해줘.\n"
                "중요: 댓글은 반드시 한글 30자 이상, 70자 이하여야 해. 71자 이상은 절대 안 돼.\n"
                "말투는 톡 보내듯 자연스럽고 가볍게 해줘.\n\n"
                "- 이모티콘과 이모지는 절대 쓰지 마.\n"
                "- 느낌표나 물결(~)은 분위기를 살릴 때만 가볍게 사용해.\n"
                "- 광고처럼 보이는 말은 금지!\n"
                "- '좋아 보여요', '유용한 정보네요' 같은 공감 표현은 괜찮아.\n"
                "- 마치 가본 것처럼 쓰면 안 돼 (예: 가봤어요, 또 가고 싶어요).\n"
                "- 반려동물을 키우는 사람처럼 말하지 마 (예: 우리 강아지랑 가고 싶어요).\n"
                "- 가족이나 지인 언급은 금지 (예: 형부, 언니, 남편, 남친, 조카 등).\n"
                "- '오랜만'이라는 단어는 절대 쓰지 마.\n"
                "- 반말은 사용하지 않되, 너무 딱딱한 말투도 피해야 해.\n"
                "- '~입니다', '~합니다' 같은 격식체 대신, 부드럽고 예의 있는 말투로 자연스럽게 마무리해줘.\n"
                "- '제주도에 산다'는 설정에 어긋나는 표현은 절대 쓰지 마. 예: '제주도 가면', '제주도 또 가고 싶어요' 등."
            ),
        },
        {"role": "user", "content": user_content},
    ]

    # OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=prompt, temperature=0.8, max_tokens=300
    )

    # 생성된 댓글 추출 및 로깅
    comment = response.choices[0].message.content.strip()
    api_log(response, user_content, comment)

    return comment


def truncate_text_to_token_limit(text: str, max_tokens: int = 2000) -> str:
    """
    텍스트를 지정된 토큰 수로 자르기

    OpenAI API 요청 시 토큰 제한을 초과하지 않도록
    텍스트를 최대 토큰 수로 제한합니다.

    Args:
        text: 자를 텍스트
        max_tokens: 최대 토큰 수

    Returns:
        str: 토큰 제한에 맞게 잘린 텍스트
    """
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens = enc.encode(text)

    # 토큰 수가 제한을 초과하면 잘라내기
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        text = enc.decode(tokens)

    return text


def is_token_length_valid(text: str, min_tokens=300) -> bool:
    """
    텍스트의 토큰 수가 최소 기준을 만족하는지 확인

    본문이 너무 짧은 게시글을 필터링하기 위해 사용됩니다.

    Args:
        text: 검증할 텍스트
        min_tokens: 최소 토큰 수

    Returns:
        bool: 최소 토큰 수 이상이면 True, 미만이면 False
    """
    enc = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(enc.encode(text))

    return min_tokens <= num_tokens
