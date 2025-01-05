#!/usr/bin/env python3
"""Script to download episodes dated weekly (but published monthly).

Friend wanted a script to automate download of Paws & Tails for a Linux media server.

Episodes are dated every seven days, uses a JSON file to track what has been downloaded.

Requires `requests`, but I think that's commonly found in the "system" Python packages.

"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

DATA_FILE = "pnt_data.json"
# Day of week that episodes are dated
EPISODE_DAY = 5  # Monday = 0, Sunday = 6
URL_PATTERN = (
    "https://insightforliving.swncdn.com/mp3/podcasts/PNT/PNT{:%Y.%m.%d}-PODCAST.mp3"
)


def main():
    try:
        folder = sys.argv[1]
    except IndexError:
        print("Usage: pnt_downloader.py FOLDER")
        return "Error: Output folder not specified"

    output_path = Path(folder)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    settings_file = output_path / DATA_FILE

    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
    else:
        settings = {}

    if "downloaded" in settings:
        last_downloaded = datetime.strptime(settings["downloaded"], "%Y-%m-%d").date()
        print(f"Last episode downloaded was {last_downloaded}")
        starting_date = last_downloaded + timedelta(days=7)
    else:
        print("No historical data found, getting episodes for this month")
        # start on the first and add days until we get to the day episodes are published
        starting_date = date.today().replace(day=1)
        while starting_date.weekday() != EPISODE_DAY:
            starting_date += timedelta(days=1)

    print(f"Starting from {starting_date}")
    processing = starting_date

    today = date.today()
    # the whole month is available at once, so load through end of month, not today
    while (processing.year, processing.month) <= (today.year, today.month):
        url = URL_PATTERN.format(processing)
        print(f"Getting {url}...")
        r = requests.get(url)

        if not r.ok:
            print(f"Failed to download episode for {processing}, quiting.")
            break

        audio_file = output_path / f"PNT{processing:%Y.%m.%d}-PODCAST.mp3"
        print(f"Writing to {audio_file}")
        with open(audio_file, "wb") as f:
            f.write(r.content)

        settings["downloaded"] = str(processing)
        processing += timedelta(days=7)

    print("Saving settings...")
    with open(output_path / DATA_FILE, "w") as f:
        json.dump(settings, f)


if __name__ == "__main__":
    sys.exit(main())
