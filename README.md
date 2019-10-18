# Oura Flask app

Guide to create an app with Flask and MySQL to request data from the Oura Cloud API.

See: https://mindatasleep.github.io/oura/



## Running the app locally


### Create oura_app_credentials.json in the root directory

```
{
    "CLIENT_ID": "YOUR_OURA_APP_CLIENT_ID",
    "CLIENT_SECRET": "YOUR_OURA_APP_CLIENT_SECRET"
}
```

### Execute app from a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

python3 -m app.app
```

## Host docs locally

```
cd docs/
bundle exec jekyll serve
```