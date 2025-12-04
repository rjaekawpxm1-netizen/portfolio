from urllib.parse import urlparse

def extract_oid_aid(url: str):
    path = urlparse(url).path
    parts = path.split("/")
    oid = parts[3]
    aid = parts[4]
    return oid, aid

# 테스트용
url = "https://n.news.naver.com/mnews/article/001/0012345678?sid=100"
oid, aid = extract_oid_aid(url)
print("oid:", oid)
print("aid:", aid)
