Delhi High Court Case Data Scraper Project
🏛️ Target Court
Delhi High Court

Website: https://delhihighcourt.nic.in/app/get-case-type-status

📝 Project Description
A web application built with Flask that allows users to input case details (case type, case number, case year) and search for them on the Delhi High Court website.
The application uses Selenium to launch a Chrome browser, fill out the form, read the CAPTCHA text displayed on the page, and automatically enter it.
After the results are displayed, the application extracts party details, hearing dates, and links to PDF files (if any), and displays them on the same page.
It also logs every query into an SQLite database to document the search history.

🚀 Setup and Installation
1. Download ChromeDriver
Download the ChromeDriver version that is compatible with your installed Google Chrome browser from the official website:
https://sites.google.com/chromium.org/driver/

Place the chromedriver.exe file in the project folder or update the file path in the code.

2. Run the Application
From within the project folder, execute the following command in your terminal:

python app.py

Then, open your web browser and navigate to:
http://127.0.0.1:5000/

🔐 CAPTCHA Bypass Strategy
The CAPTCHA text is extracted from an HTML element with the class captcha-code using Selenium.

This text is then automatically entered into the CAPTCHA input field (captchaInput).

No complex OCR or image analysis techniques are used; the application simply reads the text as it appears on the page.

Note: This method only works if the CAPTCHA is text-based and not an image or a drawing.

⚙️ Environment Details
ChromeDriver Path
The path to the ChromeDriver executable is defined in the code. You can change it according to where you placed the file.

service = Service("chromedriver.exe")

Chrome Browser Settings
In the code, the headless mode option is currently disabled to allow for visual observation of the browser's operation.

# options.add_argument('--headless')  # Can be enabled if needed

Database
An SQLite database file named queries_log.db is automatically created when the application is run for the first time. It contains a table to log every search query.

User Interface
The application uses an HTML template named home.html to display the search form and the results. It also displays error messages if no data is found or if issues occur.

📊 Extracted Data Structure
Parties: A list of the parties' names, with lines containing "VS" removed.

Last Hearing Date (filing_date): Extracted from the text containing "LAST DATE".

Next Hearing Date (next_hearing): Extracted from the text containing "NEXT DATE".

PDF URLs (pdf_urls): Links to case order PDF files, if available.

⚠️ Important Notes
Google Chrome must be installed, and the ChromeDriver version must be compatible with it.

It is recommended to disable debug mode (debug=True) in Flask before deploying the application.

Every search is logged in the database along with the raw HTML of the page for reference.

The application handles errors and displays appropriate messages to the user when data is not available or errors occur.

🆘 Help and Support
If you need the home.html template file or any further assistance in running or improving the project, feel free to ask.
