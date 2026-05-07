import json
import csv
import os

file_exists = os.path.exists("recently_played.csv")

with open("recently_played.json") as file:
    response = json.load(file)

with open("recently_played.csv", "w", newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["song_name", "artist", "album"])

    if not file_exists or os.path.getsize("recently_played.csv"):
        writer.writeheader()
    for row in response:
        writer.writerow(row)