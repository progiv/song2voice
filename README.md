Clone the repo first:
```
git@gitlab.com:hse-how-to-make-a-startup/projects/vocal-extractor-song-2-voice/song-to-voice-backend.git`
cd song-to-voice-backend
```
## Setup the environment(Do it once)
```
virtualenv -p python3 env && source env/bin/activate
```
Ensure that it is running correct python from virtual environment `env`:
```
which python && python --version
```
The output should look similar to this:
```
/home/auc/shad/mvp/song-to-voice-backend/env/bin/python
Python 3.7.4
```
Install requirements (like Django):
```
pip install -r requirements.txt
```
## Run the server
Now we are ready to run the server:
```
python manage.py runserver
```

## Running locally in docker container
*Note: it is an alternative way of doing steps from above.*

1. Install docker using [official guide](https://docs.docker.com/get-docker/)
1. Build the image with name song2voice: `docker image build -t song2voice .`
1. Run the container interactively: `docker run --rm -it -p 8000:8000 song2voice`
1. The server is now accessible at <localhost:8000>

Tip: Don't forget to rebuild image to see updates.
