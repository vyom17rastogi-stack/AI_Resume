import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Uncomment these on first run
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

def extract_entities(text):
    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    phone_pattern = r"\d{10,}"
    url_pattern = r"http[s]?://\S+|www\.\S+"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    urls = re.findall(url_pattern, text)

    for i, email in enumerate(emails):
        text = text.replace(email, f"__EMAIL{i}__")
    for i, phone in enumerate(phones):
        text = text.replace(phone, f"__PHONE{i}__")
    for i, url in enumerate(urls):
        text = text.replace(url, f"__URL{i}__")

    return text, emails, phones, urls


def basic_clean(text):
    text = text.lower()
    punctuation_to_remove = string.punctuation.replace("_", "")
    text = text.translate(str.maketrans("", "", punctuation_to_remove))

    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words and word.isalpha()]

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return " ".join(tokens)


def restore_entities(cleaned_text, emails, phones, urls):
    for i, email in enumerate(emails):
        cleaned_text = cleaned_text.replace(f"__EMAIL{i}__", email)
    for i, phone in enumerate(phones):
        cleaned_text = cleaned_text.replace(f"__PHONE{i}__", phone)
    for i, url in enumerate(urls):
        cleaned_text = cleaned_text.replace(f"__URL{i}__", url)
    return cleaned_text


def clean_text(text):
    text, emails, phones, urls = extract_entities(text)
    cleaned_text = basic_clean(text)
    cleaned_text = restore_entities(cleaned_text, emails, phones, urls)
    
    return {
        "cleaned_text": cleaned_text,
        "emails": emails,
        "phones": phones,
        "urls": urls
    }
