import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3




conn = sqlite3.connect('flipkart_items.db')
c = conn.cursor()
def create_table():
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            image_url TEXT,
            price INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)
            ''')
   
    conn.commit()






def insert_products(title, img_url, price):
    c.execute("""
     INSERT INTO product_info (title, image_url, price, created_at)
     VALUES (?, ?, ?, ?)""",
     (title, img_url, price, datetime.now().isoformat())
    )
    conn.commit()




async def main(query="smartphones", max_pages= int(input("enter how many page you want to scrap >  "))):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.flipkart.com/")
        await page.wait_for_selector('input[name="q"]')
        await page.fill('input[name="q"]', query)
        await page.press('input[name="q"]', 'Enter')


        await page.wait_for_selector('div.cPHDOP.col-12-12')  
        contents = await page.content()
        create_table()
        for i in range(1, max_pages+1):
            soup = BeautifulSoup(contents, 'lxml')
            all_item_details = soup.select('div._75nlfW')


            for item in all_item_details:
                phone_name = item.find('div', class_ = "KzDlHZ").get_text()
                img_tag = item.find('img', class_ = "DByuf4")["src"]
                price = item.find("div" , class_ = ["Nx9bqj","_4b5DiR"]).get_text()
                insert_products(phone_name,img_tag,price)
               
            print('saved in database')
            await page.goto(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}")
            await page.wait_for_selector('div.cPHDOP.col-12-12')
            contents = await page.content()




asyncio.run(main())