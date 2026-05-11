# IPL 2025 Performance Analytics

## Overview

IPL 2025 Performance Analytics is a Power BI dashboard project focused on analyzing IPL 2025 data using batting, bowling, match, and player datasets. The dashboard provides interactive insights into team performance, player statistics, match outcomes, and tournament trends.

---

## Features

* Interactive Power BI dashboard
* Batting performance analysis
* Bowling performance analysis
* Team comparison insights
* Player profile analytics
* Match and venue statistics
* Dynamic KPIs and filters

---

## Tech Stack

* Power BI
* Power Query
* DAX
* CSV Datasets

---

## Datasets Used

### `batting_summary.csv`

Contains batting statistics including runs, balls, boundaries, and strike rate.

### `bowling_summary.csv`

Contains bowling metrics including wickets, economy, overs, and runs conceded.

### `match_summary.csv`

Contains match results, teams, venue, winner, and margin details.

### `player_info.csv`

Contains player information such as team, role, batting style, and bowling style.

---

## Dashboard Insights

* Top run scorers
* Highest strike rates
* Leading wicket takers
* Best economy bowlers
* Team win analysis
* Venue performance trends
* Match summary insights

---

## File Structure

```text
IPL-2025-Analytics/
│   ipl-25-analysis.pbix
│   LICENSE
│   raw data.xlsx
│   README.md
│   
├───collected data
│       batting_summary.csv
│       bowling_summary.csv
│       match_summary.csv
│       player_info.csv
│       
└───web scrapping codes
        batting_summary.py
        bowling_summary.py
        espncricinfo.csv
        player_info_scrapper.py
```

---

## How to Use

1. Open `ipl-25-analysis.pbix` in Power BI Desktop.
2. Load or refresh the datasets.
3. Explore the dashboard using filters and slicers.

---

## Project Description

Built an interactive IPL 2025 analytics dashboard using Power BI to analyze batting, bowling, player, and match performance data. Implemented data cleaning, modeling, DAX measures, and interactive visualizations for sports analytics insights.

---

## Author

Gobinathan K

## License

This project is licensed under the [MIT License](LICENSE).
