import tweepy
import json
import style
import twitterapicreds
from textblob import TextBlob
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QIcon
import sys


# Use Twitter API bearer token to access tweet search feature
client = tweepy.Client(twitterapicreds.bearer_token)


# Get the tweets to analyze
def fetch_tweets(query, count=100):
    fetched_tweets = []
    try:
        tweets = client.search_recent_tweets(query=query, max_results=count, expansions="author_id",
                                             tweet_fields="public_metrics", user_fields="username")
        for tweet in tweets.data:
            fetched_tweets.append(tweet.text)
    except tweepy.TweepyException as e:
        print(f"Error: {str(e)}")

    return fetched_tweets


# Analyze the sentiment for each tweet and assign a score
def analyze_sentiment(tweets):
    sentiment_scores = []

    for tweet in tweets:
        analysis = TextBlob(tweet)
        sentiment_scores.append(analysis.sentiment.polarity)

    return sentiment_scores


# Get the overall score or "mood" of the searched tweet
def get_overall_sentiment(sentiment_scores):
    overall_sentiment = 0
    mood_rating = "NEUTRAL"

    for sentiment in sentiment_scores:
        overall_sentiment += sentiment

    if overall_sentiment == 0:
        mood_rating = "NEUTRAL"
    elif overall_sentiment > 0:
        mood_rating = "POSITIVE"
    else:
        mood_rating = "NEGATIVE"
    return mood_rating


# Display data in pie chart
def draw_pie_chart(positive_count, neutral_count, negative_count):
    series = QPieSeries()
    series.append("Positive", positive_count)
    series.append("Neutral", neutral_count)
    series.append("Negative", negative_count)

    colors = [QColor(0, 255, 0), QColor(255, 255, 0), QColor(255, 0, 0)]
    for i, slice in enumerate(series.slices()):
        slice.setColor(colors[i])
        slice.setLabel(f"{slice.label()} ({slice.percentage()*100:.2f}%)")

    chart = QChart()
    chart.addSeries(series)
    chart.setTitle("<font color='white'>Mood Distribution</font>")

    pen = QPen(QColor(255, 255, 255))
    chart.legend().setPen(pen)
    chart.legend().setAlignment(Qt.AlignBottom)
    chart.setBackgroundBrush(QBrush(QColor(43, 43, 43)))

    return chart


# Set up user interface
class MoodAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Twitter Mood Analyzer")

        main_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        search_button = QPushButton("Analyze Mood")
        search_button.clicked.connect(self.analyze_mood_button)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_button)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)

        self.pie_chart_view = QChartView()
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view.setBackgroundBrush(QBrush(QColor(43, 43, 43)))

        # Create an empty chart area and set color to ensure dark mode
        empty_chart = QChart()
        empty_chart.setBackgroundBrush(QBrush(QColor(43, 43, 43)))
        self.pie_chart_view.setChart(empty_chart)

        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.result_area)
        main_layout.addWidget(self.pie_chart_view)

        self.setLayout(main_layout)

        self.setFixedWidth(500)
        self.setFixedHeight(600)

        # TODO: Add icon (WIP)
        # self.setWindowIcon(QIcon("icon.png"))

    def analyze_mood_button(self):
        query = self.search_bar.text()
        tweets = fetch_tweets(query, count=10)
        sentiment_scores = analyze_sentiment(tweets)
        overall_mood = f"Overall Mood: {get_overall_sentiment(sentiment_scores)}"

        positive_count = sum(1 for score in sentiment_scores if score > 0)
        neutral_count = sum(1 for score in sentiment_scores if score == 0)
        negative_count = sum(1 for score in sentiment_scores if score == 0)

        tweets_with_scores = "\n".join(
            f"Tweet: {tweet}\nMood: {score:.2f}" for tweet, score in zip(tweets, sentiment_scores))
        result_text = overall_mood + "\n" + tweets_with_scores

        self.result_area.setPlainText(result_text)

        chart = draw_pie_chart(positive_count, neutral_count, negative_count)
        self.pie_chart_view.setChart(chart)


# Build and execute UI
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(style.DARK_STYLE)
    mood_tracker = MoodAnalyzerApp()
    mood_tracker.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
