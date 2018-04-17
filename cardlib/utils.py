# coding=utf-8
def is_list_sequential(check_list, index=0):
    if index == len(check_list) - 1:
        return True
    elif check_list[index] + 1 == check_list[(index + 1)]:
        return is_list_sequential(check_list, index + 1)
    else:
        return False
