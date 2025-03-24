import os
import praw
import re
from datetime import datetime

# Read credentials from environment variables
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = "MDTracker by Impossible_Ad346"

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Regex pattern to match the interview data fields in the post body.
# This pattern expects each field on its own line, in the format:
#
#   Time Stamp: 2025-03-15
#   Program: MD
#   Result: Invite
#   OMSAS GPA: 3.90
#   CARS: 129
#   Casper: ...
#   Geography: IP
#   Current year: 4th
#
# If users vary from this format, you may need a more flexible approach (e.g. line-by-line parsing).
pattern = re.compile(
    r"Time\s*Stamp:\s*(?P<time_stamp>.*?)\r?\n"
    r"Program:\s*(?P<program>.*?)\r?\n"
    r"Result:\s*(?P<result>.*?)\r?\n"
    r"OMSAS\s*GPA:\s*(?P<omsas_gpa>.*?)\r?\n"
    r"CARS:\s*(?P<cars>.*?)\r?\n"
    r"Casper:\s*(?P<casper>.*?)\r?\n"
    r"Geography:\s*(?P<geography>.*?)\r?\n"
    r"Current\s*year:\s*(?P<current_year>.*?)\r?\n",
    re.IGNORECASE | re.DOTALL
)

def parse_interview_data(post_text):
    """
    Search the post text for the interview template fields using our regex pattern.
    Returns a dictionary of the parsed data if found, otherwise None.
    """
    match = pattern.search(post_text)
    if match:
        return match.groupdict()
    return None

def fetch_and_generate():
    """
    1. Fetch recent posts from r/premed (time_filter='year' to limit to this cycle).
    2. Parse only those that contain the interview data template.
    3. Generate an HTML table with the relevant info.
    """
    subreddit = reddit.subreddit("premed")

    # You can adjust limit or use pagination. For demonstration, we fetch 200 newest posts from this year.
    # Or use subreddit.search(...) if you want to specifically look for "Interview" keywords, etc.
    recent_posts = subreddit.new(limit=200)

    # We'll store all successful parses here
    parsed_entries = []

    for post in recent_posts:
        # We only care about text posts (selftext). If it's a link/image post, selftext might be empty.
        if not post.selftext:
            continue
        
        data = parse_interview_data(post.selftext)
        if data:
            # If you only want "Invite" results, uncomment the next line:
            # if "invite" not in data["result"].lower():
            #     continue

            # Optionally filter by Program or year, etc.
            # e.g., if "MD" in data["program"]:

            # Keep track of which school the user is referencing in the title or text
            # (If each post includes the school name somewhere, you might parse that too.)

            parsed_entries.append({
                "title": post.title,
                "permalink": f"https://reddit.com{post.permalink}",
                **data
            })

    # Build an HTML table from parsed_entries
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
        html_lines.append(f"<td>{entry['time_stamp']}</td>")
        html_lines.append(f"<td>{entry['program']}</td>")
        html_lines.append(f"<td>{entry['result']}</td>")
        html_lines.append(f"<td>{entry['omsas_gpa']}</td>")
        html_lines.append(f"<td>{entry['cars']}</td>")
        html_lines.append(f"<td>{entry['casper']}</td>")
        html_lines.append(f"<td>{entry['geography']}</td>")
        html_lines.append(f"<td>{entry['current_year']}</td>")
        html_lines.append("</tr>")

    html_lines.append("</table>")

    # Add a timestamp
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    html_lines.append(f"<p>Last updated: {timestamp} UTC</p>")

    html_lines.append("</body></html>")

    # Write out the table to index.html (or another file)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated index.html with {len(parsed_entries)} parsed entries.")

if __name__ == "__main__":
    fetch_and_generate()
