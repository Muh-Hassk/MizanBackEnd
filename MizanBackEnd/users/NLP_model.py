from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import numpy as np
import pickle

#vectorizing the tweet by the pre-fitted tokenizer instance
class JusticeClassifier:
    max_sequence_length = 854
    legal_keywords = ["court", "judge", "petitioner", "plaintiff", "defendant", "ruling", "appealed",
                      "evidence", "verdict", "testimony", "subpoena", "misdemeanor", "felony",
                      "brief", "testify", "complaint", "lawsuit", "jury", "hearing", "probate",
                      "plea", "injunction", "settlement", "admissible", "notarize", "amicus",
                      "breach", "waiver", "certiorari", "deposition", "eminent", "forfeiture",
                      "indictment", "judicial", "litigation", "oath", "parole", "quash", "restitution",
                      "solicitor", "tort", "warrant", "evidence", "forensic", "hearsay", "immunity",
                      "judiciary", "liable", "moot", "negligence", "objection", "perjury", "quorum",
                      "remand", "subpoena", "testimony", "usurp", "venue", "writ", "zoning"]

    def __init__(self, model_weights_path, tokenizer_path):
        # Load custom model weights
        self.model = load_model(model_weights_path)
        # Load the saved tokenizer from the file
        with open(tokenizer_path, 'rb') as tokenizer_file:
            self.tokenizer = pickle.load(tokenizer_file)

    def batch_predict(self, texts, batch_size=32):
        results = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            tokenized_texts = self.tokenizer.texts_to_sequences(batch_texts)
            padded_texts = pad_sequences(tokenized_texts, maxlen=self.max_sequence_length, dtype='int32', value=0)
            batch_results = self.model.predict(padded_texts, batch_size=1, verbose=0)
            results.extend(batch_results)
        return results

    def predict(self, text, confidence_threshold=0.91, max_legal_keywords=10 , min_legal_keywords = 2):
        if isinstance(text, list):
            text = ' '.join(text)  # convert list to string
        text_lower = text.lower()

        # Count the number of legal keywords in the text
        legal_keyword_count = sum(text_lower.count(keyword) for keyword in self.legal_keywords)
        print(legal_keyword_count)
        if legal_keyword_count > max_legal_keywords or legal_keyword_count < min_legal_keywords or legal_keyword_count == 0 or len(text) < 45:
            print("False Case")
            return 3

        sentiment = self.batch_predict([text])
        max_confidence = np.max(sentiment)
        print(max_confidence)

        if max_confidence >= 0.9930829:
            return 3
        elif np.argmax(sentiment) == 0:
            return 0
        elif np.argmax(sentiment) == 1:
            return 1