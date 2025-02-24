import requests
import sys
import argparse
from collections import Counter
from typing import List, Dict
import time

class GitHubCommunityExplorer:
    def __init__(self, username: str, token: str = None):
        self.username = username
        self.headers = {'Authorization': f'token {token}'} if token else {}
        
    def get_user_interests(self) -> Dict:
        """Analyze user's starred repositories and their languages"""
        url = f"https://api.github.com/users/{self.username}/starred"
        starred_repos = self._fetch_github_data(url)
        
        languages = Counter()
        topics = Counter()
        
        for repo in starred_repos:
            if repo['language']:
                languages[repo['language']] += 1
            if repo['topics']:
                topics.update(repo['topics'])
                
        return {
            'languages': languages.most_common(5),
            'topics': topics.most_common(5)
        }
    
    def find_collaboration_opportunities(self) -> List[Dict]:
        """Find active repositories matching user's interests"""
        interests = self.get_user_interests()
        opportunities = []
        
        for language, _ in interests['languages']:
            query = f"language:{language} is:public is:open"
            url = f"https://api.github.com/search/repositories?q={query}&sort=updated"
            repos = self._fetch_github_data(url)
            
            for repo in repos['items'][:5]:
                if repo['open_issues_count'] > 0:
                    opportunities.append({
                        'name': repo['full_name'],
                        'description': repo['description'],
                        'language': repo['language'],
                        'open_issues': repo['open_issues_count'],
                        'url': repo['html_url']
                    })
        
        return opportunities
    
    def analyze_network_trends(self) -> Dict:
        """Analyze trending topics and languages in user's network"""
        url = f"https://api.github.com/users/{self.username}/following"
        following = self._fetch_github_data(url)
        
        network_languages = Counter()
        network_topics = Counter()
        
        for user in following[:5]:  # Analyze first 5 users to avoid rate limits
            repos_url = f"https://api.github.com/users/{user['login']}/repos"
            repos = self._fetch_github_data(repos_url)
            
            for repo in repos:
                if repo['language']:
                    network_languages[repo['language']] += 1
                if repo['topics']:
                    network_topics.update(repo['topics'])
        
        return {
            'trending_languages': network_languages.most_common(5),
            'trending_topics': network_topics.most_common(5)
        }
    
    def _fetch_github_data(self, url: str) -> Dict:
        """Helper method to fetch data from GitHub API with rate limit handling"""
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(0, reset_time - int(time.time()))
                if wait_time > 0:
                    print(f"\nRate limit exceeded. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self._fetch_github_data(url)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {str(e)}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Explore GitHub community and find collaboration opportunities',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('username', help='GitHub username to analyze')
    parser.add_argument('-t', '--token', help='GitHub personal access token (recommended)')
    
    args = parser.parse_args()
    
    explorer = GitHubCommunityExplorer(args.username, args.token)
    
    print(f"\nAnalyzing GitHub profile for {args.username}...")
    
    # Get user interests
    interests = explorer.get_user_interests()
    print("\n🎯 Your Interests:")
    print("\nTop Languages:")
    for lang, count in interests['languages']:
        print(f"  • {lang}: {count} repositories")
    print("\nTop Topics:")
    for topic, count in interests['topics']:
        print(f"  • {topic}: {count} repositories")
    
    # Find collaboration opportunities
    opportunities = explorer.find_collaboration_opportunities()
    print("\n🤝 Collaboration Opportunities:")
    for repo in opportunities:
        print(f"\n  • {repo['name']}")
        print(f"    Description: {repo['description']}")
        print(f"    Language: {repo['language']}")
        print(f"    Open Issues: {repo['open_issues']}")
        print(f"    URL: {repo['url']}")
    
    # Analyze network trends
    trends = explorer.analyze_network_trends()
    print("\n📈 Network Trends:")
    print("\nTrending Languages:")
    for lang, count in trends['trending_languages']:
        print(f"  • {lang}: {count} repositories")
    print("\nTrending Topics:")
    for topic, count in trends['trending_topics']:
        print(f"  • {topic}: {count} repositories")

if __name__ == "__main__":
    main()
