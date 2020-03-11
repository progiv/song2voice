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
DJANGO_DATABASE=test python manage.py runserver
```

## Running locally in docker container for debug
*Note: it is an alternative way of doing steps from above.*

1. (Once) Install docker using [official guide](https://docs.docker.com/get-docker/)
1. Build the image with name song2voice: `docker image build -t song2voice .`
1. Run the container interactively: `docker run -e DEBUG=True -e GOOGLE_APPLICATION_CREDENTIALS=get_voice.json --rm -it -p 80:80 song2voice`
1. The server is now accessible at <localhost:80>

## Deploy to Remote server
Prerequisites: it is expected that you already have setup keypair connection to your remote server on `<ROMITE IP>` with private key stored at `<PATH TO PRIVATRE SSH KEY>`. `<PATH TO ENV FILE>` should contain secrets like `SECRET_KEY`, `DJANGO_DATABASE=main` `DB_PASWORD` and `DB_HOST`
1. (Once)Setup docker environment on the remote machine. `docker-machine create --driver generic --generic-ip-address=<REMOTE IP> --generic-ssh-user=<REMOTE USERNAME> --generic-ssh-key <PATH TO PRIVATRE SSH KEY> s2v-ya`
1. Configure docker to run commands on remote host `eval $(docker-machine env s2v-ya)`
1. Build container as before. Notice: that it will be built on remote host using local source code.
1. Kill running instance and delete its data `docker kill back && docker container rm back`
1. Run new container in detached mode `docker run --env-file <PATH TO ENV FILE> -dp 80:80 --name back song2voice`
1. Unset environment variables that were set up in step 2 `eval $(docker-machine env -u)`
