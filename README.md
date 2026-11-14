# SpamShield — Email Spam Detector

## Run on Windows using VS Code

1. Extract this ZIP and open the `SpamShield` folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   `py -m venv venv`
4. Activate it in PowerShell:
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
   `.\venv\Scripts\Activate.ps1`
5. Install packages:
   `pip install -r requirements.txt`
6. Start the website:
   `python app.py`
7. Open `http://127.0.0.1:5000`

## Project structure
- `app.py`: Flask web server and page route
- `detector.py`: TF-IDF + Multinomial Naive Bayes model
- `data/messages.csv`: labelled sample training messages
- `templates/index.html`: website HTML
- `static/style.css`: website styling
- `static/script.js`: character counter and browser interaction

This is a learning prototype using a small illustrative dataset. It may misclassify messages and must not be treated as a real email security product.
