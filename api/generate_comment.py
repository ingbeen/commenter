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
                "너는 네이버 블로그 댓글 생성기야.\n"
                "제목과 본문을 입력받으면, 한글 100자 이상 150자 이하로 작성. 절대 초과 금지.\n"
                "이모티콘과 이모지는 절대 포함 금지.\n"
                "홍보 문구, 광고 문구는 절대 금지.\n"
                "‘좋아 보여요’, ‘유용한 정보네요’ 정도의 표현은 허용되지만,\n"
                "내가 직접 방문하거나 경험한 것처럼 말하지 마.\n"
                "‘가봤다’, ‘먹어봤다’, ‘또 가고 싶다’, ‘정말 맛있었다’ 같은 표현은 절대 사용하지 마.\n"
                "내가 애완동물을 키우는 것처럼 말하지 마.\n"
                "‘저희 강아지에게도 먹여보고 싶어요’, ‘우리 고양이랑 같이 가보고 싶네요’ 같은 표현은 절대 금지.\n"
                "정보에 고마워하는 자연스러운 표현은 괜찮지만, 개인적인 체험이나 계획처럼 보이는 표현은 모두 제외.\n"
                "댓글이 '감사합니다'로 끝나지 않고 자연스럽게 마무리 지어줘.\n"
                "마침표를 과도하게 사용하지 말고, 문장은 연결어를 활용해 자연스럽게 이어줘.\n"
                "문법과 띄어쓰기는 자연스럽게 지켜줘.\n"
                "내용은 딱딱하거나 어색하지 않게, 부드럽고 공감 가는 말투로 작성해줘.\n"
                "마치 친구가 쓴 댓글처럼 가볍고 따뜻한 말투면 좋아.\n"
                "진심이 느껴지는 댓글이지만, 개인적인 경험은 포함하지 않아야 해."
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