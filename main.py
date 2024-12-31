import json

from config import CONFIG
from src import fetch_video_items
from src.utils import get_logger

SOURCE_API = 'https://www.googleapis.com/youtube/v3/playlistItems'
LOGGER_FP = ...

def main():
    logger = get_logger()
    logger.info("START")
    
    res = fetch_video_items(
        google_api_key=CONFIG['google_api_key'],
        youtube_playlist_id=CONFIG['youtube_playlist_id']
    )
    logger.info("END")

    return res

if __name__ == '__main__':
    res = main()
    print(json.dumps(res, indent=4))
    with open('data/vid_output_20241230.json', 'w') as f:
        f.write('')
        json.dump(res, f, indent=4)