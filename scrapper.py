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

async def intercept(route, request):
            resource_type = request.resource_type
            url = request.url
            clean_url = url.split('?')[0]
            unwanted_resources = ["stylesheet", "font", "media"]
            if resource_type in unwanted_resources:
                await route.abort()
            elif resource_type == "image" and not clean_url.endswith('.jpeg'):
                 await route.abort()
            else:
                await route.continue_()

async def pagitation(browser,page_no,query):
     page = await browser.new_page()
     await page.route("**/*",intercept)
     await page.goto(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={page_no}")
     contents = await page.content()
     await page.close()
     return contents


async def scrap_data(contents):
     soup = BeautifulSoup(contents, 'lxml')
     all_item_details = soup.select('div.tUxRFH')
     for item in all_item_details:
        phone_name = item.find('div', class_ = "KzDlHZ").get_text()
        img_tag = item.find('img', class_ = "DByuf4")["src"]
        price = item.find("div" , class_ = ["Nx9bqj","_4b5DiR"]).get_text()
        price =  int(price.split("₹")[-1].replace("," , ""))
        insert_products(phone_name,img_tag,price)


async def main(query="smartphones", max_pages= int(input("enter how many page you want to scrap >  "))):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.route("**/*", intercept)
        await page.goto("https://www.flipkart.com/")
        await page.wait_for_selector('input[name="q"]')
        await page.fill('input[name="q"]', query)
        await page.press('input[name="q"]', 'Enter')
        await page.wait_for_selector('div.cPHDOP.col-12-12')  
        contents = await page.content()
        await page.close()
        create_table()
        async with asyncio.TaskGroup() as tg:
            for current_page in range(1, max_pages+1):
                if current_page == 1:
                    tg.create_task(scrap_data(contents))
                else:
                     tg.create_task(scrap_data( await pagitation(browser,current_page,query) ))
                     
        print(f"All the info related to {query} are fetched.")


asyncio.run(main())