import yfinance as yf
import pandas as pd
from prophet import Prophet
from datetime import datetime
import streamlit as st
import smtplib
from email.mime.text import MIMEText


def get_prediction(ticker, travel_date):
    """
    Fetches data, trains a model, and returns the forecast and top 3 days.
    """
    try:
        # 1. Fetch 5 years of historical data
        data = yf.download(tickers=ticker, period='5y', interval='1d', progress=False)

        # Flatten multi-level column headers if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # 2. Validate and Clean Data
        if data.empty or 'Close' not in data.columns or data['Close'].isnull().all():
            return None, "Could not find valid data for this currency pair.", None

        df_prophet = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}).dropna().drop_duplicates(subset=['ds'])
        
        if len(df_prophet) < 30:
            return None, "Not enough historical data available to make a reliable forecast.", None

        # 3. Train Model and Predict
        model = Prophet()
        model.fit(df_prophet)

        # Corrected this line to remove the redundant .date()
        days_to_forecast = (travel_date - datetime.now().date()).days
        future = model.make_future_dataframe(periods=days_to_forecast)
        forecast = model.predict(future)

        # 4. Analyze Forecast
        today_naive = pd.Timestamp.now().normalize()
        travel_date_naive = pd.to_datetime(travel_date).normalize()
        future_mask = (forecast['ds'] > today_naive) & (forecast['ds'] <= travel_date_naive)
        future_forecast = forecast.loc[future_mask]

        if future_forecast.empty:
            return None, "Could not generate a forecast for the selected period.", None

        # Find the 3 days with the HIGHEST predicted rate
        best_days = future_forecast.sort_values(by='yhat', ascending=False).head(3)
        
        # Return the results and the full forecast for plotting
        return best_days, forecast, model

    except Exception as e:
        return None, f"An unexpected error occurred: {e}", None

def send_email_reminder(recipient_email, best_days_df):
    """
    Sends an email reminder with the prediction results.
    """
    try:
        # Get credentials from Streamlit secrets
        sender_email = st.secrets["SENDER_EMAIL"]
        sender_password = st.secrets["SENDER_PASSWORD"]

        # Format the message
        subject = "Your Currency Exchange Reminder"
        body = "Hello,\n\nHere are the top 3 predicted days to exchange your currency:\n\n"
        for index, row in best_days_df.iterrows():
            date_str = row['ds'].strftime('%A, %Y-%m-%d')
            rate_str = f"{row['yhat']:.4f}"
            body += f"- {date_str} (Predicted Rate: {rate_str})\n"
        body += "\nDisclaimer: This is an automated statistical forecast, not financial advice."

        # Create the email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Connect to Gmail's SMTP server and send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed to send: {e}")
        return False