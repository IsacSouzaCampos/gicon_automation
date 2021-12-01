import os



for file in os.listdir('.'):
    if '.txt' not in file:
        continue
    with open(file, 'r') as fin:
        text = fin.read()
    with open(file, 'w') as fout:
        print(text.upper(), file=fout)
