import os
import json
import praw
import openai
from datetime import datetime

# --- Configuration: Load credentials from environment variables ---
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT", "MDTracker by Impossible_Ad346")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# --- Initialize Reddit via PRAW ---
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=USER_AGENT
)

# --- Define the OpenAI extraction function ---
def extract_fields_with_openai(text):
    """
    Use the OpenAI API to extract interview data from the given text.
    The AI will return a JSON object with the following keys:
      - time_stamp
      - program
      - result
      - omsas_gpa
      - cars
      - casper
      - geography
      - current_year
    For any missing fields, the AI will return "N/A".
    """
    prompt = f"""
You are an expert data extractor for medical school interview statistics. Extract the following fields from the provided text:
1) time_stamp (the date or time information)
2) program (e.g., MD, MD/PhD, etc.)
3) result (e.g., Invite, Rejection)
4) omsas_gpa (if provided)
5) cars (if provided)
6) casper (if provided)
7) geography (e.g., IP/OOP)
8) current_year (e.g., 3rd, 4th, etc.)

If any field is missing, use "N/A" as its value.
Return the answer as valid JSON with keys exactly as above.

Text:
\"\"\"{text}\"\"\"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use a valid model
            messages=[
                {"role": "system", "content": "Extract interview data from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=150
        )
        # Extract the assistant's reply (assumed to be JSON)
        reply = response.choices[0].message["content"].strip()
        data = json.loads(reply)
        return data
    except Exception as e:
        print(f"Error extracting with OpenAI: {e}")
        return None

# --- Main function: Scrape Reddit and extract interview data ---
def main():
    # For example, fetch the latest 50 posts from r/premed
    subreddit = reddit.subreddit("premed")
    posts = subreddit.new(limit=50)
    
    extracted_entries = []

    # Process each post and its comments if they contain keywords
    for post in posts:
        # Check post's selftext for relevant keywords (case-insensitive)
        if post.selftext and ("interview" in post.selftext.lower() or "invite" in post.selftext.lower()):
            print(f"Processing post: {post.title}")
            extraction = extract_fields_with_openai(post.selftext)
            if extraction:
                extraction["source"] = f"Post: {post.title}"
                extraction["permalink"] = f"https://reddit.com{post.permalink}"
                extracted_entries.append(extraction)
        
        # Process comments in the post
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            if comment.body and ("interview" in comment.body.lower() or "invite" in comment.body.lower()):
                print(f"Processing comment by {comment.author}")
                extraction = extract_fields_with_openai(comment.body)
                if extraction:
                    extraction["source"] = f"Comment in post: {post.title}"
                    extraction["permalink"] = f"https://reddit.com{comment.permalink}"
                    extracted_entries.append(extraction)

    # --- Generate an HTML file with the extracted data ---
    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Extracted Interview Data</title>",
        "<style>",
        "  body { font-family: Arial, sans-serif; margin: 20px; }",
        "  table { border-collapse: collapse; width: 100%; }",
        "  th, td { border: 1px solid #ccc; padding: 8px; }",
        "  th { background: #f4f4f4; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Extracted Interview Data from r/premed</h1>",
        "<table>",
        "<tr>",
        "  <th>Source</th>",
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
    
    for entry in extracted_entries:
        html_lines.append("<tr>")
        html_lines.append(f"<td>{entry.get('source', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('time_stamp', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('program', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('result', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('omsas_gpa', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('cars', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('casper', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('geography', 'N/A')}</td>")
        html_lines.append(f"<td>{entry.get('current_year', 'N/A')}</td>")
        html_lines.append(f"<td><a href='{entry.get('permalink', '#')}' target='_blank'>Link</a></td>")
        html_lines.append("</tr>")
    
    html_lines.append("</table>")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    html_lines.append(f"<p>Last updated: {timestamp} UTC</p>")
    html_lines.append("</body></html>")
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    
    print(f"Generated index.html with {len(extracted_entries)} entries found.")

if __name__ == "__main__":
    main()
