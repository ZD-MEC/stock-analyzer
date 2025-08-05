
# Stock Analyzer

An interactive Streamlit web application for stock data analysis using the Alpha Vantage API.

## Project Files

- `main.py` — Streamlit user interface and main workflow
- `api_client.py` — API communication and data cleaning
- `data_processor.py` — Data processing and visualizations
- `pyproject.toml`, `poetry.lock` — Poetry dependency management
- `.env.example` — Example environment file for API key
- `app.log` — Application log file (created automatically)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME
    ```

2. **Install dependencies with Poetry:**
    ```bash
    pip install poetry
    poetry install
    poetry shell
    ```

3. **Set your Alpha Vantage API key:**
    - Sign up for a free API key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key).
    - Create a file named `.env` in the project root with the following line:
      ```
      ALPHA_VANTAGE_API_KEY=your_api_key_here
      ```
    - Alternatively, enter your API key in the app UI when prompted.

4. **Run the application:**
    ```bash
    streamlit run main.py
    ```
    The app will open in your web browser (default: [http://localhost:8501](http://localhost:8501)).

## Usage

1. Enter a stock symbol (e.g., AAPL, TSLA, MSFT).
2. Enter your Alpha Vantage API key (or leave empty to use the key in `.env`).
3. Select the desired time series function (Daily, Weekly Adjusted, Monthly Adjusted, Intraday, or Global Quote).
4. Click "Analyze" to fetch and visualize the data.

## Notes

- **API Limit:** The free Alpha Vantage tier allows up to 25 requests per day per key.
- If you exceed the limit, you will see an error message. Try again later or use a different API key.
- Before running the application, copy .env_example to .env and replace your_api_key_here with your personal Alpha Vantage API key.
  Never upload your actual .env file to the repository!



## Troubleshooting

- If you see "Expected key '...' not found in API response", check your API key, daily quota, or the stock symbol.
- If the app does not start, verify you have Python 3.9+ and Poetry installed.
- For additional errors, check the `app.log` file.

## License

This project is for educational purposes only.

