import os
import praw
from datetime import datetime

# Keywords to look for in the text (broad search)
KEYWORDS = ["interview", "invite", "out"]

# The exact required fields (in lowercase for comparison)
REQUIRED_FIELDS = [
    "time stamp:",
    "program:",
    "result:",
    "omsas gpa:",
    "cars:",
    "casper:",
    "geography:",
    "current year:"
]

# Define a timeframe for 2024–2025 cycle.
# (For example, posts from Jan 1, 2024 to Jan 1, 2026)
START_TIMESTAMP = 1704067200   # Jan 1, 2024 UTC
END_TIMESTAMP   = 1767225600   # Jan 1, 2026 UTC

# Initialize Reddit with credentials from environment variables
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT", "MDTracker by Impossible_Ad346")
)

def contains_keywords(text):
    """Return True if any keyword is found in text (case-insensitive)."""
    lower_text = text.lower()
    return any(keyword in lower_text for keyword in KEYWORDS)

def parse_strict_template(text):
    """
    Checks that text contains all required fields (case-insensitive)
    and parses each field by splitting on ':'.
    Returns a dict with extracted values if successful; otherwise, None.
    """
    text_lower = text.lower()
    # Ensure all required lines are present
    if not all(field in text_lower for field in REQUIRED_FIELDS):
        return None

    data = {}
    lines = text.splitlines()
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        if line_lower.startswith("time stamp:"):
            data["time_stamp"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("program:"):
            data["program"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("result:"):
            data["result"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("omsas gpa:"):
            data["omsas_gpa"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("cars:"):
            data["cars"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("casper:"):
            data["casper"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("geography:"):
            data["geography"] = line_stripped.split(":", 1)[1].strip()
        elif line_lower.startswith("current year:"):
            data["current_year"] = line_stripped.split(":", 1)[1].strip()
    
    # Only return data if we have all fields
    if len(data) == len(REQUIRED_FIELDS):
        return data
    return None

def fetch_and_generate():
    """Fetch posts from r/premed, filter by keywords and timeframe, parse the template, and generate index.html."""
    subreddit = reddit.subreddit("premed")
    posts = subreddit.new(limit=500)
    parsed_entries = []

    for post in posts:
        # Filter by creation time (2024–2025 cycle)
        if not (START_TIMESTAMP <= post.created_utc < END_TIMESTAMP):
            continue

        # Only consider text posts (selftext must exist)
        if not post.selftext:
            continue

        # Broader search: Check if the post contains any of our keywords
        if not contains_keywords(post.selftext):
            continue

        # Now try to parse the strict template from the text
        parsed_data = parse_strict_template(post.selftext)
        if parsed_data:
            entry = {
                "title": post.title,
                "permalink": f"https://reddit.com{post.permalink}",
                **parsed_data
            }
            parsed_entries.append(entry)

    # Build the HTML table with the parsed data
    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>MDTracker Interview Results (2024-2025)</title>",
        "<style>",
        "  body { font-family: Arial, sans-serif; margin: 20px; }",
        "  table { border-collapse: collapse; width: 100%; }",
        "  th, td { border: 1px solid #ccc; padding: 8px; }",
        "  th { background: #f4f4f4; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>MDTracker Interview Results (2024-2025)</h1>",
        "<table>",
        "<tr>",
        "  <th>Title</th>",
        "  <th>Time Stamp</th>",
        "  <th>Program</th>",
        "  <th>Result</th>",
        "  <th>OMSAS GPA</th>",
        "  <th>CARS</th>",
        "  <th>Casper</th>",
        "  <th>Geography</th>",
        "  <th>Current Year</th>",
        "  <th>Link</th>",
        "</tr>"
    ]
    for entry in parsed_entries:
        html_lines.append("<tr>")
        html_lines.append(f"<td>{entry['title']}</td>")
        html_lines.append(f"<td>{entry['time_stamp']}</td>")
        html_lines.append(f"<td>{entry['program']}</td>")
        html_lines.append(f"<td>{entry['result']}</td>")
        html_lines.append(f"<td>{entry['omsas_gpa']}</td>")
        html_lines.append(f"<td>{entry['cars']}</td>")
        html_lines.append(f"<td>{entry['casper']}</td>")
        html_lines.append(f"<td>{entry['geography']}</td>")
        html_lines.append(f"<td>{entry['current_year']}</td>")
        html_lines.append(f"<td><a href='{entry['permalink']}' target='_blank'>Link</a></td>")
        html_lines.append("</tr>")
    html_lines.append("</table>")

    # Append a last updated timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    html_lines.append(f"<p>Last updated: {timestamp} UTC</p>")
    html_lines.append("</body></html>")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated index.html with {len(parsed_entries)} entries found.")

if __name__ == "__main__":
    fetch_and_generate()
