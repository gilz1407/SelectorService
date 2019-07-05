def searchTemplate(lst, expLength):
    middle = findTemplates(lst, expLength)

    index = middle
    while lst[index - 1][1] == expLength:
        index = index - 1

    return index


def findTemplates(arr, elem, start=0, end=None):
    if end is None:
        end = len(arr) - 1
    if start > end:
        return False

    mid = (start + end) // 2
    if elem == arr[mid][1]:
        return mid
    if elem < arr[mid][1]:
        return findTemplates(arr, elem, start, mid-1)
    # elem > arr[mid]
    return findTemplates(arr, elem, mid+1, end)