## How It Works

1. **Natural-language query parsing:** Gemini 3.5 Flash Lite interprets user queries and extracts structured requirements such as city, listing category, budget, capacity, and required features.
2. **Input validation:** The parsed values are checked against supported cities, categories, and features before being used.
3. **Fallback parsing:** If Gemini is unavailable or returns an invalid response, the application uses a rule-based parser.
4. **Filtering:** The engine filters listings by availability and the user's hard requirements.
5. **Ranking:** Matching listings are scored using ratings, preferred features, price, and capacity fit.
6. **Explanations:** Each recommendation includes details explaining why it matches the user's requirements.

## Technologies Used

- Python
- Streamlit
- Pandas
- Google Gemini API (`google-genai`)
- python-dotenv
- Pytest

## Testing

The project includes automated tests for normal queries, vague queries, no-match cases, availability, and recommendation explanations. A separate fallback test verifies that recommendations still work when Gemini is unavailable.

## Configuration and Limitations

Store the Gemini API key in a local `.env` file using the `GEMINI_API_KEY` variable. Do not commit API keys or other secrets to version control.

The listing dataset contains synthetic sample data. Prices, ratings, availability, and listing details are for demonstration purposes and do not represent verified real-world listings.

Gemini API availability and usage limits may affect query interpretation. The rule-based parser provides a fallback when the API cannot be used.

## Setup and Run

### 1. Clone or download the project
Open the project folder in VS Code.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create a `.env` file in the project root and add your own API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file or share your API key.

### 4. Start the application

```bash
streamlit run app.py
```

The application will open in your browser.

### 5. Run the tests

```bash
python -m pytest -v
```