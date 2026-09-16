# AI Prompt Log

**AI tool used:** Claude (Anthropic) — the Claude Code assistant, Opus model.

I used Claude both to pressure-test my idea and to help write and test the code.
Below are the prompts/turns that mattered most, roughly in order.

### 1. Critiquing the concept
> "I want to create a basic 'Guess the Weather' game, which takes a public
> weather API and gives the user a multiple choice question asking what the
> current weather is for a certain location. The answers can be the location or
> the weather or a mix. Critique this idea, and what else do I need to know or
> consider before I start building."

This was the most important prompt. Claude pointed out that guessing the raw
*condition* is nearly a coin flip because real weather is mostly "clear/cloudy,"
and suggested flipping the flagship mode to **guess the city from a full
readout**, which a player can actually reason about. It also recommended
**Open-Meteo** specifically because it needs no API key — removing the risk of
committing a secret — and listed the failure cases the assignment grades.

### 2. Choosing scope
I decided to include **all three modes behind a menu** (Guess the City, Guess
the Temperature, Hotter City) plus a free-text lookup, as a **console Python
app** in its own repo.

### 3. Picking the API shape
Claude tested the two Open-Meteo endpoints live (geocoding + current forecast)
to confirm the exact JSON fields (`temperature_2m`, `weather_code`, etc.) and
the WMO weather-code system before writing any code.

### 4. Implementation guidance
> "Build a keyless Open-Meteo console quiz with a menu, three quiz modes plus a
> lookup, scoring, a °C/°F toggle, and graceful handling for a bad city, empty
> input, and the network being down."

Claude split the code into an API layer (`weather_api.py`) and a game layer
(`weather_quiz.py`), funneled every network call through one helper that
converts any failure into a single `WeatherError`, and mapped WMO codes to
readable text.

### 5. Testing the failure paths
I asked Claude to verify the "try to break it" cases from the assignment:
misspelled city, empty input, and a simulated network outage — confirming the
program prints a friendly message instead of crashing.
