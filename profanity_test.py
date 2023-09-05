from better_profanity import profanity
from profanity_check import predict_prob
#from profanity_filter import ProfanityFilter

#pf = ProfanityFilter()

def readProfanities():
    profanities = []
    file = open('./static/profanity-list.txt','r')
    for line in file:
        line = line.strip()
        profanities.append(line)
    return profanities

PROFANITIES = readProfanities()

def man_censor(txt):
    txt = txt.lower()
    for bad_word in PROFANITIES:
        txt = txt.replace(bad_word, '****')
    return txt

while True:
    txt = input("Text to be censored: ")
    print("Censored with better_profanity: " + profanity.censor(txt))
    print("Chance of being profane: " + str(predict_prob([txt])[0]))
    #print('Censored with profanity_filter: ' + pf.censor(txt))
    print("Censored manually: " + man_censor(txt))

