"""
weather_quiz.py
---------------
"Guess the Weather" -- a small console game built on the Open-Meteo API.

Run it with:   python3 weather_quiz.py

From a main menu the player can choose:
  1. Guess the City   -- see a live weather readout, guess which city it is
  2. Guess the Temp   -- see a city, guess its current temperature range
  3. Hotter City      -- two cities head to head, pick the warmer one
  4. Weather Lookup   -- type any city and see its current conditions
  5. Settings         -- switch between Celsius/Fahrenheit and set round count

All the weather comes from live current-conditions data, so the questions
change through the day. Network and bad-input problems are caught and reported
politely instead of crashing.
"""

import random

import weather_api as api

# ---------------------------------------------------------------------------
# City data
# ---------------------------------------------------------------------------
# A curated, climate-diverse set of cities with hard-coded coordinates. Using
# fixed coords means the quiz modes need only ONE weather call per question and
# never depend on the geocoding endpoint -- fast and reliable. The spread of
# climates (desert, arctic, tropical, temperate) is what makes the guessing
# genuinely reason-able rather than random.
CITIES = [
    {"name": "Reykjavik",     "country": "Iceland",       "lat": 64.15, "lon": -21.90},
    {"name": "Anchorage",     "country": "USA",           "lat": 61.22, "lon": -149.90},
    {"name": "Oslo",          "country": "Norway",        "lat": 59.91, "lon": 10.75},
    {"name": "Moscow",        "country": "Russia",        "lat": 55.76, "lon": 37.62},
    {"name": "London",        "country": "UK",            "lat": 51.51, "lon": -0.13},
    {"name": "Berlin",        "country": "Germany",       "lat": 52.52, "lon": 13.40},
    {"name": "Vancouver",     "country": "Canada",        "lat": 49.28, "lon": -123.12},
    {"name": "Toronto",       "country": "Canada",        "lat": 43.65, "lon": -79.38},
    {"name": "New York",      "country": "USA",           "lat": 40.71, "lon": -74.01},
    {"name": "Denver",        "country": "USA",           "lat": 39.74, "lon": -104.99},
    {"name": "Chicago",       "country": "USA",           "lat": 41.88, "lon": -87.63},
    {"name": "Seattle",       "country": "USA",           "lat": 47.61, "lon": -122.33},
    {"name": "Tokyo",         "country": "Japan",         "lat": 35.68, "lon": 139.69},
    {"name": "Beijing",       "country": "China",         "lat": 39.90, "lon": 116.40},
    {"name": "Rome",          "country": "Italy",         "lat": 41.90, "lon": 12.50},
    {"name": "Madrid",        "country": "Spain",         "lat": 40.42, "lon": -3.70},
    {"name": "Cairo",         "country": "Egypt",         "lat": 30.04, "lon": 31.24},
    {"name": "Dubai",         "country": "UAE",           "lat": 25.20, "lon": 55.27},
    {"name": "Mumbai",        "country": "India",         "lat": 19.08, "lon": 72.88},
    {"name": "Delhi",         "country": "India",         "lat": 28.61, "lon": 77.21},
    {"name": "Bangkok",       "country": "Thailand",      "lat": 13.76, "lon": 100.50},
    {"name": "Singapore",     "country": "Singapore",     "lat": 1.35,  "lon": 103.82},
    {"name": "Nairobi",       "country": "Kenya",         "lat": -1.29, "lon": 36.82},
    {"name": "Cape Town",     "country": "South Africa",  "lat": -33.92, "lon": 18.42},
    {"name": "Lima",          "country": "Peru",          "lat": -12.05, "lon": -77.04},
    {"name": "Mexico City",   "country": "Mexico",        "lat": 19.43, "lon": -99.13},
    {"name": "Buenos Aires",  "country": "Argentina",     "lat": -34.60, "lon": -58.38},
    {"name": "Sydney",        "country": "Australia",     "lat": -33.87, "lon": 151.21},
    {"name": "Honolulu",      "country": "USA",           "lat": 21.31, "lon": -157.86},
    {"name": "Phoenix",       "country": "USA",           "lat": 33.45, "lon": -112.07},
]

# Letters used for multiple-choice options.
LETTERS = ["A", "B", "C", "D"]


# ---------------------------------------------------------------------------
# Settings (the user-adjustable parameters)
# ---------------------------------------------------------------------------
class Settings:
    """Holds the player's chosen options for the session."""

    def __init__(self):
        self.units = "C"     # "C" or "F"
        self.rounds = 5      # questions per quiz game

    def format_temp(self, temp_c):
        """Format a Celsius temperature in the player's chosen unit."""
        if self.units == "F":
            return f"{api.c_to_f(temp_c):.0f} F"
        return f"{temp_c:.0f} C"


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
def read_line(prompt):
    """Read a line of input, treating Ctrl-C / Ctrl-D as 'quit'.

    Returns the typed string, or None if the player wants to bail out.
    """
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print()  # tidy newline after ^C
        return None


def prompt_choice(options):
    """Ask the player to pick from a list of option strings.

    `options` is a list like ["Tokyo", "Cairo", ...]; they are shown as A, B,
    C, D. Accepts the letter ("b"/"B") or the number ("2"). Reprompts on empty
    or invalid input. Returns the chosen zero-based index, or None to quit.
    """
    for i, text in enumerate(options):
        print(f"  {LETTERS[i]}. {text}")

    while True:
        raw = read_line("Your answer (letter, or 'q' to quit): ")
        if raw is None:
            return None
        choice = raw.strip().lower()

        if choice == "" :
            print("  Please type a letter.")
            continue
        if choice == "q":
            return None

        # Accept a letter (a-d).
        if choice in [letter.lower() for letter in LETTERS[:len(options)]]:
            return [letter.lower() for letter in LETTERS].index(choice)

        # Accept a number (1-based).
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(options):
                return num - 1

        print("  Not a valid choice -- try one of the letters shown.")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def print_weather_card(title, weather, settings, show_title=True):
    """Print a formatted current-conditions block."""
    print("-" * 40)
    if show_title:
        print(f"  {title}")
    print(f"  Conditions : {weather['description']}")
    print(f"  Temperature: {settings.format_temp(weather['temp_c'])} "
          f"(feels like {settings.format_temp(weather['feels_c'])})")
    print(f"  Humidity   : {weather['humidity']}%")
    print(f"  Wind       : {weather['wind_kmh']:.0f} km/h")
    print("-" * 40)


# ---------------------------------------------------------------------------
# Game modes
# ---------------------------------------------------------------------------
def mode_guess_city(settings):
    """Mode 1: show a live weather readout, guess which city it belongs to."""
    print("\n=== Guess the City ===")
    print("Read the live weather below and pick which city it's from.\n")

    score = 0
    played = 0
    for rnd in range(1, settings.rounds + 1):
        picks = random.sample(CITIES, 4)      # 4 distinct cities
        answer = random.choice(picks)         # one is the real location

        try:
            weather = api.get_current_weather(answer["lat"], answer["lon"])
        except api.WeatherError as exc:
            print(f"[Skipping this round] {exc}\n")
            continue

        played += 1
        print(f"Round {rnd} of {settings.rounds}")
        print_weather_card("Mystery city weather", weather, settings, show_title=True)

        labels = [f"{c['name']}, {c['country']}" for c in picks]
        idx = prompt_choice(labels)
        if idx is None:
            print("Leaving the game early.")
            break

        if picks[idx] is answer:
            print("Correct!\n")
            score += 1
        else:
            print(f"Nope -- it was {answer['name']}, {answer['country']}.\n")

    report_score(score, played)


def temp_bucket(temp_c):
    """Return the label of the temperature bucket a Celsius value falls in."""
    if temp_c < 0:
        return "Below 0 C"
    if temp_c < 10:
        return "0 to 10 C"
    if temp_c < 20:
        return "10 to 20 C"
    if temp_c < 30:
        return "20 to 30 C"
    return "Above 30 C"


# The full ordered set of buckets, used to build multiple-choice distractors.
ALL_BUCKETS = ["Below 0 C", "0 to 10 C", "10 to 20 C", "20 to 30 C", "Above 30 C"]


def mode_guess_temp(settings):
    """Mode 2: show a city, guess which temperature range it's currently in."""
    print("\n=== Guess the Temperature ===")
    print("Given a city, pick the range its current temperature falls in.\n")

    score = 0
    played = 0
    for rnd in range(1, settings.rounds + 1):
        city = random.choice(CITIES)

        try:
            weather = api.get_current_weather(city["lat"], city["lon"])
        except api.WeatherError as exc:
            print(f"[Skipping this round] {exc}\n")
            continue

        played += 1
        correct = temp_bucket(weather["temp_c"])

        # Build 4 options: the correct bucket plus 3 random other buckets.
        distractors = [b for b in ALL_BUCKETS if b != correct]
        options = random.sample(distractors, 3) + [correct]
        random.shuffle(options)

        print(f"Round {rnd} of {settings.rounds}")
        print(f"What's the current temperature in {city['name']}, {city['country']}?")
        idx = prompt_choice(options)
        if idx is None:
            print("Leaving the game early.")
            break

        if options[idx] == correct:
            print(f"Correct! It's {settings.format_temp(weather['temp_c'])}.\n")
            score += 1
        else:
            print(f"Not quite -- it's {settings.format_temp(weather['temp_c'])} "
                  f"({correct}).\n")

    report_score(score, played)


def mode_hotter_city(settings):
    """Mode 3: two cities head to head -- pick the warmer one right now."""
    print("\n=== Hotter City ===")
    print("Two cities. Pick whichever is warmer right now.\n")

    score = 0
    played = 0
    for rnd in range(1, settings.rounds + 1):
        # Pick two distinct cities whose temps differ (re-pick on a rare tie).
        weather_a = weather_b = None
        city_a = city_b = None
        for _attempt in range(5):
            city_a, city_b = random.sample(CITIES, 2)
            try:
                weather_a = api.get_current_weather(city_a["lat"], city_a["lon"])
                weather_b = api.get_current_weather(city_b["lat"], city_b["lon"])
            except api.WeatherError as exc:
                print(f"[Skipping this round] {exc}\n")
                weather_a = None
                break
            if weather_a["temp_c"] != weather_b["temp_c"]:
                break  # a clear winner exists
        if weather_a is None or weather_b is None:
            continue
        if weather_a["temp_c"] == weather_b["temp_c"]:
            continue  # couldn't find a non-tie; skip this round

        played += 1
        print(f"Round {rnd} of {settings.rounds}: Which city is warmer right now?")
        options = [
            f"{city_a['name']}, {city_a['country']}",
            f"{city_b['name']}, {city_b['country']}",
        ]
        idx = prompt_choice(options)
        if idx is None:
            print("Leaving the game early.")
            break

        chosen_is_a = (idx == 0)
        a_is_hotter = weather_a["temp_c"] > weather_b["temp_c"]
        if chosen_is_a == a_is_hotter:
            print("Correct!", end="  ")
            score += 1
        else:
            print("Wrong!", end="  ")
        print(f"{city_a['name']}: {settings.format_temp(weather_a['temp_c'])}  |  "
              f"{city_b['name']}: {settings.format_temp(weather_b['temp_c'])}\n")

    report_score(score, played)


def mode_lookup(settings):
    """Mode 4: type any city and see its current conditions.

    This is where free-text input, empty input, and misspelled/not-found
    cities are exercised -- it uses the geocoding endpoint.
    """
    print("\n=== Weather Lookup ===")
    name = read_line("Enter a city name (blank to go back): ")
    if name is None:
        return
    name = name.strip()
    if name == "":
        print("No city entered -- back to the menu.")
        return

    try:
        place = api.geocode_city(name)
    except api.WeatherError as exc:
        print(f"Couldn't reach the weather service: {exc}")
        return

    if place is None:
        print(f"Couldn't find a city called '{name}'. Check the spelling and try again.")
        return

    try:
        weather = api.get_current_weather(place["lat"], place["lon"])
    except api.WeatherError as exc:
        print(f"Couldn't reach the weather service: {exc}")
        return

    title = f"{place['name']}, {place['country']}".strip(", ")
    print_weather_card(title, weather, settings, show_title=True)


def mode_settings(settings):
    """Mode 5: change units and rounds per game."""
    print("\n=== Settings ===")
    print(f"Current units: {'Fahrenheit' if settings.units == 'F' else 'Celsius'}")
    print(f"Rounds per game: {settings.rounds}")

    print("\nTemperature units:")
    idx = prompt_choice(["Celsius", "Fahrenheit"])
    if idx == 0:
        settings.units = "C"
    elif idx == 1:
        settings.units = "F"

    raw = read_line("Rounds per game (1-20, blank to keep current): ")
    if raw is not None and raw.strip().isdigit():
        num = int(raw.strip())
        if 1 <= num <= 20:
            settings.rounds = num
        else:
            print("Out of range -- keeping the current value.")

    print(f"Saved: {'Fahrenheit' if settings.units == 'F' else 'Celsius'}, "
          f"{settings.rounds} rounds.")


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def report_score(score, played):
    """Print the end-of-game tally with a light comment."""
    if played == 0:
        print("No rounds were completed (the weather service may be unreachable).")
        return

    print(f"Final score: {score} / {played}")
    ratio = score / played
    if ratio == 1:
        print("Perfect round -- you really know your weather!")
    elif ratio >= 0.6:
        print("Nice work -- sharp guessing.")
    elif ratio > 0:
        print("Not bad -- the planet is a big place.")
    else:
        print("Rough one! The atmosphere had other plans.")
    print()


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------
def main():
    settings = Settings()
    print("=" * 44)
    print("        GUESS THE WEATHER")
    print("   Live current-conditions quiz game")
    print("      Data from Open-Meteo (no API key)")
    print("=" * 44)

    modes = {
        "1": mode_guess_city,
        "2": mode_guess_temp,
        "3": mode_hotter_city,
        "4": mode_lookup,
        "5": mode_settings,
    }

    while True:
        print("\nMain menu:")
        print("  1. Guess the City")
        print("  2. Guess the Temperature")
        print("  3. Hotter City")
        print("  4. Weather Lookup (type any city)")
        print("  5. Settings")
        print("  6. Quit")

        choice = read_line("Pick an option (1-6): ")
        if choice is None:
            choice = "6"  # Ctrl-C at the menu quits
        choice = choice.strip()

        if choice == "6" or choice.lower() == "q":
            print("Thanks for playing -- stay dry out there!")
            break
        elif choice in modes:
            modes[choice](settings)
        else:
            print("Please choose a number from 1 to 6.")


if __name__ == "__main__":
    main()
