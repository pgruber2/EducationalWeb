# Piazza Integration for -- EducationalWeb

The following instructions have been tested with Python3.8.5 on MacOS

1. Set environment variables for the downloader:
    1. `export BASE_DIR=[absolute path of base directory to store posts]` - e.g. `/opt/data/piazza`
    2. `export SLEEP_OVERRIDE=5`

2. Run the downloader `./piazza_downloader.py [your piazza email] [class id to download]` - e.g. `./piazza_downloader.py piazza@org.edu kdp8arjgvyj67a`

3. Set environment variables for the parser:
    1. `export TARGET_DATE=[date directory from downloader]` - e.g. 2020_11_12
    2. `export BASE_DIR=[absolute path of base directory where posts are stored]` - e.g. `/opt/data/piazza`

4. Run the parser `./piazza_post_parser.py [class id to parse]` - e.g. `./piazza_post_parser.py kdp8arjgvyj67a`
