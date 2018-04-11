def is_list_sequential(list, index=0):
    if index == len(list) - 1:
        return True
    elif list[index] + 1 == list[(index + 1)]:
        return is_list_sequential(list, index + 1)
    else:
        return False
