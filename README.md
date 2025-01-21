# Yotube API Collector
## Author: Jayden Lee

## Objective
> Let's find out during what time of the day, morning, afternoon, or dinner, do we see the most gains in Likes among some of the most trendy music videos on Youtube.

While working on this project, I wanted to focus on learning and implementing the concepts of the following:
1. Accelerating the rate of GET Request using Python Multithread built-in [threading](https://docs.python.org/3/library/threading.html) module
2. Managing processed tabular-formatted data in RDBMS environment with [sqlite3](https://www.sqlite.org/)

## How to use
1. Clone this repository to your machine
```bash
git clone this_repo.git
```

2. Install the dependencies using `poetry`
```bash
poetry install
```

3. Access the entrypoint
```bash
cd cloned_proj # `cd` into the cloned repository

python main.py # Does not cache collected data in local filesystem
python main.py --local-save # Caches collected data under new folder named `data`(if not exists) in current repo

sh main.sh # Bash-scripted entrypoint

## I've automated this collection of data using cron for three times a day
0 9,16,22 * * * sh /path/to/main.sh
```

## Operation
In order to answer our question, we'll first need to collect content information about the music videos. Google provides [Open Source API endpoints for Developers](https://developers.google.com/youtube/v3) of which all you need to use it are your Google(Youtube) account and personalized token generated from the endpoint webpage. 

Once we gather all required credential and links, we will use Python `request` library to submit `GET` request to Youtube API endpoint and fetch the ids of all contents in source Youtube playlist

With the collected ids, we need to collect further information about the video content itself. For that, we'll yet again use another Youtube API endpoint for collecting video data, such as video title, publisher, like and comment counts, ..etc. For making this much of a HTTP request over the Internet(by default, we collect 100 contents at each run), I wanted to expedite this process through Asynchronous Processing and Python's `threading` library, in which allows us to assign th `GET` task to each thread(default `max_threads=6`)

The collected data then gets ingested into `sqlite3` database, which exists as a single file under `db` folder.

# Shortcomings
1. API collection is divided into two parts: one for collecting content information from Playlist API endpoint and another for collecting video information from Video API endpoint. While both are heavily I/O-based operations, I implemented asynchronous processing only on collecting Video API due to the validation steps I incorporated for the output generated from the Playlist API endpoint. To compensate, the Playlist collection was implemented with Generative functionalities
2. `sqlite3` is a reliable database software for small-scale project but to enlarge the scale of this project, I'd look into hosting a database in DBMS like `postgresql` or `mysql` environment for advanced database functionalities and more