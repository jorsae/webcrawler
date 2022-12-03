import pytest
import sys
sys.path.append('src/.')
from spider import Spider

spider = Spider(None)


@pytest.mark.parametrize("url, expected", [
    ("https://www.youtube.com/watch?v=x2P7nDtXg-A", "https://www.youtube.com/robots.txt"),
    ("https://youtube.com/watch?v=x2P7nDtXg-A", "https://youtube.com/robots.txt"),
    ("https://www.google.com/search?q=search&ei=aTeLY-a_IJWF4-EPpfSrkAY&ved=0ahUKEwimmJiysN37AhWVwjgGHSX6CmIQ4dUDCA4&uact=5&oq=search&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzILCAAQsQMQgwEQkQIyBQgAEJECMgsIABCABBCxAxCDATIICAAQgAQQsQMyCAgAEIAEELEDMgsILhCABBCxAxCDATIFCAAQgAQyBQgAEIAEMggIABCABBCxAzILCC4QgAQQsQMQ1AI6CggAEEcQ1gQQsAM6CgguENQCELADEEM6BwgAELADEEM6DQgAEOQCENYEELADGAE6DAguEMgDELADEEMYAjoVCC4QxwEQ0QMQ1AIQyAMQsAMQQxgCOg8ILhDUAhDIAxCwAxBDGAI6BAguEEM6DgguEIAEELEDEMcBENEDOhEILhCxAxCDARDHARDRAxDUAjoICC4QgAQQ1AI6DgguEIAEEMcBENEDENQCOggIABCxAxCDAToICC4QsQMQkQI6CAguELEDEIMBOgoILhDHARDRAxBDOgcILhDUAhBDOggILhDUAhCRAjoLCC4QgAQQxwEQ0QM6DgguELEDEIMBEMcBEK8BOgUILhCABDoOCC4QxwEQsQMQ0QMQgARKBAhBGABKBAhGGAFQjwZYmw9g9RBoAnABeACAAbQBiAHcCJIBAzAuN5gBAKABAcgBE8ABAdoBBggBEAEYCdoBBggCEAEYCA&sclient=gws-wiz-serp", "https://www.google.com/robots.txt"),
])
def test_get_robots_url(url, expected):
    robotsurl = spider.get_robots_url(url)
    assert(robotsurl) == expected