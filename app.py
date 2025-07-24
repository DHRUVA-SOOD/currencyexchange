import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta
import base64
import os
import smtplib
from email.mime.text import MIMEText

# --- Helper Functions ---

def set_bg_from_local(image_file):
    """Sets a local image as the background of the Streamlit app robustly."""
    script_dir = os.path.dirname(__file__)
    abs_image_path = os.path.join(script_dir, image_file)
    
    try:
        with open(abs_image_path, "rb") as f:
            img_bytes = f.read()
        encoded_img = base64.b64encode(img_bytes).decode()
        custom_css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_img}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .stApp > header {{ background-color: transparent; }}
            </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Background image not found. Ensure '{image_file}' is in the same folder as app.py.")

def get_prediction(ticker, travel_date):
    """Fetches data, trains a model, and returns the forecast and top 3 days."""
    try:
        data = yf.download(tickers=ticker, period='5y', interval='1d', progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if data.empty or 'Close' not in data.columns or data['Close'].isnull().all():
            return None, "Could not find valid data for this currency pair.", None

        df_prophet = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}).dropna().drop_duplicates(subset=['ds'])
        
        if len(df_prophet) < 30:
            return None, "Not enough historical data available for a forecast.", None

        model = Prophet()
        model.fit(df_prophet)
        days_to_forecast = (travel_date - datetime.now().date()).days
        future = model.make_future_dataframe(periods=days_to_forecast)
        forecast = model.predict(future)

        today_naive = pd.Timestamp.now().normalize()
        travel_date_naive = pd.to_datetime(travel_date).normalize()
        future_mask = (forecast['ds'] > today_naive) & (forecast['ds'] <= travel_date_naive)
        future_forecast = forecast.loc[future_mask]

        if future_forecast.empty:
            return None, "Could not generate a forecast for the selected period.", None

        best_days = future_forecast.sort_values(by='yhat', ascending=False).head(3)
        return best_days, forecast, model
    except Exception as e:
        return None, f"An unexpected error occurred: {e}", None

def send_email_reminder(recipient_email, best_days_df):
    """Sends an email reminder with the prediction results."""
    try:
        sender_email = st.secrets["SENDER_EMAIL"]
        sender_password = st.secrets["SENDER_PASSWORD"]

        subject = "Your Currency Exchange Reminder"
        body = "Hello,\n\nHere are the top 3 predicted days to exchange your currency:\n\n"
        for _, row in best_days_df.iterrows():
            date_str = row['ds'].strftime('%A, %Y-%m-%d')
            rate_str = f"{row['yhat']:.4f}"
            body += f"- {date_str} (Predicted Rate: {rate_str})\n"
        body += "\nDisclaimer: This is an automated statistical forecast, not financial advice."

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email failed to send: {e}")
        return False

# --- Main App ---
st.set_page_config(page_title="Currency Forecaster", page_icon="💰", layout="centered")
set_bg_from_local("background.png")

st.title("💱 Currency Exchange Forecaster")
st.write("Predict the best days to exchange currency before your travel date.")

country_to_currency = {
    'United States': 'USD', 'India': 'INR', 'United Kingdom': 'GBP',
    'Euro Area': 'EUR', 'Japan': 'JPY', 'Australia': 'AUD', 'Canada': 'CAD'
}

with st.form("exchange_form"):
    col1, col2 = st.columns(2)
    with col1: from_country = st.selectbox("From", list(country_to_currency.keys()))
    with col2: to_country = st.selectbox("To", list(country_to_currency.keys()), index=1)
    travel_date = st.date_input("Travel Date", min_value=datetime.today() + timedelta(days=7))
    submitted = st.form_submit_button("🔍 Find Best Exchange Days")

if submitted:
    if from_country == to_country:
        st.error("'From' and 'To' countries cannot be the same.")
    else:
        base, quote = country_to_currency[from_country], country_to_currency[to_country]
        pair = f"{base}{quote}=X"

        with st.spinner(f"Making predictions for {base} to {quote}..."):
            best_days, forecast_data, model = get_prediction(pair, travel_date)

            if best_days is not None:
                st.header("✅ Top 3 Predicted Days to Exchange")
                for i, row in best_days.iterrows():
                    st.success(f"**{row['ds'].strftime('%A, %Y-%m-%d')}** – Predicted Rate: **`{row['yhat']:.4f}`**")

                with st.expander("📧 Get an Email Reminder"):
                    with st.form("email_form"):
                        email_address = st.text_input("Enter your email address")
                        email_submitted = st.form_submit_button("Send Reminder")
                        if email_submitted:
                            if email_address:
                                with st.spinner("Sending email..."):
                                    if send_email_reminder(email_address, best_days):
                                        st.success(f"Reminder sent to {email_address}!")
                                    else:
                                        st.error("Failed to send email. Ensure secrets are configured correctly.")
                            else:
                                st.warning("Please enter your email address.")

                st.markdown("### 📊 Forecast Trend")
                fig = model.plot(forecast_data)
                ax = fig.gca()
                ax.set_title(f'Forecast for {pair}')
                ax.set_xlabel("Date")
                ax.set_ylabel("Exchange Rate")
                st.pyplot(fig)
            else:
                st.error(f"Prediction failed. Reason: {forecast_data}")
        
        st.warning("⚠️ **Disclaimer:** This is a statistical forecast, not financial advice.", icon="❗")

# --- NEW: Feedback Section ---
st.write("---") 
with st.expander("📝 Leave a Review"):
    with st.form("feedback_form", clear_on_submit=True):
        user_email = st.text_input("Your Email (Optional)")
        user_review = st.text_area("Your Review")
        feedback_submitted = st.form_submit_button("Submit Review")

        if feedback_submitted:
            if user_review: # Ensure review is not empty
                # Create a dataframe from the new feedback
                feedback_df = pd.DataFrame({
                    "email": [user_email],
                    "review": [user_review],
                    "timestamp": [datetime.now()]
                })

                # Append to a CSV file without writing the header every time
                try:
                    # Check if the file exists to decide on writing the header
                    file_exists = os.path.exists("feedback.csv")
                    feedback_df.to_csv("feedback.csv", mode='a', header=not file_exists, index=False)
                    st.success("Thank you for your feedback!")
                except Exception as e:
                    st.error(f"Failed to save feedback: {e}")
            else:
                st.warning("Please write a review before submitting.")