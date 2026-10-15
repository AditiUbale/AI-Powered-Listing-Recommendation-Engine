# AI-Powered Listing Recommendation Engine

An AI-powered listing recommendation system that understands natural-language queries, filters available listings based on user requirements, and ranks the best matches with explanations.

## How It Works

1. **Natural-language query parsing:** Gemini interprets user queries and extracts structured requirements such as city, listing category, budget, capacity, and required features.
2. **Input validation:** Parsed values are checked against supported cities, categories, and features.
3. **Fallback parsing:** If Gemini is unavailable or returns an invalid response, the application uses a rule-based parser.
4. **Filtering:** Listings are filtered by availability and the user's requirements.
5. **Ranking:** Matching listings are scored using ratings, preferred features, price, and capacity fit.
6. **Explanations:** Each recommendation includes details explaining why it matches the user's requirements.

## Technologies Used

- Python
- Streamlit
- Pandas
- Google Gemini API (`google-genai`)
- python-dotenv
- Pytest

## Project Structure

```text
listing-recommendation-engine/
├── data/
│   └── listings.csv
├── app.py
├── recommender.py
├── create_dataset.py
├── test_recommender.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup and Run

### 1. Download the project

Download or clone the repository and open the project folder in VS Code.

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root and add your own API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your actual key. Keep `.env` private and never upload it to GitHub.

### 5. Start the application

```bash
streamlit run app.py
```

The application will open in your browser.

### 6. Run the tests

```bash
python -m pytest -v
```

The project includes automated tests for normal queries, vague queries, no-match cases, availability, recommendation explanations, Gemini parser output, and rule-based fallback behavior.

## Configuration and Limitations

- The listing dataset contains synthetic sample data. Prices, ratings, availability, and listing details are for demonstration purposes and do not represent verified real-world listings.
- Gemini API availability, model configuration, and usage limits may affect query interpretation.
- The rule-based parser provides a fallback when Gemini cannot be used.
- A valid Gemini API key is required for Gemini-powered query parsing.

## Security

The Gemini API key should be stored in a local `.env` file. The `.env` file and virtual environment are excluded from version control through `.gitignore`. Never publish API keys or other secrets.
