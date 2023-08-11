import nltk
nltk.download('punkt')

from nltk.tokenize import word_tokenize

def count_tokens(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
        tokens = word_tokenize(text)
    return len(tokens)

filename = 'output.jsonl' # Change filename here based on which file you'd like tokens to be counted for.
num_tokens = count_tokens(filename)
print(f'The training data file "{filename}" contains {num_tokens} tokens.')
