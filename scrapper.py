import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import abc 

class Database:
    def __init__(self, db_name='flipkart_items.db'):
        self._conn = sqlite3.connect(db_name)
        self._c = self._conn.cursor()

    def create_table(self):
        self._c.execute('''
            CREATE TABLE IF NOT EXISTS product_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                image_url TEXT,
                price INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)
                ''')
        self._conn.commit()

    def insert_products(self, title, img_url, price):
        self._c.execute("""
          INSERT INTO product_info (title, image_url, price, created_at)
          VALUES (?, ?, ?, ?)""", (title, img_url, price, datetime.now().isoformat()))
        self._conn.commit()
    

    def close_connection(self):
        self._conn.close()


class Scraper(abc.ABC):
    def __init__(self, query, max_pages, db):
        self._query = query
        self._max_pages = max_pages
        self._db = db

    @abc.abstractmethod
    async def run(self):
        raise NotImplementedError("Subclasses must implement the 'run' method.")


class FlipkartScraper(Scraper):
    count=0
    def __init__(self, query, max_pages, db):
        super().__init__(query, max_pages, db)


    async def intercept(self, route, request):
        resource_type = request.resource_type
        url = request.url.split('?')[0]
        unwanted_resources = ["stylesheet", "font"]
        if resource_type in unwanted_resources:
            await route.abort()
        elif resource_type == "image" and not url.endswith('.jpeg'):
            await route.abort()
        else:
            await route.continue_()

    async def pagitation(self, browser, page_no):
        page = await browser.new_page()
        await page.route("**/*", self.intercept)
        await page.goto(f"https://www.flipkart.com/search?q={self._query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={page_no}")
        await page.wait_for_selector("div.bowO0w")
        contents = await page.content()

        # FlipkartScraper.count += 1
        # filename = f"saved_page{FlipkartScraper.count}.html"
        # with open(filename, "w", encoding="utf-8") as f:
        #     f.write(contents)

        await page.close()
        return contents
    

    async def scrap_data(self, contents):
        soup = BeautifulSoup(contents, 'lxml')
        all_item_details = soup.select('div._75nlfW')
        for item in all_item_details:
            try:
                product_cards = item.find_all('div', attrs={'data-id': True})
                if len(product_cards) == 1:
                    name = item.find('div', class_ = "KzDlHZ").get_text()
                    url = item.find('img', class_ = "DByuf4")["src"]
                    price_text = item.find("div", class_=["Nx9bqj", "_4b5DiR"]).get_text()
                    price = price_text.split("₹")[-1]
                    if len(price)>3:
                        price = int(price.replace(',', ''))
                    else:
                        price = int(price)
                    self._db.insert_products(name, url, price)
        

                else:
                    for card in product_cards:
                        a_tag = card.find('a', title=True)
                        name = a_tag['title'] if a_tag else "N/A"
                        img_tag = card.find('img', src=True)
                        url = img_tag['src'] if img_tag else "N/A"
                        price_tag = card.find('div', class_='Nx9bqj')
                        if price_tag:
                            price_text = price_tag.get_text().strip()
                            price = int(price_text.replace('₹', '').replace(',', ''))
                        
                        else:
                            price = 0
                        self._db.insert_products(name, url, price)

            except Exception as e:
                print(f"Could not scrap an item: {e}")


    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.route("**/*", self.intercept)
            
            print(f"\nStarting to scrape Flipkart for '{self._query}'...")
            await page.goto("https://www.flipkart.com/")
            await page.wait_for_selector('input[name="q"]')
            await page.fill('input[name="q"]', self._query)
            await page.press('input[name="q"]', 'Enter')
            await page.wait_for_selector('div.cPHDOP.col-12-12')
            contents = await page.content()
            await page.close()
            self._db.create_table()


            async with asyncio.TaskGroup() as tg:
                for current_page in range(1, self._max_pages + 1):
                    if current_page == 1:
                        print(f"Scraping page {current_page}...")
                        tg.create_task(self.scrap_data(contents))
                    else:
                        print(f"Scraping page {current_page}...")
                        tg.create_task(self.scrap_data ( await self.pagitation(browser, current_page ) ))
            
            await browser.close()
        
        print(f"\nAll the info related to '{self._query}' has been fetched and stored.")


async def main():
    try:
        database = Database()
        query = input("\nEnter your search item > ")
        max_pages = int(input("Enter how many pages you want to scrape > "))
        if max_pages <= 0:
            print("Enter a positive number.")
            return
        
        scraper = FlipkartScraper(query, max_pages, database)
        await scraper.run()
        database.close_connection()
        
    except Exception as e:
        print(f"error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())