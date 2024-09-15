# AI-Powered Email Response Assistant

This project automates email processing and response generation using NLP (Natural Language Processing). It can:

- Analyze the context, tone, and urgency of incoming emails.
- Generate personalized, context-aware replies.
- Automatically send responses using the Gmail API.
- Prioritize emails based on content for better email management.

## Features

- **NLP-Powered Context Analysis**: Understands the sentiment, urgency, and tone of incoming emails.
- **Automated Responses**: Uses AI to draft replies, saving time on manual effort.
- **Email Prioritization**: Classifies emails into priority levels, ensuring high-priority emails are addressed promptly.
- **Emotion Detection**: Detects the prominent emotion in the email text to guide the response tone.

## Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/GenXAICoder/email-auto-reply.git
    cd email-auto-reply
    ```

2. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Setup Google API**:
    - Enable the Gmail API from the Google Developer Console.
    - Download your `credentials.json` and place it in the root folder of the project.
    - Configure your `.env` file with the following keys:
      ```
      GOOGLE_CLIENT_ID=<your_client_id>
      GOOGLE_CLIENT_SECRET=<your_client_secret>
      GOOGLE_REFRESH_TOKEN=<your_refresh_token>
      GOOGLE_ACCESS_TOKEN=<your_access_token>
      GEMINI_API_KEY=<your_gemini_api_key>
      ```

4. **Download NLTK and Other Required Libraries**:
    Run these commands to download necessary resources:
    ```bash
    python -m nltk.downloader vader_lexicon
    python -m nltk.downloader punkt_tab
    ```

5. **Train or Load Email Classifier**:
    - Train a Naive Bayes classifier using the Enron dataset or load your pre-trained model.
    - Store the trained model in the project directory as `classifier.joblib` and vectorizer as `vectorizer.joblib`.

## Running the Application

1. **Start the program**:
    ```bash
    python main.py
    ```

2. **How it works**:
   - The app will fetch emails from your Gmail account.
   - It will classify and prioritize them based on sentiment and context.
   - The system will generate responses using the configured AI model and send the emails back automatically.

## Key Components

- **Sentiment and Emotion Detection**: Uses `vaderSentiment` and `NRCLex` libraries to analyze emails.
- **Gmail API Integration**: Fetches emails and sends replies through Gmail.
- **Response Generation**: Integrates with the Gemini AI API to generate intelligent, context-based email replies.

## Contributing

Feel free to contribute to this project! Fork the repository, make changes, and submit a pull request.
