import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


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
       
        for i in range(1, max_pages+1):
            soup = BeautifulSoup(contents, 'lxml')
            all_item_details = soup.find_all('div', class_ = 'cPHDOP.col-12-12')


            for item in all_item_details:
                phone_name = item.find('div', class_ = "KzDlHZ").text
                print(phone_name)
           
            await page.goto(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}")
            contents = await page.content()






asyncio.run(main())
