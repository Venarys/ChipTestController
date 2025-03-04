with open("img/exp1.txt", 'r') as file:
    line = file.readline()
    text = line.split(",")
    for i in text:
        i = i.strip()
        i = i.strip("'")
        print(i)