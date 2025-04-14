def my_min(numbers):
    min_value = numbers[0]  # 첫 번째 요소를 최소값으로 설정
    for num in numbers:
        if num < min_value:
            min_value = num
    return min_value

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]
print(my_min(numbers))  # 1
