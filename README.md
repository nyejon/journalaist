# JournalAIst - Your personal ghostwriter

Factory Network x {Tech: Berlin} AI Hackathon

Generate a personal story by uploading pictures and answering a few questions to remember events vividly in the future.


## Installation

Install the required packages with:
```
poetry install 
```

You can install poetry with:
```
curl -sSL https://install.python-poetry.org | python3 -
```

See the [poetry documentation](https://python-poetry.org/docs/basic-usage/) for more information.

## Usage

Run with:
```
streamlit run journalaist.py
```


This assumes you have your mistral API key as an env variable called `MISTRAL_API_KEY`. If not you will be prompted for the key. 