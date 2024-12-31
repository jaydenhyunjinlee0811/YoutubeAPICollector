import json 
import requests

from .utils import get_logger

PLAYLIST_SOURCE_API = 'https://www.googleapis.com/youtube/v3/playlistItems'
VIDEO_SOURCE_API = 'https://www.googleapis.com/youtube/v3/videos'
NUM_PAGE_COLLECTED = 0

def fetch_video_items(
    google_api_key: str, 
    youtube_playlist_id: str,
    logger_fp: str=None
):
    output = list()
    logger = get_logger(logger_fp)

    # Collects data from all pages and store each page's data as Generator
    playlist_items_generator = _fetch_playlist_items(
        google_api_key=google_api_key,
        youtube_playlist_id=youtube_playlist_id
    )

    for i, item in enumerate(playlist_items_generator):
        if i >= 100:
            playlist_items_generator.close()
            break
        video_id = item['contentDetails']['videoId']
        raw_video_info = _fetch_video_item_page(google_api_key=google_api_key, video_id=video_id)
        output.append(_summarize_video_item(video_id=video_id, video_info=raw_video_info))
        logger.info('Page [%s]th data collection & transformation complete', str(i+1))

    return output

def _fetch_playlist_items(
    google_api_key: str, 
    youtube_playlist_id: str,
    page_token: str = None
):

    # Fetch one page and parse the output
    page_payload = _fetch_playlist_item_page(
        google_api_key,
        youtube_playlist_id,
        page_token
    )
    yield from page_payload['items'] # Collect current page's data
    
    # Effective way to work with pagination
    page_token = page_payload.get('nextPageToken', None) # `page_token` gets reset with next page's value after each page

    # Recursive call within the Generative function with new parameter values
    # At the last page, `page_token=None`, function passes this `if` statement and gets terminated
    if page_token is not None:
        yield from _fetch_playlist_items(google_api_key, youtube_playlist_id, page_token)

def _fetch_playlist_item_page(
    google_api_key: str, 
    youtube_playlist_id: str,
    page_token = None
):
    '''
    Returns dictionary of page info including data from all contents in the page
    By default, fetches 5 items for each page
    Items are stored under `items` key as list
    '''
    response = requests.get(PLAYLIST_SOURCE_API, params={
        'key':google_api_key, 
        'playlistId': youtube_playlist_id, 
        'part':'contentDetails',
        'pageToken': page_token
    })
    payload = json.loads(response.text)
    return payload

def _fetch_video_item_page(
    google_api_key: str, 
    video_id: str
):
    response = requests.get(VIDEO_SOURCE_API, params={
        'key':google_api_key, 
        'id': video_id, 
        'part': 'snippet,statistics'
    })
    res = json.loads(response.text)['items'].pop(0)
    return res

def _summarize_video_item(
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