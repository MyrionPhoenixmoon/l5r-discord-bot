# L5R Bot

So you want to run this bot?

Well, strap in, bucko!

## Dependencies

The software is written for Python 3. (If you still run Python 2, please ask yourself what you're doing...)

All Python dependencies are specified in `requirements.txt`.

## How to get it running locally

```
# set up a virtual environment
python3 -m venv ./venv

# Install wheel (Hopefully not necessary anymore at some point in the future.)
./venv/bin/pip install wheel

# Install all dependencies
./venv/bin/pip install -r requirements.txt
```

## Docker

How to use the newly minted Dockerfile?

### Building the image
```
docker build -t l5r-discord-bot:latest .
```
### Running it
```
docker run l5r-discord-bot:latest .
```



# TODO

Write a proper setup.py, Pipfile, or even better pyproject.toml to make the tooling future-proof. 
