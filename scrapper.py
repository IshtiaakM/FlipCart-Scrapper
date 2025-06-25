import asyncio
from playwright.async_api import async_playwright


async def main(query="smartphones", max_pages= int(input("enter how many page you want to scrap >  "))):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.flipkart.com/")
        await page.wait_for_selector('input[name="q"]')
        await page.fill('input[name="q"]', query)
        await page.press('input[name="q"]', 'Enter')


        await page.wait_for_selector('div.cPHDOP.col-12-12')  
        contents = []
        contents.append(page.content())
       
        for i in range(1, max_pages+1):
           
            await page.goto(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}")
            contents.append(page.content())


        print(contents)


asyncio.run(main())