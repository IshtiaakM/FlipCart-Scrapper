# Flipkart-Harvester

## Introduction

Flipkart Harvester is an asynchronous Python script tool that automates the process of extracting product details (title, image URL, and price) in Flipkart search result pages. It utilizes Playwright which is used to mimic a user, BeautifulSoup to parse HTML, and SQLite to store local data.



**Table of Contents**

1. [Features](#features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Dependencies](#dependencies)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
---

## Features

- High-performance asynchronous scraping with `asyncio` and Playwright.
- Interceptions of resources to block unwanted assets (stylesheets, fonts, media) and block images to JPEGs.
- BeautifulSoup to parse HTML and obtain the titles, image URLs and prices of the products.
- A SQLite database that will facilitate convenient local storage of scraped data.
- Developed on an abstract base-class (Scraper) so it can be extended to other e-commerce sites in the future with minimum effort.
- Customizable pagination so that you can scrape as many pages as you want.
- Simple command-line interface to enter a search term and mention how many pages to scrape.

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/IshtiaakM/FlipKart-Harvester.git
   cd flipkart-scraper
   ```

2. **Create & activate a virtual environment (recommended)**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**  
   ```bash
   playwright install
   ```

---

## Configuration

The scraper can be configured via constructor parameters or by modifying constants in the script:

- `db_name` (default: `flipkart_items.db`): SQLite database filename.
- `query`: Search items on Flipkart (e.g., "Smartphones").
- `max_pages`: Maximum number of pages to scrape (must be a positive integer).

---

## Usage

Run the scraper interactively:

```bash
python scraper.py
```

You will be prompted to enter:

1. Search item (e.g., `Smartphones`)
2. Number of pages to scrape (e.g., `3`)

**Example session:**

```
Enter your search item > Smartphones

Enter how many pages you want to scrape > 3
Starting to scrape Flipkart for 'Smartphones'...
Scraping page 1...
Scraping page 2...
Scraping page 3...

All the info related to 'Smartphones' has been fetched and stored.

```

Data will be saved in the SQLite database file (`flipkart_items.db` by default), in the table `product_info`.

---

## Project Structure

```
.
├── scraper.py            # Main script containing all classes and entry point
├── requirements.txt      # Python package dependencies
└── flipkart_items.db     # SQLite database (created at runtime)
```

---

## Dependencies

- Python ≥ 3.7
- `playwright`
- `beautifulsoup4`
- `sqlite3`
- `asyncio`
  
---

## Examples

Below is a quick example of how to integrate the scraper in another script:

```python
import asyncio
from scraper import FlipkartScraper, Database

async def run_scraper():
    db = Database(db_name='my_products.db')
    scraper = FlipkartScraper(query='headphones', max_pages=5, db=db)
    await scraper.run()
    db.close_connection()

if __name__ == "__main__":
    asyncio.run(run_scraper())
```

---

## Troubleshooting

- **Playwright browser not found**  
  Make sure you’ve run `playwright install`.

- **Selectors have changed**  
  Flipkart’s page structure may evolve. Update CSS selectors in `scrap_data()` and `pagitation()`.

- **network errors**  
  Check your internet connection and consider adding extra error handling or increasing timeouts.

- **Database locked**  
  Ensure no other process is accessing the SQLite file concurrently.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m "Add some feature"`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Raise a pull request

All code must adhere to PEP 8 and where possible must have tests.
