# Aegis web crawler node

A simple method to just get text from the internet:
1. choose a random url from the unvisited list and move it to the visited list
2. download text; goto 1 if text is too big or is not valid utf8
3. extract all links from the page
4. for every link, add the link to the unvisited list if it is not currently in the visited or unvisited lists
5. return {url, text, links}

## Usage
POST to `/` to receive:
```js
{
  "url": "the url that was scraped",
  "text": "the 'inner text' of the page",
  "links": ["a list of", "links on", "the page"]
}
```

## Environment
- `MAX_LENGTH` - max length (in bytes) on the page (defaults to 1048576; 1MB)
- `MAX_VISITED` - max number of visited sites to remember (defaults to 10000)
- `MAX_UNVISITED` - max number of unvisited sites to remember (defaults to 1000)
- `PORT` - the port to listen on (defaults to 80)
- `DELAY` - amount to delay responses by, in seconds (this is a horrible idea; defaults to 1)
- `USER_AGENT` - user agent string to appear as (defaults to "AegisCrawler")
- `START_URLS` - json encoded list of urls to start scraping on (defaults to '["https://old.reddit.com/r/news/"]')

## TODO
- method for only adding a maximum of N random new links from the page
