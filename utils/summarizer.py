from transformers import pipeline

model = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(text):
    return model(text[:1024])[0]["summary_text"]
