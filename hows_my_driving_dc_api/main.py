"""hows-my-driving-dc-api main app"""
import asyncio
import os
import subprocess
import zipfile

import boto3
from bs4 import BeautifulSoup
from fastapi import FastAPI
from PIL import Image
from pydantic import BaseModel
from pyppeteer import launch
from pyppeteer_stealth import stealth
from pytesseract import image_to_string

app = FastAPI(title="How's My Driving DC API", version=0.1, root_path="/prod/")

CHROMIUM_KEY = "stable-headless-chromium-amazonlinux-2.zip"
s3_bucket = boto3.resource("s3").Bucket(os.environ["BUCKET"])


def get_chromium():
    """download chromium binary from S3"""
    zip_file_path = "/tmp/chrome.zip"
    if not os.path.exists(zip_file_path):
        s3_bucket.download_file(CHROMIUM_KEY, zip_file_path)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall("/tmp")
            subprocess.run(["chmod", "+x", "/tmp/headless-chromium"], check=True)


async def get_page():
    """get pyppeteer page object"""
    browser = await launch(
        args=[
            "--no-sandbox",
            "--single-process",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-zygote",
        ],
        executablePath="/tmp/headless-chromium",
        userDataDir="/tmp",
    )

    page = await browser.newPage()
    await stealth(page)
    await page.setViewport(dict(height=768, width=1024))
    await page.goto(
        "https://prodpci.etimspayments.com/pbw/include/dc_parking/input.jsp",
        options=dict(waitUntil="networkidle0"),
    )
    return page


# adapted from https://github.com/mdminhazulhaque/html-table-to-json/blob/master/tabletojson.py
def table_to_list(content):
    """convert HTML table to list of dicts"""
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")
    headers = ["Ticket Number", "Issue Date", "Violation", "Location", "Amount"]
    data = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) == len(headers):
            items = {}
            for index, header in enumerate(headers):
                items[header] = cells[index].text
            data.append(items)
    return data


class SearchRequest(BaseModel):
    """Search Request model"""

    state: str
    plate: str


@app.post("/search")
async def search(req: SearchRequest):
    """search for tickets"""
    get_chromium()

    state = req.state
    plate = req.plate

    page = await get_page()

    # type plate number
    plate_field = await page.querySelector("[name=plateNumber]")
    await plate_field.type(plate)

    # select state
    await page.evaluate(
        """state => {
      document.querySelector('[name=statePlate]').value = state;
    }""",
        state,
    )

    # save then solve captcha, write to text field
    captcha = await page.querySelector("#captcha")
    bbox = await captcha.boundingBox()
    await page.screenshot(dict(path="/tmp/captcha.png", clip=bbox))

    img = Image.open("/tmp/captcha.png")
    solved = image_to_string(img)
    clean = "".join([d for d in solved if d.isdigit()])

    captcha_field = await page.querySelector("[name=captchaSText]")
    await captcha_field.type(clean)

    # submit, extract results
    await asyncio.gather(
        page.waitForNavigation(dict(waitUntil="networkidle0")),
        page.click("[name=submit"),
    )

    # try extracting results
    try:
        table = await page.evaluate(
            """() => {
            return document.querySelector('form table table').innerHTML;
        }"""
        )
        number = await page.evaluate(
            """() => {
            return +document.querySelector('form table').innerText.match(/You have a total of (\d+) citation/)[1];
        }"""
        )
        amount = await page.evaluate(
            """() => {
            return document.querySelector('form table').innerText.match(/The total of all your citations and fees is: (.*)/)[1];
        }"""
        )
        resp = dict(number=number, amount=amount, tickets=table_to_list(table))
    except Exception as e:
        print(e)
        resp = {"error": "problem reading table"}

    # save backup image
    await page.screenshot(dict(path="/tmp/example.png"))
    s3_bucket.upload_file("/tmp/example.png", f"{plate}-{state}.png")

    return resp
