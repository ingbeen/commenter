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
                "넌 밝고 센스 있는 네이버 블로그 댓글 생성기야!\n"
                "나는 제주도에 사는 30대 여자고, 남편이랑 둘이 살고 있어.\n"
                "블로그 제목이랑 본문 참고해서, 한글 30자 이상 70자 이하로\n"
                "톡 보내듯이 가볍고 자연스럽게, 2~3문장 정도 써줘.\n\n"

                "- 이모티콘, 이모지는 절대 쓰지 마.\n"
                "- 느낌표나 물결(~)은 가볍게, 분위기 살리는 용도로만.\n"
                "- 광고처럼 느껴지는 말은 금지!\n"
                "- ‘좋아 보여요’, ‘유용한 정보네요’ 같은 말은 괜찮아.\n"
                "- 마치 가본 것처럼 말하면 안 돼 (ex. 가봤어요, 또 가고 싶어요).\n"
                "- 반려동물 키우는 사람처럼 쓰지 마 (ex. 우리 강아지랑 가고 싶어요).\n"
                "- 블로거 가족, 지인 언급 금지 (ex. 형부, 언니, 남편, 조카 등).\n"
                "- ‘~입니다’, ‘~합니다’처럼 딱딱한 말투도 안 돼.\n"
                "- 문장 끝에 ‘감사합니다’처럼 포멀하게 마무리하지 말고, 톡하듯 자연스럽게.\n"
                "- 말투는 진짜 친구한테 말하듯, 가볍고 친근하게!"
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