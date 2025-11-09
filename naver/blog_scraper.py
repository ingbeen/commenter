import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from driver.base_driver import BaseDriver
from driver.driver_manager import DriverManager


class BlogScraper(BaseDriver):
    def __init__(self, driver_manager: DriverManager):
        super().__init__(driver_manager)

    def go_to_blog(self, blog_id: str):
        url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}"
        self.get(url)

        return url

    def get_post_header(self) -> str:
        post_1 = self.driver_manager.get_driver().find_element(By.ID, "post_1")
        span = post_1.find_element(By.CSS_SELECTOR, ".se-documentTitle .pcol1 span")

        return self._optimize_for_chatgpt(span.text)

    def get_post_content(self) -> str:
        post_1 = self.driver_manager.get_driver().find_element(By.ID, "post_1")
        se_text_paragraphs = post_1.find_elements(
            By.CSS_SELECTOR, ".se-main-container .se-text-paragraph"
        )

        clean_texts = []
        for p in se_text_paragraphs:
            html = p.get_attribute("outerHTML") or ""
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="", strip=True)
            text = self._optimize_for_chatgpt(text)
            if text:
                clean_texts.append(text)

        return "\n".join(clean_texts)

    def _optimize_for_chatgpt(self, text: str) -> str:
        text = re.sub(
            r"[~!@$%^&*()_+={}\[\]:;\"'<>,.?/\\|`✓■▶♡♥☆★ㅜㅠㅎㅎㅋㄱ🅿☎⏱♠【】▷▽‼️⭐☝⏰⭕𐭩•ᡣ↓▼”ദ്ദി｡̀‧₊◡´ゝ☺‘’※●₍ᐢ₎ෆ-▫▪٩๑˃́ꇴ˂๑وԅ ˘ω˘ԅᴗ́و･ﾟ˚]+",
            "",
            text,
        )  # 특수기호 제거
        text = re.sub(r"\s+", " ", text)  # 공백 정리
        text = re.sub(r"[ㄱ-ㅎㅏ-ㅣ]+", "", text)  # 초성, 감탄사 제거
        text = self._remove_emojis(text)
        text = text.strip()

        return text

    def _remove_emojis(self, text: str) -> str:
        emoji_pattern = re.compile(
            "["  # 시작 괄호
            "\U0001f600-\U0001f64f"  # 😀~😏 (감정 이모지)
            "\U0001f300-\U0001f5ff"  # 🌀~🗿 (사물, 기호)
            "\U0001f680-\U0001f6ff"  # 🚀~🛳 (교통)
            "\U0001f1e0-\U0001f1ff"  # 🇰🇷~🇺🇸 (국기)
            "\U00002700-\U000027bf"  # 기타 기호 ✂️~➿
            "\U0001f900-\U0001f9ff"  # 🤗~🧿 (몸짓, 물건)
            "\U0001fa70-\U0001faff"  # 🩰~🪿 (추가된 이모지)
            "\u200d"  # Zero Width Joiner
            "\u200b"  # Zero Width Space
            "\ufe0f"  # Variation Selector
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub(r"", text)
