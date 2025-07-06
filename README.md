# Tautulli to SensCritique CSV Converter

This script converts CSV files containing movie and TV show data from Tautulli format to SensCritique format.

## Requirements

- Python 3.7+
- InquirerPy library

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Get The CSV from Tautulli

- Go to Libraries > <your-library> > Export > Export metadata
- Set all export level to 0
- Set Custom Metadata Fiels to `title` `userRating` `viewCount` `year`

## Usage

The script takes CSV files with the following columns:
- `title`: Movie/TV show title
- `userRating`: User rating (numeric)
- `viewCount`: Number of times viewed
- `year`: Release year

### Command Line Arguments

```bash
python convert_csv.py [--movies MOVIES_CSV] [--tv_shows TV_SHOWS_CSV] [--output OUTPUT_CSV]
```

- `--movies`: Path to movies CSV file
- `--tv_shows`: Path to TV shows CSV file  
- `--output`: Output CSV file path (default: output.csv)

**Note**: At least one of `--movies` or `--tv_shows` must be provided.

### Examples

```bash
# Convert both movies and TV shows
python convert_csv.py --movies movies.csv --tv_shows shows.csv

# Convert only movies
python convert_csv.py --movies movies.csv

# Convert only TV shows with custom output
python convert_csv.py --tv_shows shows.csv --output my_output.csv
```

## Output Format

The script generates a CSV with the following columns:

- `universe`: "movie" or "tvshow"
- `title`: Original title
- `release_date`: Original year
- `rating`: User rating rounded to integer (default: 5 if not provided)
- `is_wishlisted`: True if viewCount equals 0
- `is_recommended`: True if userRating >= 8
- `is_done`: True if confirmed as watched (interactive prompt for items with viewCount > 0)

## Validation

The script includes validation to ensure data consistency:
- Throws an error if userRating exists but viewCount is 0 (inconsistent state)
- Handles missing or invalid ratings by defaulting to 5
- Validates that required columns exist in input files

## Interactive Features

For items with viewCount > 0, the script will prompt you to confirm whether each item has actually been watched, allowing you to set the `is_done` flag accurately.

## Sample Files

Sample CSV files are included:
- `sample_movies.csv`: Example movie data
- `sample_tv_shows.csv`: Example TV show data

## Made with Copilot
This project was developed with the help of GitHub Copilot, which assisted in generating the code.
