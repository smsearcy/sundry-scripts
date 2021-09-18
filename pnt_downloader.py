#!/usr/bin/env python3
"""Script to download episodes dated weekly (but published monthly).

Friend wanted a script to automate download of Paws & Tails for a Linux media server.

Episodes are dated every seven days, uses a JSON file to track what has been downloaded.

Requires `urllib3`, but I think that's commonly found in the "system" Python packages.

"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import urllib3

BASE_DATE = date(2021, 9, 4)
DATA_FILE = "pnt_data.json"
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
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
        settings = {}

    if "downloaded" in settings:
        last_downloaded = datetime.strptime(settings["downloaded"], "%Y-%m-%d").date()
        print(f"Last episode downloaded was {last_downloaded}")
        processing = last_downloaded + timedelta(days=7)
    else:
        # go back a couple weeks
        elapsed_time = date.today() - BASE_DATE
        weeks = int(elapsed_time.days / 7) - 2
        processing = BASE_DATE + timedelta(days=weeks * 7)
        print(f"Starting from {processing}")

    http = urllib3.PoolManager()
    today = date.today()
    # the whole month is available at once, so load through next month
    while (processing.year, processing.month) <= (today.year, today.month):
        url = URL_PATTERN.format(processing)
        print(f"Getting {url}...")
        r = http.request("GET", url)

        if r.status != 200:
            print(f"Failed to download episode for {processing}, quiting.")
            break

        audio_file = output_path / f"PNT{processing:%Y.%m.%d}-PODCAST.mp3"
        print(f"Writing to {audio_file}")
        with open(audio_file, "wb") as f:
            f.write(r.data)

        settings["downloaded"] = str(processing)
        processing += timedelta(days=7)

    print("Saving settings...")
    with open(output_path / DATA_FILE, "w") as f:
        json.dump(settings, f)


if __name__ == "__main__":
    sys.exit(main())
