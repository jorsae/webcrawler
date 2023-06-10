import logging

from bs4 import BeautifulSoup
from bs4.element import Comment
from summarizer import Summarizer


def get_summarization(content):
    visible_data = get_visible_data(content)
    model = Summarizer()
    result = model(visible_data, ratio=0.2)
    return result


def get_visible_data(content):
    try:
        soup = BeautifulSoup(content, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)
    except Exception as e:
        logging.error(e)
        return ""


def tag_visible(element):
    if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
        return False
    if isinstance(element, Comment):
        return False
    return True
