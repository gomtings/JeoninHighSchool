def get_neighbors(matrix, row, col):
    neighbors = []
    for i in range(row - 1, row + 2):
        for j in range(col - 1, col + 2):
            if 0 <= i < len(matrix) and 0 <= j < len(matrix[0]):
                neighbors.append(matrix[i][j])
    return neighbors

# 예시 이차원 리스트
matrix = [
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 25]
]

# (2, 2) 좌표를 기준으로 주변 3*3 내에 있는 값들을 얻음
row_index = 0
col_index = 0
result = get_neighbors(matrix, row_index, col_index)
print(result)  # 결과 출력
