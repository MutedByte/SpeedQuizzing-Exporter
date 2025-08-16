# SpeedQuizzing Quizpack Exporter

A Python tool to fetch and export quiz questions and options from [SpeedQuizzing](https://www.speedquizzing.com/) question packs.\
This script collects quizpack data concurrently and outputs it into a structured CSV file for analysis, backup, or offline use.

## Features

- Fetches all available quizpack keys from SpeedQuizzing.
- Concurrently downloads quizpack questions and their options for high performance.
- Supports multiple question types: Keypad, Advanced, Multi Tap, and Nearest.
- Outputs a well-structured CSV including:
  - Question ID
  - Question text
  - Answer
  - Additional info (long answer if different from short answer)
  - Question type, tags, author, publication info
  - Options and image links
- Progress logging and error handling for reliable data collection.

## Requirements

- Python 3.10+
- `requests` library

Install dependencies via pip:

```bash
pip install requests
```

## Usage

1. Clone the repository:

```bash
git clone https://github.com/MutedByte/SpeedQuizzing-Exporter.git
cd SpeedQuizzing-Exporter
```

2. Set your SpeedQuizzing session cookie in `scraper.py`:

```python
COOKIES = {
    "sq_session": "YOUR_COOKIE"
}
```

3. Run the exporter:

```bash
python scraper.py
```

4. The data will be saved in `all_quizpacks.csv`.

## Contributing

Contributions, issues, and feature requests are welcome!\
Please follow Python best practices and maintain clear docstrings.


## Disclaimer

This tool is intended for personal or authorized use only. The developer is not responsible for any misuse of the exported data. Ensure that your use of SpeedQuizzing data complies with their terms of service and applicable laws.

