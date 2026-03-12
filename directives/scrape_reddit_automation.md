# Directive: Scrape Top Reddit Posts for Automation

## Goal
Fetch the 100 most recent posts from `r/n8n` and `r/automation`, and extract the top 5 posts with the highest engagement from each subreddit.

## Tools/Scripts
- `execution/scrape_reddit.py`

## Inputs
- Subreddits: `r/n8n`, `r/automation`
- Limit: 100 recent posts
- Top N: 5 posts with the highest engagement

## Logic
Engagement is calculated by summing `score` and `num_comments`. 
The script will fetch the most recent posts, calculate engagement for each, sort them descending, and extract the top 5.

## Outputs
- An intermediate Markdown file in `.tmp/top_reddit_posts.md` containing the formatted list of the top 5 posts from each topic.

## Edge Cases
- Reddit API rate limits: The script uses a custom `User-Agent`. If it still fails, wait a few minutes.
- Empty subreddit or network error: Gracefully handle and record an error message in the output file instead of crashing.
