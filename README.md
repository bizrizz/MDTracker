# MDTracker

This project automatically fetches the latest posts from [r/premed](https://www.reddit.com/r/premed/) using Reddit's API (via PRAW) and generates a static HTML file (`index.html`) that is served with GitHub Pages.

## Setup Instructions

### 1. Create a Reddit App
- Go to [Reddit Apps](https://www.reddit.com/prefs/apps) and create a **script** app.
- Note your **Client ID** and **Client Secret**.

### 2. Configure GitHub Secrets
In your GitHub repository:
1. Navigate to **Settings > Secrets and variables > Actions**.
2. Add the following secrets:
   - `REDDIT_CLIENT_ID`: Your Reddit Client ID
   - `REDDIT_CLIENT_SECRET`: Your Reddit Client Secret

### 3. GitHub Pages Setup
- Go to your repository's **Settings > Pages**.
- Configure GitHub Pages to serve from the branch/folder that contains your `index.html` (typically the root of the `main` branch).

### 4. Automated Updates
The GitHub Actions workflow in `.github/workflows/update.yml` is set up to:
- Run the Python script every hour (or when manually triggered).
- Update the `index.html` file with the latest posts.
- Commit and push the changes automatically.

## Running Locally

To test locally:
1. Install dependencies:
   ```bash
   pip install praw
