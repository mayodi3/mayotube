# mayotube

Set Up

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

create .env file in root project and add 
"YOUTUBE_API_KEY={YOUR YOUTUBE API KEY}"

uvicorn main:app --reload
