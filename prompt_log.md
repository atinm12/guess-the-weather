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

### 6. Making a browser-playable web version
> "Make a web version so I am able to play it in a browser."

Claude built a self-contained `index.html` (HTML/CSS/JS) that ports all four
modes and calls Open-Meteo directly from the browser — and flagged *why* that's
safe here: because the API is keyless there's no secret to expose in front-end
code (the classic trap of putting an API key in browser JS). It then hosted it
on **GitHub Pages** so there's a live, shareable link.

### 7. Redesigning the UI with an illustrated theme
> "Make the UI friendly, colorful, illustrated … a scenic background (blue sky,
> sun, clouds, hills), soft rounded cards, playful icons … keep the same
> structure and functionality."

Claude rebuilt the interface with a hand-drawn SVG scene (sky, sun, clouds,
layered hills), four pastel color-coded mode cards with icons and arrow buttons,
rounded Fredoka/Nunito fonts, and pill-style selectors — while leaving all the
game logic untouched. A follow-up prompt ("explicitly prompt the user to pick a
game mode — it's confusing what the four options are") added a clear
"Choose a game mode to play" heading above the cards.

### 8. Adding difficulty levels
> "Add easy, medium, and hard levels … and make the questions accordingly."

Before coding, Claude asked what "difficulty" should actually change and I chose
**how confusable the answer choices are**. It implemented this per mode: Guess
the City picks distractor cities by climate similarity (using latitude as a
proxy), Guess the Temperature switches from wide 10° buckets to narrow 5° ones,
and Hotter City picks city pairs with a large gap (easy) down to the smallest
still-distinguishable gap (hard). It also made a point of keeping Hard fair —
never showing two cities with the same rounded temperature.
