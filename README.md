# API Collector
## Author: Jayden Lee

There are two main things I wanted to familiarize with working on this project:
1. Memory-efficient collection of data using Python Generator
2. Accelerating the rate of GET Request using Python Multithread built-in `threading` module
3. Managing processed tabular-formatted data in RDBMS environment with `sqlite3`

Metrics of interest:
1. Among the three timelines, when do we gain the most likes
2. Compare each TOD(Time Of Day) table to that of previous day's(cache/), in which TOD do we observe the most amount of gain Like counts?