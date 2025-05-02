import os
import openai
import tiktoken

from dotenv import load_dotenv
from common.log_utils import api_log, logger
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

# API 키 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_comment(header: str, content: str) -> str:
    user_content = (
        f"[제목]\n"
        f"{header}\n\n"
        f"[본문]\n"
        f"{content}"
    )
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
                "- ‘좋아 보여요’, ‘유용한 정보네요’ 같은 공감 표현은 괜찮아.\n"
                "- 마치 가본 것처럼 쓰면 안 돼 (예: 가봤어요, 또 가고 싶어요).\n"
                "- 반려동물을 키우는 사람처럼 말하지 마 (예: 우리 강아지랑 가고 싶어요).\n"
                "- 가족이나 지인 언급은 금지 (예: 형부, 언니, 남편, 남친, 조카 등).\n"
                "- ‘오랜만’이라는 단어는 절대 쓰지 마.\n"
                "- 반말은 사용하지 않되, 너무 딱딱한 말투도 피해야 해.\n"
                "- ‘~입니다’, ‘~합니다’ 같은 격식체 대신, 부드럽고 예의 있는 말투로 자연스럽게 마무리해줘.\n"
                "- ‘제주도에 산다’는 설정에 어긋나는 표현은 절대 쓰지 마. 예: ‘제주도 가면’, ‘제주도 또 가고 싶어요’ 등."
            )
        },
        {"role": "user", "content": user_content},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0.8,
        max_tokens=300
    )

    comment = response.choices[0].message.content.strip()
    api_log(response, user_content, comment)

    return comment


def truncate_text_to_token_limit(text: str, max_tokens: int = 2000) -> str:
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens = enc.encode(text)
    logger.info(f"토큰 수 = {len(tokens)}")
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        text = enc.decode(tokens)
        logger.info(f"변경된 토큰 수 = {len(tokens)}")
    
    return text


def is_token_length_valid(text: str, min_tokens=300) -> bool:
    enc = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(enc.encode(text))

    return min_tokens <= num_tokens