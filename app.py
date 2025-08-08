from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3

# إنشاء اتصال بالقاعدة
conn = sqlite3.connect('queries_log.db')
c = conn.cursor()

# إنشاء جدول لتسجيل الاستعلامات
c.execute('''
    CREATE TABLE IF NOT EXISTS queries_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_type TEXT,
        case_number TEXT,
        case_year TEXT,
        raw_response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print("✅ تم إنشاء قاعدة البيانات.")




app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cases', methods=['POST'])
def result():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    case_year = request.form['case_year']

    # إعداد السائق
    service = Service("chromedriver.exe")
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # يمكنك تفعيل هذا في الإنتاج
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")
        wait = WebDriverWait(driver, 15)

        # إدخال البيانات
        wait.until(EC.presence_of_element_located((By.NAME, "case_type"))).send_keys(case_type)
        driver.find_element(By.NAME, "case_number").send_keys(case_number)
        driver.find_element(By.NAME, "case_year").send_keys(case_year)

        # التقاط الكابتشا
        captcha = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "captcha-code"))).text.strip()
        driver.find_element(By.ID, "captchaInput").send_keys(captcha)

        # الضغط على زر البحث
        driver.execute_script("document.getElementById('search').click();")

        # الانتظار لظهور النتائج
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "caseTable")),
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'No Data')]"))
            )
        )
        raw_html = driver.page_source
        # تسجيل في قاعدة البيانات
        conn = sqlite3.connect('queries_log.db')
        c = conn.cursor()
        c.execute(''' INSERT INTO queries_log (case_type, case_number, case_year, raw_response)
         VALUES (?, ?, ?, ?)
        ''', (case_type, case_number, case_year, raw_html))
        conn.commit()
        conn.close()


        soup = BeautifulSoup(driver.page_source, "html.parser")

        table = soup.find("table", id="caseTable")
        if not table:
            driver.quit()
            return render_template("home.html", parties=None, error="⚠️ لم يتم العثور على جدول بيانات.")

        row = table.find("tbody").find("tr")
        if not row:
            driver.quit()
            return render_template("home.html", parties=None, error="⚠️ لم يتم العثور على صف بيانات.")

        cells = row.find_all("td")
        if len(cells) < 4:
            driver.quit()
            return render_template("home.html", parties=None, error="⚠️ البيانات غير مكتملة.")

        # استخراج الأطراف
        parties_text = cells[2].get_text(separator="\n").strip()
        lines = [line.strip() for line in parties_text.split("\n") if line.strip()]
        parties = [line for line in lines if "VS" not in line.upper()]

        # استخراج التواريخ
        dates_text = cells[3].get_text(separator="\n").strip()
        filing_date = ""
        next_hearing = ""
        for line in dates_text.split("\n"):
            if "LAST DATE" in line.upper():
                filing_date = line.split(":")[-1].strip()
            elif "NEXT DATE" in line.upper():
                next_hearing = line.split(":")[-1].strip()

        # رابط PDF
        link = cells[1].find("a", string="Orders")
        pdf_urls = [link['href']] if link and link.has_attr('href') else []

        driver.quit()

        return render_template("home.html",
                               parties=parties,
                               filing_date=filing_date,
                               next_hearing=next_hearing,
                               pdf_urls=pdf_urls)

    except Exception as e:
        driver.quit()
        return render_template("home.html", parties=None, error=f"⚠️ حدث خطأ: {e}")

if __name__ == "__main__":
    app.run(debug=True)
