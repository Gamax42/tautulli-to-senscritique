#!/usr/bin/env python3
"""
CSV Converter Script for Movies and TV Shows

This script processes CSV files containing movie and TV show data and converts them
to a standardized format for SensCritique import.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional
from InquirerPy import inquirer


def validate_csv_file(file_path: str, file_type: str) -> bool:
    """Validate that the CSV file exists and has required columns."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: {file_type} file '{file_path}' does not exist.")
        return False
    
    if not path.is_file():
        print(f"Error: '{file_path}' is not a file.")
        return False
    
    # Check if file has required columns
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = {'title', 'userRating', 'viewCount', 'year'}
            actual_columns = set(reader.fieldnames or [])
            
            missing_columns = required_columns - actual_columns
            if missing_columns:
                print(f"Error: {file_type} file is missing required columns: {missing_columns}")
                return False
                
    except Exception as e:
        print(f"Error reading {file_type} file: {e}")
        return False
    
    return True


def process_csv_file(file_path: str, universe: str) -> List[Dict]:
    """Process a single CSV file and return list of processed records."""
    records = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because header is row 1
            try:
                # Extract values
                title = row['title'].strip()
                user_rating = row['userRating'].strip()
                view_count = row['viewCount'].strip()
                year = row['year'].strip()
                
                # Skip empty rows
                if not title:
                    continue
                
                # Throw error if year is missing
                if not year:
                    raise ValueError(f"Row {row_num}: Missing 'year' for title '{title}'")
                
                # Convert viewCount to integer
                try:
                    view_count_int = int(view_count)
                except ValueError:
                    print(f"Warning: Invalid viewCount '{view_count}' in row {row_num}, treating as 0")
                    view_count_int = 0
                
                # Convert userRating to float, then round to integer
                if user_rating:
                    try:
                        rating_float = float(user_rating)
                        # Validation: throw error if userRating exists but viewCount is 0
                        if rating_float > 0 and view_count_int == 0:
                            raise ValueError(f"Row {row_num}: userRating is {rating_float} but viewCount is 0. "
                                           "This is inconsistent - how can something be rated if not viewed?")
                        rating = round(rating_float)
                    except ValueError as e:
                        if "userRating is" in str(e):
                            raise  # Re-raise validation errors
                        print(f"Warning: Invalid userRating '{user_rating}' in row {row_num}, using default value 5")
                        rating = 5
                else:
                    rating = 5
                
                # Determine flags
                is_wishlisted = view_count_int == 0
                is_recommended = rating >= 8 if user_rating else False
                
                # Handle is_done flag
                is_done = False
                if view_count_int > 0:
                    # Ask user for confirmation that the item has been watched
                    answer = inquirer.confirm(
                        message=f"Has '{title}' ({universe}) been watched?",
                        default=True
                    ).execute()
                    is_done = answer
                
                # Create record with boolean values as 'true'/'false' strings
                record = {
                    'universe': universe,
                    'title': title,
                    'release_date': year,
                    'rating': rating,
                    'is_wishlisted': 'true' if is_wishlisted else 'false',
                    'is_recommended': 'true' if is_recommended else 'false',
                    'is_done': 'true' if is_done else 'false'
                }
                
                records.append(record)
                
            except Exception as e:
                print(f"Error processing row {row_num} in {file_path}: {e}")
                sys.exit(1)
    
    return records


def write_output_csv(records: List[Dict], output_path: str):
    """Write processed records to output CSV file."""
    if not records:
        print("No records to write.")
        return
    
    fieldnames = ['universe', 'title', 'release_date', 'rating', 'is_wishlisted', 'is_recommended', 'is_done']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Successfully wrote {len(records)} records to {output_path}")


def main():
    """Main function to handle argument parsing and orchestrate the conversion."""
    parser = argparse.ArgumentParser(
        description="Convert movie and TV show CSV files to SensCritique format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_csv.py --movies movies.csv --tv_shows shows.csv
  python convert_csv.py --movies movies.csv
  python convert_csv.py --tv_shows shows.csv
        """
    )
    
    parser.add_argument(
        '--movies',
        type=str,
        help='Path to movies CSV file'
    )
    
    parser.add_argument(
        '--tv_shows',
        type=str,
        help='Path to TV shows CSV file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output.csv',
        help='Output CSV file path (default: output.csv)'
    )
    
    args = parser.parse_args()
    
    # Validate that at least one input file is provided
    if not args.movies and not args.tv_shows:
        parser.error("At least one of --movies or --tv_shows must be provided")
    
    all_records = []
    
    # Process movies file
    if args.movies:
        if validate_csv_file(args.movies, "Movies"):
            print(f"Processing movies from: {args.movies}")
            movie_records = process_csv_file(args.movies, "movie")
            all_records.extend(movie_records)
            print(f"Processed {len(movie_records)} movie records")
        else:
            sys.exit(1)
    
    # Process TV shows file
    if args.tv_shows:
        if validate_csv_file(args.tv_shows, "TV Shows"):
            print(f"Processing TV shows from: {args.tv_shows}")
            tv_records = process_csv_file(args.tv_shows, "tvshow")
            all_records.extend(tv_records)
            print(f"Processed {len(tv_records)} TV show records")
        else:
            sys.exit(1)
    
    # Write output
    if all_records:
        write_output_csv(all_records, args.output)
    else:
        print("No records were processed.")


if __name__ == '__main__':
    main()
