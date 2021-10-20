"""hows-my-driving-dc-api main app"""
import os
import subprocess
import zipfile

import boto3
from fastapi import FastAPI
from pyppeteer import launch
from pyppeteer_stealth import stealth

app = FastAPI()

CHROMIUM_KEY = "stable-headless-chromium-amazonlinux-2.zip"


@app.get("/")
async def index():
    """test"""

    s3_bucket = boto3.resource("s3").Bucket(os.environ["BUCKET"])
    zip_file_path = "/tmp/chrome.zip"
    if not os.path.exists(zip_file_path):
        s3_bucket.download_file(CHROMIUM_KEY, zip_file_path)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall("/tmp")
            subprocess.run(["chmod", "+x", "/tmp/headless-chromium"], check=True)

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
    await page.goto(
        "https://prodpci.etimspayments.com/pbw/include/dc_parking/input.jsp"
    )
    await page.screenshot({"path": "/tmp/example.png"})

    s3_bucket.upload_file("/tmp/example.png", "example.png")

    return {"Hello": "World"}
