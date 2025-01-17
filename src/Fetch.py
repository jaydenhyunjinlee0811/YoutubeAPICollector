import json
import os 
import requests
import threading
from queue import Queue

from .utils import get_logger

MAX_THREADS=6

class YoutubeAPIFetch:
    def __init__(
        self, 
        playlist_source_api: str, 
        video_source_api: str,
        logger_fp: str=None
    ):
        self.playlist_source_api = playlist_source_api
        self.video_source_api = video_source_api

        self.fetched_data: Queue = Queue()
        self.prcsd_data: Queue = Queue()
        self.data = list()
        self.logger = get_logger(logger_fp)

    def fetch(
        self,
        google_api_key: str, 
        youtube_playlist_id: str
    ):
        # Collects data from all pages and store each page's data as Generator
        playlist_items_generator = self._fetch_playlist_items(
            google_api_key=google_api_key,
            youtube_playlist_id=youtube_playlist_id
        )

        cnt=0
        cache = set()
        for item in playlist_items_generator:
            if cnt >= 100:
                playlist_items_generator.close()
                break

            try:
                video_id = item['contentDetails']['videoId']
            except KeyError:
                continue

            # Collect at least 100 unique set of videos
            if video_id in cache:
                print(video_id)
                continue
            self.fetched_data.put(video_id)
            cache.add(video_id)
            self.logger.info('Collected content of id: [%s] from playlist', video_id)
            cnt+=1

        del cache
        self.logger.info('Successfully collected [%s] video data', cnt)

        num_threads = min(os.cpu_count(), MAX_THREADS)
        threads = list()
        for _ in range(num_threads):
            thread = threading.Thread(target=self._async_fetch_video_item_page, args=(google_api_key,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        while not self.prcsd_data.empty():
            self.data.append(self.prcsd_data.get())
        # raw_video_info = self._async_fetch_video_item_page(google_api_key=google_api_key, video_id=video_id)
        # self.data.append(self._summarize_video_item(video_id=video_id, video_info=raw_video_info))
        # self.logger.info('Page [%s]th data collection & transformation complete', str(i+1))

################ Recurisve Generator ################

    def _fetch_playlist_items(
        self,
        google_api_key: str, 
        youtube_playlist_id: str,
        page_token: str = None
    ):

        # Fetch one page and parse the output
        page_payload = self._fetch_playlist_item_page(
            google_api_key,
            youtube_playlist_id,
            page_token
        )
        yield from page_payload['items'] # Collect current page's data
        
        # Effective way to work with pagination
        page_token = page_payload.get('nextPageToken', None) # `page_token` gets reset with next page's value after each page

        # Recursive call within the Generative function with new parameter values
        # At the last page, `page_token=None`, function passes this `if` statement and recurison stops
        if page_token is not None:
            yield from self._fetch_playlist_items(google_api_key, youtube_playlist_id, page_token)

    def _fetch_playlist_item_page(
        self,
        google_api_key: str, 
        youtube_playlist_id: str,
        page_token = None
    ):
        '''
        Returns dictionary of page info including data from all contents in the page
        By default, fetches 5 items for each page
        Items are stored under `items` key as list
        '''
        response = requests.get(self.playlist_source_api, params={
            'key':google_api_key, 
            'playlistId': youtube_playlist_id, 
            'part':'contentDetails',
            'pageToken': page_token
        })
        payload = json.loads(response.text)
        return payload

################ Multithreaded(Async) collection of video content data ################

    def _async_fetch_video_item_page(
        self,
        google_api_key: str
    ):
        while True:
            if self.fetched_data.empty():
                return
            else:
                video_id = self.fetched_data.get()
                self.logger.info('Requesting GET for content detail information about video with ID: [%s]', video_id)
                response = requests.get(self.video_source_api, params={
                    'key':google_api_key, 
                    'id': video_id, 
                    'part': 'snippet,statistics'
                })
                res = json.loads(response.text)['items'].pop(0)
                prcsd = self._summarize_video_item(video_id, res)
                self.prcsd_data.put(prcsd)
                continue

################ Parser function ################

    def _summarize_video_item(
        self,
        video_id: str,
        video_info: dict
    ):
        return {
            'videoId': video_id,
            'title': video_info['snippet'].get('title', 'N/A'),
            'publisedAt': video_info['snippet'].get('publishedAt', 'N/A'),
            'channel': video_info['snippet'].get('channelTitle', 'N/A'),
            'viewCount': int(video_info['statistics'].get('viewCount', 0)),
            'likeCount': int(video_info['statistics'].get('likeCount', 0)),
            'favoriteCount': int(video_info['statistics'].get('favoriteCount', 0)),
            'commentCount': int(video_info['statistics'].get('commentCount', 0))
        }