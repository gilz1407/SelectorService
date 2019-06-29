def searchTemplate(lst, expLength):
    middle = findTemplates(lst, expLength)

    index = middle
    while lst[index - 1] == expLength:
        index = index - 1

    return index

def findTemplates(lst, expLength):
    middle = int(len(lst) / 2)
    middleVal = lst[middle][1]

    if int(expLength) < middleVal:
        return findTemplates(lst[:middle], int(expLength))
    elif int(expLength) > middleVal:
        return middle + findTemplates(lst[middle:], int(expLength))

    first = 0
    last = 0
    # return middle
    for i in range(middle, len(lst) - 1):
        if lst[i][1] > lst[middle][1]:
            last = i
            break

    for i in range(middle, 0, -1):
        if lst[i][1] < lst[middle][1]:
            first = i + 1
            break

    return lst[first:last]