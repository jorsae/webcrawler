from bs4 import BeautifulSoup
from bs4.element import Comment
import logging

def get_visible_data(content):
    soup = BeautifulSoup(content, "html.parser")
    for script in soup(["script", "style"]):
        script.extract() # rip it out
    
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True