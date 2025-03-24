import os
import praw
from datetime import datetime

# Read Reddit credentials from environment variables (recommended).
# For local testing, you can export them like so:
#   export REDDIT_CLIENT_ID="your_client_id"
#   export REDDIT_CLIENT_SECRET="your_client_secret"
#   export USER_AGENT="MDTracker by your_reddit_username"

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT", "MDTracker by Impossible_Ad346")

# Initialize the Reddit instance using PRAW
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=USER_AGENT
)

def parse_interview_data_line_by_line(text):
    """
    Splits the post body (selftext) into lines, looks for known fields, and returns a dict.
    Example lines expected:
      Time Stamp: 2025-03-15
      Program: MD
      Result: Invite
      OMSAS GPA: 3.9
      CARS: 129
      Casper: ...
      Geography: IP
      Current year: 4th
    This function is case-insensitive for the field names.
    """
    data = {}
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue  # skip empty lines

        lower_line = line.lower()
        if lower_line.startswith("time stamp:"):
            data["time_stamp"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("program:"):
            data["program"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("result:"):
            data["result"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("omsas gpa:"):
            data["omsas_gpa"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("cars:"):
            data["cars"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("casper:"):
            data["casper"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("geography:"):
            data["geography"] = line.split(":", 1)[1].strip()
        elif lower_line.startswith("current year:"):
            data["current_year"] = line.split(":", 1)[1].strip()

    # If the post has at least one recognized field, consider it valid for display.
    # Adjust logic if you require *all* fields to be present.
    if data:
        return data
    return None

def fetch_and_generate():
    """
    1. Fetch recent posts from r/premed.
    2. Parse only those that contain interview-like data.
    3. Generate an HTML table with the relevant info.
    4. Write the results to index.html.
    """
    # Access the r/premed subreddit
    subreddit = reddit.subreddit("premed")

    # We can fetch more posts to increase our chances of finding the interview template.
    # Adjust as needed. You could also use .search("Interview") if you want to narrow results.
    posts = subreddit.new(limit=300)

    parsed_entries = []

    for post in posts:
        # Only consider text posts (selftext). Link/image posts might not have relevant data.
        if not post.selftext:
            continue

        data = parse_interview_data_line_by_line(post.selftext)
        if data:
            # Optionally, filter only "Invite" or "MD" or certain schools, etc.
            # e.g.:
            # if "invite" not in data.get("result", "").lower():
            #     continue

            # Add some metadata
            entry = {
                "title": post.title,
                "permalink": f"https://reddit.com{post.permalink}",
                **data
            }
            parsed_entries.append(entry)

    # Build the HTML table
    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>MDTracker Interviews</title>",
        "<style>",
        "  body { font-family: Arial, sans-serif; margin: 20px; }",
        "  table { border-collapse: collapse; width: 100%; }",
        "  th, td { border: 1px solid #ccc; padding: 8px; }",
        "  th { background: #f4f4f4; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Interview Results (r/premed)</h1>",
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
        "</tr>"
    ]

    for entry in parsed_entries:
        html_lines.append("<tr>")
        html_lines.append(f"<td><a href='{entry['permalink']}' target='_blank'>{entry['title']}</a></td>")
        html_lines.append(f"<td>{entry.get('time_stamp', '')}</td>")
        html_lines.append(f"<td>{entry.get('program', '')}</td>")
        html_lines.append(f"<td>{entry.get('result', '')}</td>")
        html_lines.append(f"<td>{entry.get('omsas_gpa', '')}</td>")
        html_lines.append(f"<td>{entry.get('cars', '')}</td>")
        html_lines.append(f"<td>{entry.get('casper', '')}</td>")
        html_lines.append(f"<td>{entry.get('geography', '')}</td>")
        html_lines.append(f"<td>{entry.get('current_year', '')}</td>")
        html_lines.append("</tr>")

    html_lines.append("</table>")

    # Add a timestamp
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    html_lines.append(f"<p>Last updated: {timestamp} UTC</p>")
    html_lines.append("</body></html>")

    # Write to index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated index.html with {len(parsed_entries)} entries found.")

if __name__ == "__main__":
    fetch_and_generate()
