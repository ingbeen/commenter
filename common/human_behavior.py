"""
봇 탐지 회피를 위한 행동 패턴 시뮬레이션 모듈

네이버 보호조치를 우회하기 위해 자연스러운 사용자 행동을 시뮬레이션합니다.
- 페이지 읽기 시뮬레이션 (스크롤, 체류)
- 정확한 체류시간 제어
- 상세한 로그 출력
"""

import random
import time

from common.log_utils import logger
from common.time_utils import wait_random

# ============================================================================
# 상수 정의
# ============================================================================

# 봇 탐지 회피 활성화 여부
BOT_EVASION_ENABLED = True

# 전체 체류시간 설정 (초)
TOTAL_STAY_DURATION_MIN = 20
TOTAL_STAY_DURATION_MAX = 40

# 스크롤 구간별 읽기 시간 (초)
READING_PAUSE_MIN = 1.0
READING_PAUSE_MAX = 3.0

# 스크롤 설정
SCROLL_PIXEL_MIN = 700
SCROLL_PIXEL_MAX = 1500

# 확률 설정
REVERSE_SCROLL_PROBABILITY = 0.1  # 역스크롤 확률


# ============================================================================
# 핵심 함수
# ============================================================================


def smooth_scroll(driver, total_pixels):
    """
    부드러운 스크롤 구현 (스르르 내려가기)

    JavaScript의 smooth scroll 기능을 사용하여 자연스러운 스크롤을 구현합니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        total_pixels: 총 스크롤할 픽셀 수 (음수면 위로 스크롤)
    """
    driver.execute_script(
        f"""
        window.scrollBy({{
            top: {total_pixels},
            behavior: 'smooth'
        }});
    """
    )
    # smooth scroll 애니메이션이 완료될 때까지 대기
    wait_random(min_sec=0.5, max_sec=1.0)


def is_at_page_bottom(driver):
    """
    스크롤이 페이지 맨 아래에 도달했는지 확인

    Returns:
        bool: 페이지 맨 아래면 True, 아니면 False
    """
    return driver.execute_script(
        "return (window.innerHeight + window.pageYOffset) >= document.body.scrollHeight;"
    )


def simulate_reading(driver, target_duration, btn_comment=None):
    """
    페이지 읽기를 시뮬레이션하여 자연스러운 사용자 행동 재현

    전체 체류시간을 정확히 제어하며, 각 행동마다 상세한 로그를 출력합니다.

    처리 흐름:
    1. 최소 체류시간 설정 및 시작 시간 기록
    2. 페이지 상단으로 이동
    3. target_duration 기반 스크롤 구간 수 계산
       - 평균 읽기 시간(READING_PAUSE 중간값)으로 적정 구간 수 산출
    4. 스크롤 구간별 반복:
       - 부드러운 스크롤 이동
       - 페이지 맨 아래 도달 확인 (도달 시 반복 중단)
       - 구간별 읽기 시간 체류
       - 확률적으로 역스크롤
    5. 경과 시간 계산 및 부족한 시간 추가 대기
    6. 총 소요 시간 로그 출력
    7. 댓글 버튼 위치로 스크롤 이동

    Args:
        driver: Selenium WebDriver 인스턴스
        target_duration: 최소 체류시간 (초)
        btn_comment: 댓글 버튼 웹 요소 (선택적, None이면 스크롤 스킵)
    """
    start_time = time.time()
    logger.info(f"봇 탐지 회피 시작: 최소 체류시간 {target_duration:.1f}초")

    # 1. 페이지 상단으로 이동
    driver.execute_script("window.scrollTo(0, 0);")
    logger.info("페이지 상단으로 이동")
    wait_random(min_sec=1, max_sec=2)

    # 2. 스크롤 구간 수 계산 (target_duration 기반)
    average_pause = (READING_PAUSE_MIN + READING_PAUSE_MAX) / 2
    sections = max(1, int(target_duration / average_pause))
    logger.info(f"계산된 스크롤 구간 수: {sections} (목표 시간: {target_duration:.1f}초)")

    # 3. 각 구간별 스크롤 및 읽기 시뮬레이션
    for i in range(sections):
        # 3-1. 부드러운 스크롤 이동
        scroll_amount = random.randint(SCROLL_PIXEL_MIN, SCROLL_PIXEL_MAX)
        smooth_scroll(driver, scroll_amount)

        # 3-2. 페이지 맨 아래 도달 확인
        if is_at_page_bottom(driver):
            logger.info(f"스크롤 {i+1}/{sections}: 페이지 맨 아래 도달, 스크롤 중단")
            break

        # 3-3. 읽기 시간 체류
        logger.info(
            f"스크롤 {i+1}/{sections}: {scroll_amount}px 이동, {READING_PAUSE_MIN:.1f}~{READING_PAUSE_MAX:.1f}초 체류"
        )
        wait_random(min_sec=READING_PAUSE_MIN, max_sec=READING_PAUSE_MAX)

        # 3-4. 확률적으로 역스크롤 (첫 번째 구간 제외)
        if i > 0 and random.random() < REVERSE_SCROLL_PROBABILITY:
            reverse_amount = random.randint(SCROLL_PIXEL_MIN, SCROLL_PIXEL_MAX) / 2
            smooth_scroll(driver, -reverse_amount)
            logger.info(f"역스크롤: -{reverse_amount}px")
            wait_random(min_sec=1.0, max_sec=2.0)

    # 4. 경과 시간 계산 및 부족한 시간 추가 대기
    elapsed = time.time() - start_time

    if elapsed < target_duration:
        remaining = target_duration - elapsed
        logger.info(f"추가 대기: {remaining:.1f}초")
        time.sleep(remaining)

    # 5. 총 소요 시간 로그 출력
    total_elapsed = time.time() - start_time
    logger.info(f"봇 탐지 회피 완료: 총 {total_elapsed:.1f}초 소요")

    # 6. 댓글 버튼 위치로 스크롤 이동
    if btn_comment:
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                btn_comment,
            )
            logger.info("댓글 버튼 위치로 스크롤 이동")
            wait_random(min_sec=1.0, max_sec=2.0)
        except Exception as e:
            logger.warning(f"댓글 버튼으로 스크롤 실패: {e}")
