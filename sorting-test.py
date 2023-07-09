import datetime
f = '%Y-%m-%d %H:%M:%S'
data = [['b', datetime.datetime.now() + datetime.timedelta(hours=1)], ['a', datetime.datetime.now()], ['c', datetime.datetime.now() + datetime.timedelta(hours = 23)]]

for tup in data:
    tup[1] = tup[1].strftime(f)

data.sort(key=lambda tup: tup[1])
print(data)