# discord-rekordr

<!-- TOC -->

- [discord-rekordr](#discord-rekordr)
  - [Preparation](#preparation)
  - [Usage](#usage)

<!-- /TOC -->

## Preparation

- Go to [Discord Developers](https://discord.com/developers/applications/) and create a bot
- Go to `OAuth2` -> `URL Generator`
  - select `[scopes: bot && bot permissions: Administrator]`
  - then `Generated URL` -> Copy for the invitation link
- Go to `OAuth2` -> `General` -> `Default Authorization Link`
  - select `In-app Authorization` then provide the permissions
- Go to `Bot` and grab the token
- Create a `.env` file with `TOKEN="<token>"`

## Usage

Create and activate the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate.fish
```

Install the dependencies

```bash
pip install -r requirements.txt
```

Start the Rekordr Bot:

```bash
python main.py
```