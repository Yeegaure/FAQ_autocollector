import emoji
import pickle
import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings('ignore', category=InconsistentVersionWarning)


with open('log_regression_model.pkl', 'rb') as file:
    log_reg = pickle.load(file)

with open('vectorizer.pkl', 'rb') as file:
    vectorizer = pickle.load(file)

def clean_message(message : str) -> str:
    message = emoji.replace_emoji(message, '')
    message.strip()
    return message

def classify_message(message : str) -> bool:
    message_cleaned = clean_message(message)
    X = vectorizer.transform([message_cleaned])
    pred = log_reg.predict(X)[0]
    return pred

if __name__ == '__main__':
    print('Testing utilities...')
    test = "интересно😮 так а толку то от педиатра, скажет аллергия или энтеровирус (былотакое), напишите пожалуйста как сьездите. а к дерматологу куда? на сухэ батора?"
    print('input : ', test)
    print('cleaned ', clean_message(test))
    print('prediction :', classify_message(test))