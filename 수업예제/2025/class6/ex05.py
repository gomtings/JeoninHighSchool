def my_len(lst):
    count = 0
    for _ in lst:
        count += 1
    return count

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 1, 4, 1, 5, 9, 2, 6, 5]
print(my_len(numbers))  # 9
