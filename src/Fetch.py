import json 
import requests

from .utils import get_logger

class YoutubeAPIFetch:
    def __init__(
        self, 
        playlist_source_api: str, 
        video_source_api: str,
        logger_fp: str=None
    ):
        self.playlist_source_api = playlist_source_api
        self.video_source_api = video_source_api

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

        for i, item in enumerate(playlist_items_generator):
            if i >= 100:
                playlist_items_generator.close()
                break
            video_id = item['contentDetails']['videoId']
            raw_video_info = self._fetch_video_item_page(google_api_key=google_api_key, video_id=video_id)
            self.data.append(self._summarize_video_item(video_id=video_id, video_info=raw_video_info))
            self.logger.info('Page [%s]th data collection & transformation complete', str(i+1))

################ Data Generator ################

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

################ GET Response functions ################

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

    def _fetch_video_item_page(
        self,
        google_api_key: str, 
        video_id: str
    ):
        response = requests.get(self.video_source_api, params={
            'key':google_api_key, 
            'id': video_id, 
            'part': 'snippet,statistics'
        })
        res = json.loads(response.text)['items'].pop(0)
        return res

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