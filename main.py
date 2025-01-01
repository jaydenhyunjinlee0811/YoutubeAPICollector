import json
import sys
import datetime

from config import CONFIG
from src import YoutubeAPIFetch
from src.utils import get_logger

LOGGER_FP = ...

def main():
    logger = get_logger()
    logger.info("START")
    
    fetcher = YoutubeAPIFetch(
        playlist_source_api=CONFIG['PLAYLIST_SOURCE_API'],
        video_source_api=CONFIG['VIDEO_SOURCE_API']
    )
    fetcher.fetch(
        google_api_key=CONFIG['google_api_key'],
        youtube_playlist_id=CONFIG['youtube_playlist_id']
    )

    # Save local copy
    dt_str = datetime.datetime.strftime(
        datetime.datetime.now(), 
        '%Y%m%d_%H%M%S'
    )
    with open(f'data/vid_output_{dt_str}.json', 'w') as f:
        f.write('')
        json.dump(fetcher.data, f, indent=4)

    logger.info("END")
if __name__ == '__main__':
    sys.exit(main())