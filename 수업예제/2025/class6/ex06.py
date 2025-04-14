def my_in(element, lst):
    for item in lst:
        if item == element:
            return True
    return False

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]
print(my_in(5, numbers))  # True
print(my_in(10, numbers))  # False
