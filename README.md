# 💱 Currency Exchange Forecaster

A web application that uses machine learning to predict the best days to exchange currency before your travel date.

---

## 🚀 Live Demo

🔗 **[Click Here to Try the App](https://your-app-name.streamlit.app/)**
*(Replace this with your actual deployed Streamlit link)*

📸&#x20;
*(Replace this with a real screenshot of your app)*

---

## 🔍 Features

* 🗕️ **Forecast Exchange Rates:** Predicts future rates using Prophet (by Meta).
* 🌐 **Multi-Currency Support:** Choose any "From" and "To" country.
* ✅ **Top 3 Days Recommendation:** Shows the best 3 days to exchange currency.
* 📧 **Email Alerts (Optional):** Get forecasts directly in your inbox.
* 🖥️ **User-Friendly Interface:** Built with Streamlit for simplicity.
* 📝 **Feedback System:** Submit reviews stored in a local CSV.

---

## 🧰 Tech Stack

| Layer       | Tools Used                 |
| ----------- | -------------------------- |
| Frontend    | Streamlit                  |
| Backend     | Python, Pandas             |
| ML Model    | Prophet                    |
| Data Source | `yfinance` (Yahoo Finance) |

---

## 💻 Installation & Setup

### 1⃣ Clone the Repo

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2⃣ Add Dependencies

Create a `requirements.txt` file with the following:

```txt
streamlit
pandas==2.1.4
prophet
yfinance
```

Install with:

```bash
pip install -r requirements.txt
```

### 3⃣ Email Setup (Optional)

If using the email reminder feature:

Create a file at `.streamlit/secrets.toml`:

```toml
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-16-character-app-password"
```

> 🔐 Make sure to keep this file private. Use an App Password if you're using Gmail with 2FA enabled.

### 4⃣ Run the App

```bash
streamlit run app.py
```

---

## 🌍 Deployment

Deploy for free using [Streamlit Community Cloud](https://streamlit.io/cloud).
Just connect your GitHub repo and it’s live in seconds!

---

## ⚠️ Disclaimer

> This tool provides **statistical predictions only** and should **not** be used as financial advice.
> Currency markets are volatile and involve risk. 

---
