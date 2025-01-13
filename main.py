import json
import sys
import os
import datetime
import sqlite3
from argparse import ArgumentParser

from config import CONFIG
from src import YoutubeAPIFetch
from src.utils import get_logger

# Configuration
TODAY = datetime.datetime.now()
LOGGER_FP = ...

def main():
    # Command Line flags
    parser = ArgumentParser(
        description='Available flags for the script'
    )
    parser.add_argument(
		'--local-save',
		action='store_true', # If `--local-save` is not provided in command line, defaults to False
		help='Execute script with `--local-save` to save a copy of fetched data as .json file in project repo', # Description of this flag when executed with `-h` flag
        dest='local_save' # Name of the variable to store the value of this flag
	)
    args = parser.parse_args()

    logger = get_logger()
    logger.info("START")
    logger.info('RUNTIME: [%s]', TODAY)
    logger.info('LOCALLY SAVE FILE? [%s]', args.local_save)
    
    fetcher = YoutubeAPIFetch(
        playlist_source_api=CONFIG['PLAYLIST_SOURCE_API'],
        video_source_api=CONFIG['VIDEO_SOURCE_API']
    )
    fetcher.fetch(
        google_api_key=CONFIG['google_api_key'],
        youtube_playlist_id=CONFIG['youtube_playlist_id']
    )

    dt_str = datetime.datetime.strftime(
        TODAY, 
        '%Y%m%d_%H%M%S'
    )
    dt_db_folder = datetime.datetime.strftime(
        TODAY, 
        '%Y%m%d'
    )

    # Save fetched data as .json file if specified
    if args.local_save:
        with open(f'data/vid_output_{dt_str}.json', 'w') as f:
            f.write('')
            json.dump(fetcher.data, f, indent=4)

    # Ingest data into SQLite3 database
    # Create a central folder to store data collected at each runtime
    db_path = os.path.join(os.getcwd(), 'db', dt_db_folder)
    tbl_name = ''
    num_table_query = '''
    SELECT name FROM sqlite_master WHERE type='table';
    '''
    ingest_query = """
    INSERT INTO {} (videoId, title, publishedAt, channel, viewCount, likeCount, favoriteCount, commentCount) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    if not os.path.exists(db_path):
        _ = os.makedirs(db_path)

    with sqlite3.connect(os.path.join(db_path, 'YoutubeAPI.db')) as conn:
        try:
            cursor = conn.cursor()
            _ = cursor.execute(num_table_query)
            res = cursor.fetchall()
            if len(res) == 0:
                tbl_name = 'videosMorning'
            elif len(res) == 1:
                tbl_name = 'videosNoon'
            else:
                tbl_name = 'videosNight'

            # Create dest table
            with open('src/create_table.txt', 'r') as f:
                cursor.executescript(f.read().format(tbl_name=tbl_name))

            # Ingest data into dest table
            ingest_query = ingest_query.format(tbl_name)
            print(ingest_query)

            # Transform
            rows = [
                tuple(item.values()) for item in fetcher.data
            ]
            _ = cursor.executemany(ingest_query, rows)
            logger.info('[%d] records inserted into [%s]', cursor.rowcount, tbl_name)
            
        except sqlite3.Error:
            logger.error(sqlite3.Error, exc_info=True)
        # finally:
        #     if cursor:
        #         cursor.close()

        #     if conn:
        #         conn.close()
    
    logger.info("END")
if __name__ == '__main__':
    sys.exit(main())