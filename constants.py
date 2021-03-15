from collections import Counter
import nltk

UPPERCASE_LETTERS = [chr(i) for i in range(65, 91)]
LOWERCASE_LETTERS = [chr(i) for i in range(97, 123)]
LETTERS = UPPERCASE_LETTERS + LOWERCASE_LETTERS
STOP_WORDS = Counter(nltk.corpus.stopwords.words('english'))

if __name__ == '__main__':
    print("is" in STOP_WORDS)
    print("as" in STOP_WORDS)
    print("was" in STOP_WORDS)