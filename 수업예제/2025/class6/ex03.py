def my_max(numbers):
    max_value = numbers[0]  # 첫 번째 요소를 최대값으로 설정
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]
print(my_max(numbers))  # 9
