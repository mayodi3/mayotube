from fastapi import HTTPException
import aiohttp
import os

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

async def search_videos(query: str, page_token: str | None = None):
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 10,
        'key': YOUTUBE_API_KEY
    }

    if page_token:
        params['pageToken'] = page_token

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                raise HTTPException(status_code=response.status, detail='YouTube API error')
            

# POST route to handle video searches
@app.post('/search', response_class=JSONResponse)
async def post_videos(request: Request, query: str = Form(...), page_token: str | None = Form(None)):
    # Perform the YouTube search with the provided query and page token
    results = await search_videos(query, page_token)

    if 'items' not in results:
        return JSONResponse({'message': 'No videos found'})

    nextPageToken = results.get('nextPageToken', None)  # Get the nextPageToken from the result

    new_videos = []
    for item in results['items']:
        snippet = item['snippet']
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        new_videos.append({
            'url': video_url,
            'title': snippet['title'],
            'uploaded': snippet['publishedAt'],
            'thumbnail': snippet['thumbnails']['high']['url'],
        })

    # Render the partial template for the videos
    videos_html = templates.TemplateResponse('_video_list.html', {
        'request': request,
        'videos': new_videos  # Only render the new videos
    }).body.decode('utf-8')

    # Return the JSON response
    return JSONResponse({
        'videos_html': videos_html,  # Return the HTML for the video cards
        'nextPageToken': nextPageToken  # Return the next page token if available
    })