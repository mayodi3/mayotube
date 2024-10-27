# mayotube

Set Up

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

create .env file in root project and add 
"YOUTUBE_API_KEY={YOUR YOUTUBE API KEY}" => This is Youtube V3 Api Key

uvicorn main:app --reload

open http://localhost:5000 on the browser
