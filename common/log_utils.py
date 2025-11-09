import logging
import os
import traceback
from typing import Optional
from openai.types.chat import ChatCompletionMessageParam

# 로그 저장 디렉토리 설정
LOG_DIR = r"C:\logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 로그 파일 경로 설정
log_file_path = os.path.join(LOG_DIR, "app.log")

# 로깅 기본 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler(),  # 콘솔 출력도 포함
    ],
)

logger = logging.getLogger(__name__)


def api_log(response, user_content: str, comment: str):
    usage = response.usage
    user_content = user_content.replace("\n", " / ")
    msg = (
        "[API 사용로그]\n"
        f"user_content: {user_content}\n"
        f"comment: {comment}\n"
        f"총 토큰: {usage.total_tokens} / 입력: {usage.prompt_tokens} / 출력: {usage.completion_tokens}"
    )

    logger.info(msg)


def error_log(e: Exception, url: Optional[str] = None):
    trace = traceback.format_exc().split("Stacktrace:")[0].strip()
    if url:
        msg = f"[예외 발생 - URL: {url}]\n{trace}"
    else:
        msg = f"[예외 발생]\n{trace}"

    logger.error(msg)
