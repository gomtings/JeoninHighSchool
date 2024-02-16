def change_center_value(matrix, new_value):
    rows = len(matrix)
    cols = len(matrix[0])
    center_row = rows // 2
    center_col = cols // 2
    
    if rows % 2 == 1 and cols % 2 == 1:
        matrix[center_row][center_col] = new_value
    elif rows % 2 == 0 and cols % 2 == 1:
        matrix[center_row - 1][center_col] = new_value
        matrix[center_row][center_col] = new_value
    elif rows % 2 == 1 and cols % 2 == 0:
        matrix[center_row][center_col - 1] = new_value
        matrix[center_row][center_col] = new_value
    elif rows % 2 == 0 and cols % 2 == 0:
        matrix[center_row - 1][center_col - 1] = new_value
        matrix[center_row - 1][center_col] = new_value
        matrix[center_row][center_col - 1] = new_value
        matrix[center_row][center_col] = new_value

# 예시 2차원 리스트
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# 중앙 값을 0으로 바꿈
change_center_value(matrix, 0)

# 변경된 리스트 출력
for row in matrix:
    print(row)
