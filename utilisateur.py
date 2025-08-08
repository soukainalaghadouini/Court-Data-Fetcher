from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

def get_case_types():
    options = Options()
    options.add_argument('--headless')  # بدون واجهة مرئية
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://delhihighcourt.nic.in/casequery")
        time.sleep(3)

        select = driver.find_element(By.ID, "ddlCaseType")
        options = select.find_elements(By.TAG_NAME, "option")

        case_types = []
        for opt in options:
            value = opt.get_attribute("value").strip()
            text = opt.text.strip()
            if value:
                case_types.append({'value': value, 'label': text})
        return case_types
    finally:
        driver.quit()

@app.route('/')
def index():
    case_types = get_case_types()
    return render_template('index.html', case_types=case_types)

if __name__ == '__main__':
    app.run(debug=True)





from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    case_year = request.form['filing_year']

    # تهيئة متصفح كروم مع WebDriver Manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")
    time.sleep(2)

    # تعبئة الحقول
    driver.find_element(By.ID, "ddlCaseType").send_keys(case_type)
    driver.find_element(By.ID, "txtCaseNumber").send_keys(case_number)
    driver.find_element(By.ID, "txtCaseYear").send_keys(case_year)

    # جلب الكابتشا المكتوبة (نص)
    captcha_text = driver.find_element(By.ID, "captchaText").text
    driver.find_element(By.ID, "CaptchaInputText").send_keys(captcha_text)

    # الضغط على زر البحث
    driver.find_element(By.ID, "btnSubmit").click()
    time.sleep(3)

    # جلب نتيجة البحث
    try:
        result = driver.find_element(By.ID, "divCaseStatus").text
    except:
        result = "لا توجد نتائج أو حدث خطأ."

    driver.quit()

    return f"<h3>نتيجة البحث:</h3><pre>{result}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
