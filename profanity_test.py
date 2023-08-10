from better_profanity import profanity
from profanity_check import predict_prob
from profanity_filter import ProfanityFilter
pf = ProfanityFilter()

while True:
    txt = input("Text to be censored: ")
    print("Censored: " + profanity.censor(txt))
    print(predict_prob([txt]))
    print('Censored with profanity_filter: ' + pf.censor(txt))