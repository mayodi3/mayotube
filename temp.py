from fastapi import FastAPI, Request, HTTPException, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
import aiohttp
import os

from pytubefix import YouTube
from pytubefix.cli import on_progress

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Initialize the FastAPI app
app = FastAPI()

# Serve static files (CSS, images, etc.)
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up Jinja2 templates
templates = Jinja2Templates(directory='templates')

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


# Route for the homepage
@app.get('/', response_class=HTMLResponse)
async def homepage(request: Request):
    # Display the homepage with no videos initially
    return templates.TemplateResponse('index.html', {'request': request})

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

# POST route to download videos (MP4 or MP3)
@app.post('/download')
async def download(request: Request, url: str = Form(...), type: str = Form(...)):
    yt = YouTube(url, on_progress_callback=on_progress)

    if type == "mp4":
        ys = yt.streams.get_highest_resolution()
        ys.download()
    elif type == "mp3":
        ys = yt.streams.get_audio_only()
        ys.download(mp3=True)

    # return {'message': 'Download completed'}
    return Response(status_code=204)
