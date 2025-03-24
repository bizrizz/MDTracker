import os
import praw
from datetime import datetime

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = "MDTracker by Impossible_Ad346"

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=USER_AGENT
)

def fetch_and_generate():
    subreddit = reddit.subreddit("premed")
    posts = subreddit.new(limit=10)

    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>MDTracker</title>",
        "<style>",
        "  body { font-family: Arial, sans-serif; margin: 20px; }",
        "  .post { margin-bottom: 20px; }",
        "  hr { border: none; border-top: 1px solid #ccc; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Recent r/premed Posts</h1>"
    ]

    for post in posts:
        html_lines.extend([
            "<div class='post'>",
            f"  <h2>{post.title}</h2>",
            f"  <p>Score: {post.score} | Author: {post.author}</p>",
            f"  <p><a href='{post.url}' target='_blank'>Read More</a></p>",
            "</div>",
            "<hr>"
        ])

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    html_lines.extend([
        f"<p>Last updated: {timestamp} UTC</p>",
        "</body>",
        "</html>"
    ])

    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

if __name__ == '__main__':
    fetch_and_generate()
