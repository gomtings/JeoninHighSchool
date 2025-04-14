def my_min_max(numbers):
    min_value = numbers[0]
    max_value = numbers[0]
    
    for num in numbers:
        if num < min_value:
            min_value = num
        if num > max_value:
            max_value = num
            
    return min_value, max_value

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]
min_val, max_val = my_min_max(numbers)
print(f"최소값: {min_val}, 최대값: {max_val}")  # 최소값: 1, 최대값: 9
