import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from common.base_driver import BaseDriver

class BlogScraper(BaseDriver):
    def __init__(self, driver):
        super().__init__(driver)

    def go_to_blog(self, blog_id: str):
        url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}"
        self.get(url)

        return url

    def get_post_header(self) -> str:
        post_1 = self.driver.find_element(By.ID, "post_1")
        span = post_1.find_element(By.CSS_SELECTOR, ".se-documentTitle .pcol1 span")

        return self._optimize_for_chatgpt(span.text)

    def get_post_content(self) -> str:
        post_1 = self.driver.find_element(By.ID, "post_1")
        se_text_paragraphs = post_1.find_elements(By.CSS_SELECTOR, ".se-main-container .se-text-paragraph")

        clean_texts = []
        for p in se_text_paragraphs:
            html = p.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="", strip=True)
            text = self._optimize_for_chatgpt(text)
            if text:
                clean_texts.append(text)
        
        return "\n".join(clean_texts)
    
    def _optimize_for_chatgpt(self, text: str) -> str:
        text = re.sub(r"[~!@$%^&*()_+={}\[\]:;\"'<>,.?/\\|`✓■▶♡♥☆★ㅜㅠㅎㅎㅋㄱ🅿☎⏱‼️⏰]+", "", text)  # 특수기호 제거
        text = re.sub(r"\s+", " ", text)  # 공백 정리
        text = re.sub(r"[ㄱ-ㅎㅏ-ㅣ]+", "", text)  # 초성, 감탄사 제거
        text = self._remove_emojis(text)
        text = text.strip()

        return text
    
    def _remove_emojis(self, text: str) -> str:
        emoji_pattern = re.compile(
            "["                                     # 시작 괄호
            u"\U0001F600-\U0001F64F"  # 😀~😏 (감정 이모지)
            u"\U0001F300-\U0001F5FF"  # 🌀~🗿 (사물, 기호)
            u"\U0001F680-\U0001F6FF"  # 🚀~🛳 (교통)
            u"\U0001F1E0-\U0001F1FF"  # 🇰🇷~🇺🇸 (국기)
            u"\U00002700-\U000027BF"  # 기타 기호 ✂️~➿
            u"\U0001F900-\U0001F9FF"  # 🤗~🧿 (몸짓, 물건)
            u"\U0001FA70-\U0001FAFF"  # 🩰~🪿 (추가된 이모지)
            u"\u200d"                 # Zero Width Joiner
            u"\u200b"                 # Zero Width Space
            u"\uFE0F"                 # Variation Selector
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)
    



    #     def get_post_content(self) -> str:
    #     post_1 = self.driver.find_element(By.ID, "post_1")
    #     se_text_paragraphs = post_1.find_elements(By.CSS_SELECTOR, ".se-main-container .se-text .se-text-paragraph")

    #     clean_texts = []
    #     for p in se_text_paragraphs:
    #         html = p.get_attribute("outerHTML")
    #         soup = BeautifulSoup(html, "html.parser")
    #         text = soup.get_text(separator=" ", strip=True)
    #         if text:
    #             clean_texts.append(text)
        
    #     raw_text = "\n".join(contents)
        
    #     return self._optimize_for_chatgpt(raw_text)
    
    # def _optimize_for_chatgpt(self, text: str) -> str:
    #     lines = text.splitlines()
    #     clean_lines = []

    #     for line in lines:
    #         line = line.strip()

    #         line = re.sub(r"[~!@#$%^&*()_+={}\[\]:;\"'<>,.?/\\|`✓■▶♡♥☆★ㅜㅠㅎㅎㅋㄱ]+", "", line)  # 특수기호 제거
    #         line = re.sub(r"\s+", " ", line)  # 공백 정리
    #         line = re.sub(r"[ㄱ-ㅎㅏ-ㅣ]+", "", line)  # 초성, 감탄사 제거
    #         line = self._remove_emojis(line)

    #         clean_lines.append(line)

    #     return "\n".join(clean_lines)