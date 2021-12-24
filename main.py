import os
import re
import random
import time
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Comment
from protopost import ProtoPost

def tag_visible(element):
  if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
    return False
  if isinstance(element, Comment):
    return False
  return True

def get_inner_text(body):
  soup = BeautifulSoup(body, 'html.parser')
  texts = soup.findAll(text=True)
  visible_texts = filter(tag_visible, texts)
  #preserve at least one newline
  text = u" ".join([t.strip() + ("\n" if t.endswith("\n") else "") for t in visible_texts])
  texts = text.split("\n")
  texts = [t.strip() for t in texts] #remove spacing at beginning and end of lines
  text = "\n".join(texts) #join back
  text = re.sub(r"\n\n+", "\n\n", text) #replace >2 consecutive newlines with only 2
  return text

PORT = int(os.getenv("PORT", 80))
MAX_LENGTH = int(os.getenv("MAX_LENGTH", 1024 * 1024))
MAX_VISITED = int(os.getenv("MAX_VISITED", 10000))
MAX_UNVISITED = int(os.getenv("MAX_UNVISITED", 1000))
#TODO: probably a better way to handle this than to add a delay...
DELAY = float(os.getenv("DELAY", 1))
USER_AGENT = os.getenv("USER_AGENT", "AegisCrawler")
#NOTE: must end in slash
START_URLS = json.loads(os.getenv("START_URLS", '["https://old.reddit.com/r/news/"]'))
START_URLS = [s + "/" if not s.endswith("/") else s for s in START_URLS]

#TODO: prefill buffer with N samples

unvisited = START_URLS
visited = []

#TODO: improve system so it doesnt get stuck on one domain

def crawl():
  #choose random url from unvisited and move it to visited
  i = random.randrange(len(unvisited))
  base_url = unvisited[i]
  unvisited.pop(i)
  visited.append(base_url)

  #grab html
  r = requests.get(base_url, headers = {"User-agent": USER_AGENT})

  #if its greater than N bytes long, ignore
  if len(r.content) > MAX_LENGTH:
    print(f"File too big {len(r.content)}...")
    return None

  #TODO: if it isnt html, ignore

  try:
    r.raise_for_status()
  except Exception:
    print(f"received status: {r.status_code}")
    return None

  html = r.text

  #attempt to decode text as utf8, if it fails then retry
  try:
    html.encode('utf-8')
  except UnicodeError:
    print("Not unicode...")
    return None

  #TODO: reuse soup?
  text = get_inner_text(html)
  links = []

  for link in BeautifulSoup(html, "html.parser", parse_only=SoupStrainer('a')):
    if link.has_attr('href'):
      link = link['href']
      link = urljoin(base_url, link)
      links.append(link)
      if link not in visited and link not in unvisited:
        unvisited.append(link)

  while len(visited) > MAX_VISITED:
    visited.pop(0)

  while len(unvisited) > MAX_UNVISITED:
    unvisited.pop(0)

  unique = len(set([urlparse(u).hostname for u in visited+unvisited]))
  print(f"Visited: {len(visited)}, Unvisited: {len(unvisited)}, Unique hostnames: {unique}")
  # print(text)
  time.sleep(DELAY)

  return {
    "url": base_url,
    "text": text,
    "links": links
  }

def do_crawl(data):
  text = None
  while text is None:
    try:
      text = crawl()
    except Exception as e:
      print("unexpected failure:")
      print(e)

    if text is None:
      print("retrying...")
      time.sleep(DELAY)

  return text

routes = {
  "": do_crawl,
}

ProtoPost(routes).start(PORT)
