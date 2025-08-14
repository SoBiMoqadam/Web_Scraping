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

def clean_text(text):
    if not text:
        return "نامشخص"
    cleaned = text.strip()
    return cleaned if cleaned else "نامشخص"

def safe_find(selector, default="نامشخص"):
    try:
        text = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        return text if text else default
    except:
        return default

def find_by_label_contains(label):
    try:
        divs = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-1")
        for div in divs:
            spans = div.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 2 and label in spans[0].text:
                return spans[1].text.strip()
    except:
        return None

def find_book_name():
    try:
        return driver.find_element(By.CSS_SELECTOR, "h5.text-sm.font-bold.truncate.pt-2").text.strip()
    except:
        try:
            return driver.title.strip().replace(" | ایران کتاب", "")
        except:
            return "نامشخص"

def find_writer():
    try:
        return driver.find_element(By.CSS_SELECTOR, "h6.text-xs.truncate.pt-1").text.strip()
    except:
        return "نامشخص"

def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def save_all_files(books):
    df = pd.DataFrame(books)
    before = len(df)
    df = df.drop_duplicates(subset=["name", "sku"], keep="first")
    after = len(df)

    df.to_json("books_finance_all.json", orient="records", force_ascii=False, indent=2)
    df.to_csv("books_finance_all.csv", index=False, encoding="utf-8-sig")
    df.to_excel("books_finance_all.xlsx", index=False)

    print(f"\n ذخیره نهایی انجام شد.")
    print(f" کل کتاب‌ها قبل از حذف تکراری: {before}")
    print(f" پس از حذف تکراری‌ها: {after}")
    print(f" فایل‌ها ذخیره شدند.")

driver = create_driver()
base_url = "https://www.iranketab.ir"
category_slug = "484-finance"
all_books = []
seen_links = set()

try:
    for page_num in range(1, 33):
        try:
            url = f"{base_url}/tag/{category_slug}?p={page_num}"
            print(f"\n بارگذاری صفحه {page_num}: {url}")
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.card.product-card-simple")))

            scroll_to_bottom()
            time.sleep(1)

            elems = driver.find_elements(By.CSS_SELECTOR, "a.card.product-card-simple")
            page_links = list(dict.fromkeys([e.get_attribute("href") for e in elems if e.get_attribute("href")]))
            print(f" {len(page_links)} لینک در این صفحه یافت شد.")

            if not page_links:
                print(" صفحه خالی بود.")
                continue

            for book_url in page_links:
                if book_url in seen_links:
                    continue
                seen_links.add(book_url)

                for attempt in range(3):
                    try:
                        driver.get(book_url)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        break
                    except:
                        time.sleep(3)
                else:
                    print(f" رد شد: {book_url}")
                    continue

                name = find_book_name()
                writer = find_writer()
                translator_links = driver.find_elements(By.XPATH, "//span[text()='مترجم:']/following-sibling::div//a")
                translator_raw = "، ".join([a.text.strip() for a in translator_links])
                translator = clean_text(translator_raw) if translator_raw else "نامشخص"

                try:
                    price_text = fa_to_en(driver.find_element(By.CSS_SELECTOR, "strong.toman").get_attribute("innerText"))
                    price = int(re.sub(r"[^\d]", "", price_text))
                except:
                    price = 0

                book = {
                    "name": name,
                    "writer": writer,
                    "translator": translator,
                    "nasher": clean_text(find_by_label_contains("انتشارات")),
                    "sku": find_by_label_contains("شابک") or "نامشخص",
                    "price": price,
                    "pages": extract_int(find_by_label_contains("تعداد صفحه")),
                    "year_shamsi": extract_year_shamsi(find_by_label_contains("سال انتشار شمسی")),
                    "year_miladi": extract_int(find_by_label_contains("سال انتشار میلادی")),
                    "nobat": extract_int(find_by_label_contains("سری چاپ")),
                    "ghat": find_by_label_contains("قطع") or "نامشخص",
                    "jeld": find_by_label_contains("نوع جلد") or "نامشخص",
                    "description": safe_find(".text-justify.leading-6"),
                    "category": "مالی"
                }

                all_books.append(book)
                print(f" ذخیره شد: {name}")

        except Exception as e:
            print(f" خطا در صفحه {page_num}: {e}")

except KeyboardInterrupt:
    print("\n توقف دستی فعال شد.")

finally:
    driver.quit()
    save_all_files(all_books)