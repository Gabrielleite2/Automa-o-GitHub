import urllib.request
import urllib.error
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

# Layer 3: Execution script
# This script fetches the 100 most recent posts from specified subreddits and extracts the top 5 by engagement.

os.makedirs('.tmp', exist_ok=True)
LOG_FILE = os.path.join('.tmp', 'automation_logs.jsonl')

SUBREDDITS = ['n8n', 'automation']
LIMIT = 100
TOP_N = 5

def log_event(level: str, message: str) -> None:
    timestamp = datetime.now().isoformat()
    log_entry = json.dumps({
        "timestamp": timestamp,
        "level": level,
        "script": "scrape_reddit",
        "message": message
    })
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def fetch_reddit_posts(subreddit: str, limit: int) -> List[Dict[str, Any]]:
    log_event("INFO", f"Fetching up to {limit} recent posts from r/{subreddit}...")
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    
    # Use a custom user agent to avoid Reddit's default block for python-urllib
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPE-Script/1.0',
            'Accept': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'data' in data and 'children' in data['data']:
                return [child['data'] for child in data['data']['children']]
            return []
    except Exception as e:
        log_event("ERROR", f"Error fetching from r/{subreddit}: {e}")
        return []

def calculate_engagement(post: Dict[str, Any]) -> int:
    return post.get('score', 0) + post.get('num_comments', 0)

def fetch_author_icon(author: str) -> str:
    if not author or author == '[deleted]': return ""
    url = f"https://www.reddit.com/user/{author}/about.json"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 OPE-Agent/1.1'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            icon = data.get('data', {}).get('icon_img', '')
            if icon:
                # Remove URL query params like ?width=256
                return icon.split('?')[0]
        return ""
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "" # User suspended/deleted
        log_event("WARNING", f"Error fetching avatar for {author}: {e}")
        return ""
    except Exception as e:
        return ""

def main() -> None:
    results: Dict[str, List[Dict[str, Any]]] = {}
    
    for sub in SUBREDDITS:
        posts = fetch_reddit_posts(sub, LIMIT)
        if not posts:
            log_event("WARNING", f"No posts retrieved or API error for r/{sub}.")
            results[sub] = []
            continue
            
        log_event("INFO", f"Retrieved {len(posts)} posts for r/{sub}. Sorting by engagement (score + comments)...")
        posts.sort(key=calculate_engagement, reverse=True)
        
        # Using list comprehension to bypass Pyre2 strict slice __getitem__ overload issues
        top_posts = [posts[i] for i in range(min(TOP_N, len(posts)))]
        
        # Fetch real author avatars for the top posts
        log_event("INFO", f"Fetching real author avatars for top {len(top_posts)} posts in r/{sub}...")
        for p in top_posts:
            author = p.get('author', '')
            icon_url = fetch_author_icon(author)
            p['author_icon_url'] = icon_url
            time.sleep(1.5) # Be gentle with Reddit API
            
        results[sub] = top_posts
        
    output_path = os.path.join('.tmp', 'top_reddit_posts.md')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Top Engaged Reddit Posts\n\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        for sub, posts in results.items():
            f.write(f"## r/{sub}\n")
            if not posts:
                f.write("*No posts found or API error.*\n\n")
                continue
                
            for i, post in enumerate(posts, 1):
                title = post.get('title', 'Unknown Title').replace('\n', ' ')
                score = post.get('score', 0)
                comments = post.get('num_comments', 0)
                engagement = score + comments
                url = post.get('url', '')
                permalink = f"https://www.reddit.com{post.get('permalink', '')}"
                
                f.write(f"### {i}. {title}\n")
                f.write(f"- **Engagement:** {engagement} (Score: {score}, Comments: {comments})\n")
                if url and not url.startswith('https://www.reddit.com'):
                    f.write(f"- **External URL:** {url}\n")
                f.write(f"- **Reddit Thread:** {permalink}\n\n")

    # NEW: Also dump structured results to a JSON file for the dashboard
    json_output_path = os.path.join('.tmp', 'top_reddit_posts.json')
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
                
    log_event("SUCCESS", f"Execution complete. Results successfully saved to {output_path} and {json_output_path}")

if __name__ == "__main__":
    log_event("INFO", "Started scrape_reddit execution.")
    main()
