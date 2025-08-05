import feedparser
import datetime
import heapq
from typing import List, Tuple
import yaml

def parse_date(date_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")

def get_latest_items(feed_urls: List[str], num_items: int, skip_item: str) -> List[Tuple[datetime.datetime, str, str, str, str]]:
    all_items = []
    
    for url in feed_urls:
        feed = feedparser.parse(url)
        channel_title = feed.feed.title
        channel_link = feed.feed.link
        
        for item in feed.entries[:10]:  # Get the last 10 items from each feed
            pub_date = parse_date(item.published)
            title = item.title
            link = item.link
 
            #Skip items with title "yaml_title"
            if title.strip().lower() == skip_item.strip().lower():
              continue
            
            # Use a tuple with negative timestamp for reverse sorting
            heapq.heappush(all_items, (-pub_date.timestamp(), pub_date, channel_title, channel_link, title, link))
    
    # Get the latest num_items
    return [heapq.heappop(all_items) for _ in range(min(num_items, len(all_items)))]

def generate_yaml_front_matter(title: str, author: str, name: str, weight: str, icon: str) -> str:
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yaml_content = f"""---
title: {title}
author: {author}
date: {current_date}
generated: {current_date}
type: page
menu:
    main:
        name: {name}
        weight: {weight}
        params:
            icon: {icon}
---

"""
    return yaml_content

def generate_markdown(items: List[Tuple[datetime.datetime, str, str, str, str]]) -> str:
    markdown = "| Blog | Title | Date |\n"
    markdown += "|------|-------|------|\n"
    for _, pub_date, channel_title, channel_link, title, link in items:
        markdown += f"| {channel_title} | [{title}]({link}) | {pub_date.strftime('%Y-%m-%d %H:%M:%S %Z')} |\n"
    return markdown

def main():
    # Read configuration from YAML file
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    
    feed_urls = config["feed_urls"]
    num_items = config["num_items"]
    output_file = config["output_file"]
    yaml_title = config["yaml_title"]
    yaml_author = config["yaml_author"]
    yaml_menu = config["yaml_menu"]
    yaml_weight = config["yaml_weight"]
    yaml_icon = config["yaml_icon"]
    
    latest_items = get_latest_items(feed_urls, num_items, yaml_title)
    
    yaml_front_matter = generate_yaml_front_matter(yaml_title, yaml_author, yaml_menu, yaml_weight, yaml_icon)
    markdown_content = generate_markdown(latest_items)
    
    full_content = yaml_front_matter + markdown_content
    
    with open(output_file, "w") as f:
        f.write(full_content)
    
    print(f"Markdown file '{output_file}' has been generated with YAML front matter and the latest {num_items} items.")

if __name__ == "__main__":
    main()
