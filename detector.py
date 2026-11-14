
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)


class SpamDetector:

    def __init__(self):

        self.data = pd.read_csv("data/messages.csv")

        self.texts = self.data["message"].astype(str)
        self.labels = self.data["label"].str.lower()

        # Split dataset into training and testing data
        X_train, X_test, y_train, y_test = train_test_split(
            self.texts,
            self.labels,
            test_size=0.2,
            random_state=42,
            stratify=self.labels
        )

        # Create machine learning pipeline
        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2)
            )),
            ("classifier", MultinomialNB())
        ])

        # Train model
        self.model.fit(X_train, y_train)

        # Test model
        y_pred = self.model.predict(X_test)

        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        self.accuracy = round(accuracy * 100, 2)

        print("\nModel Training Completed!")
        print("Model Accuracy:", self.accuracy, "%")

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Train final model on complete dataset
        self.model.fit(self.texts, self.labels)

    def predict(self, message):

        prediction = self.model.predict([message])[0]

        probabilities = self.model.predict_proba([message])[0]

        classes = list(self.model.classes_)

        spam_probability = probabilities[classes.index("spam")]

        confidence = max(probabilities) * 100

        spam_percent = spam_probability * 100

        # Calculate risk level
        if spam_percent <= 30:
            risk_level = "LOW"

        elif spam_percent <= 70:
            risk_level = "MEDIUM"

        else:
            risk_level = "HIGH"

        return {
            "label": "SPAM" if prediction == "spam" else "NOT SPAM",
            "confidence": round(confidence, 2),
            "spam_probability": round(spam_percent, 2),
            "risk_level": risk_level
        }


if __name__ == "__main__":

    detector = SpamDetector()

    message = "Congratulations! You won a free prize. Click here."

    result = detector.predict(message)

    print("\nTest Prediction:")
    print(result)
