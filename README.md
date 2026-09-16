# Guess the Weather 🌦️

A small game that quizzes you on **live, real-world weather**. Pick a mode and
it pulls current conditions from the internet, so the answers change through the
day — it's never the same quiz twice.

It comes in **two versions**:

- 🌐 **Web version** ([`index.html`](index.html)) — play it in a browser, no install.
  **▶ Play it live:** _enable GitHub Pages, then your link is_
  `https://<your-username>.github.io/<repo-name>/`
- 💻 **Console version** ([`weather_quiz.py`](weather_quiz.py)) — the original terminal game.

Both use the same keyless Open-Meteo API and offer the same four modes.

## Game modes

| Mode | What you do |
| --- | --- |
| **Guess the City** | See a live weather readout (conditions, temp, humidity, wind) and guess which of 4 cities it belongs to. |
| **Guess the Temperature** | Given a city, pick the temperature range it's currently in. |
| **Hotter City** | Two cities head-to-head — pick the warmer one right now. |
| **Weather Lookup** | Type any city name and see its current conditions. |

Quiz modes track your score across the rounds and give you a final tally.

### Difficulty levels

Pick **Easy / Medium / Hard** on the home screen (alongside the °C/°F and round
selectors). The level changes how *confusable* the answer choices are:

- **Guess the City** — Easy picks distractor cities from very different climates
  (using latitude as a proxy); Hard picks climatically similar ones.
- **Guess the Temperature** — Easy uses wide 10° buckets with far-apart options;
  Hard uses narrow 5° buckets with neighbouring ranges.
- **Hotter City** — Easy pairs cities with a big temperature gap; Hard picks the
  closest pair that still shows two different temperatures (so it stays fair).

## How the API is called

This project uses the free [**Open-Meteo**](https://open-meteo.com) API through
Python's [`requests`](https://requests.readthedocs.io/) library, via simple
HTTPS `GET` calls. Two endpoints are used: a **geocoding** endpoint
(`geocoding-api.open-meteo.com/v1/search`) that turns a city name into
latitude/longitude using the `name` parameter, and a **forecast** endpoint
(`api.open-meteo.com/v1/forecast`) that takes `latitude`, `longitude`, and a
`current=...` list of fields and returns the current weather. Responses come
back as **JSON**, which is parsed into a Python dict — temperature is a float in
°C, humidity an int in %, wind a float in km/h, and the sky condition an integer
**WMO weather code** that the app maps to readable text (e.g. `61` → "Slight
rain"). All of this is wrapped in [`weather_api.py`](weather_api.py) so the game
logic only deals with clean Python dictionaries.

## API key

**None needed.** Open-Meteo is free and keyless for non-commercial use, so there
are no secrets in this repo and nothing to configure. (A `.gitignore` is still
included to keep local junk and any future `.env` out of version control — good
habit even when there are no keys.)

## Running it

**Web version (easiest):** open [`index.html`](index.html) in any browser — just
double-click the file, or host it for free on **GitHub Pages** (repo Settings →
Pages → deploy from `main`, root) to get a shareable link. Because Open-Meteo
needs no key, it's safe to call directly from the browser with no backend.

**Console version:** you need Python 3.8+ and the `requests` package.

```bash
pip install -r requirements.txt
python3 weather_quiz.py
```

Then follow the on-screen menu.

> **Why a key-free API matters here:** never put a real API key in front-end
> JavaScript — anyone can read it in the browser's dev tools. The keyless
> Open-Meteo API is what makes a safe, backend-free web version possible.

## Handling things going wrong

The app is built to fail gracefully rather than crash:

- **Misspelled / unknown city** in Lookup → "Couldn't find a city called …".
- **Empty input** → politely re-prompts or returns to the menu.
- **No internet / dropped wifi / timeout** → every network call has a timeout
  and is caught, so you get "Network problem talking to the weather service"
  and land back on the menu instead of a traceback. (Try it: turn wifi off and
  play a round.)
- **Malformed API response** (missing fields) → reported as a clean message.

## Files

- [`index.html`](index.html) — the web version: self-contained HTML/CSS/JS, all four modes, calls Open-Meteo directly from the browser.
- [`weather_quiz.py`](weather_quiz.py) — the console game: menu, modes, scoring, input handling.
- [`weather_api.py`](weather_api.py) — the console API layer: geocoding, current weather, WMO code map, error handling.
- [`prompt_log.md`](prompt_log.md) — the AI tools and key prompts used to build this.

## AI prompt log

See [`prompt_log.md`](prompt_log.md) for the AI model and the key prompts that
shaped the implementation.
