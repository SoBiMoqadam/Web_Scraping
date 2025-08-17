# Web Scraping With Python

<div align="center">
<h1 style="color:#00ffff; font-family:monospace;">🤖 Web Scraper Automation</h1>
<p style="font-family:monospace; font-size:16px; color:#9be7ff;">
This is an automation scraper that uses <strong>selenium</strong> and optionally <strong>BeautifulSoup (bs4)</strong> for faster extraction.  
It collects book information such as <strong>ISBN</strong>, <strong>price</strong>, and <strong>number of pages</strong>, and saves it into <strong>CSV</strong>, <strong>JSON</strong>, and <strong>Excel</strong> files 🚀
</p>
</div>

---

## Sample Code

<div style="background:#1e1e2f; padding:15px; border-radius:10px; color:#fff; font-family:monospace; line-height:1.5;">
<pre>
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver

def fa_to_en(text):
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    return ''.join(english_digits[persian_digits.index(ch)] if ch in persian_digits else ch for ch in text)

def extract_int(text):
    return int(re.sub(r"[^\d]", "", fa_to_en(text))) if text else None

def extract_year_shamsi(text):
    cleaned = fa_to_en(text.strip()) if text else ""
    return int(cleaned) if re.match(r"^(13[0-9]{2}|14[0-4][0-9])$", cleaned) else None
</pre>
</div>

---

## ⬇️ Download Files

You can download the scraper script and a sample output JSON:

[![Download scraper.py](https://img.shields.io/badge/Download-scraper.py-00FFFF?style=for-the-badge&logo=python&logoColor=white)](https://raw.githubusercontent.com/SoBiMoqadam/Web_Scraping_WithPython/main/scraper.py)
[![Download books_finance_all.json](https://img.shields.io/badge/Download-books_finance_all.json-F7DF1E?style=for-the-badge&logo=json&logoColor=black)](https://raw.githubusercontent.com/SoBiMoqadam/Web_Scraping_WithPython/main/books_finance_all.json)

---

## Installation / Setup

Clone this repository and install the required packages using pip:

```bash
git clone https://github.com/SoBiMoqadam/Web_Scraping_WithPython.git
cd Web_Scraping_WithPython
pip install -r requirements.txt
python scraper.py
