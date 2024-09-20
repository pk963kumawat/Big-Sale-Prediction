from flask import Flask, request, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Prediction function based on historical sales and market trend factor
def big_sale_prediction(historical_sales, market_trend_factor):
    avg_sales = sum(historical_sales) / len(historical_sales)  # Calculate average sales
    forecasted_sales = avg_sales * market_trend_factor  # Apply trend factor
    return forecasted_sales

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if an Excel file is uploaded
        if 'file' not in request.files:
            return render_template('index.html', prediction_text="No file uploaded.")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', prediction_text="No file selected.")
        
        # Read the Excel file if it's valid
        if file and file.filename.endswith('.xlsx'):
            # Sanitize the filename to avoid security risks
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)

            # Save the file to server temporarily
            file.save(file_path)

            try:
                # Read the historical sales data from the Excel file (assumes data is in the first column)
                df = pd.read_excel(file_path)
                historical_sales = df.iloc[:, 0].tolist()  # Read the first column of the Excel file
                
                # Get the market trend factor from the form and validate it
                market_trend_factor = request.form['market_trend_factor']
                if not market_trend_factor or not market_trend_factor.replace('.', '', 1).isdigit():
                    raise ValueError("Market trend factor must be a valid number.")
                market_trend_factor = float(market_trend_factor)

                # Predict the sales based on the uploaded data
                predicted_sales = big_sale_prediction(historical_sales, market_trend_factor)

                return render_template('index.html', prediction_text=f'Predicted Sales: {predicted_sales:.2f}')
            finally:
                # Clean up by removing the uploaded file
                os.remove(file_path)

        else:
            return render_template('index.html', prediction_text="Please upload a valid Excel (.xlsx) file.")
    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: {str(e)}")

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)  # Ensure upload directory exists
    app.run(debug=True)
