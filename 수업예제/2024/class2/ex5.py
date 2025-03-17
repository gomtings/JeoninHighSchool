import time
import random
size = 20000

def rand_list(numbers,size):
    for i in range(1,size):
        number=random.randint(1,size+1)
        numbers.append(number)
        
def sortAcendingArr(arr):
    for i in range(0,len(arr)): # 처음부터 배열의 끝까지 실행. 
        for j in range((i+1),len(arr)-1): # 
            if arr[i] > arr[j]: # 오름차순 으로 정렬 함.
                tmp = arr[i] # 옮길 데이터를 임시로 저장 
                arr[i] = arr[j] #  i 와 j 두개의 데이터를 서로 바꿔 준다.
                arr[j] = tmp # 임시로 저장 했던 데이터를 j 에 저장해 준다.

def quick_sort(array, start, end):
    if start >= end:
        return
    pivot = start #피벗 초기값은 첫번째 요소
    left = start+1
    right = end
    
    while left <= right:
        # 피벗보다 큰 데이터를 찾을 때까지 반복
        while left <= end and array[left] <= array[pivot]:
            left+=1
            
            #피벗보다 작은 데이터를 찾을 때까지 반복
        while right > start and array[right] >= array[pivot]:
            right-=1
            
        if left>right: # 엇갈렸다면 작은 right -=1 데이터와 피벗을 교체
            array[right], array[pivot] = array[pivot], array[right]
            
        else: # 엇갈리지 않았다면 작은 데이터와 큰 데이터를 교체 
            array[left], array[right] = array[right], array[left]
            
    # 분할 이후 왼쪽 부분과 오른쪽 부분에서 각각 정렬 수행
    quick_sort(array, start, right-1)
    quick_sort(array, right+1, end)   
    
Bubble=[]
rand_list(Bubble,size)
Bubble_start_time = time.process_time_ns()
sortAcendingArr(Bubble)
Bubble_end_time = time.process_time_ns()

Quick=[]
rand_list(Quick,size)
Quick_start_time = time.process_time_ns()
#quick_sort(Quick)
quick_sort(Quick, Quick[0], len(Quick)-1)
Quick_end_time = time.process_time_ns()

print('버블 정렬 실행시간 : {} s'.format(str((Bubble_end_time - Bubble_start_time)/1000000000)))
print('큌 정렬 실행시간 : {} s'.format(str((Quick_end_time - Quick_start_time)/1000000000)))

"""
def sortAcendingArr(arr):
    for i in range(0,len(arr)):
        for j in range((i+1),len(arr)-1):
            if arr[i] > arr[j]: # 오름차순 
                tmp = arr[i]
                arr[i] = arr[j]
                arr[j] = tmp
"""
"""
def quick_sort (arr):
    # 리스트 내 원소가 1개인 경우 함수 종료
    if len(arr) <= 1: 
        return arr

    # 첫 번째 원소를 피벗으로 설정
    pv = arr[0]
    # 피벗을 제외한 리스트
    tail = arr[1:]
    
    # 분할된 좌측 리스트
    left_list = [x for x in tail if x <= pv]
    # 분할된 우측 리스트
    right_list = [x for x in tail if x > pv]
    
    # 분할 이후 좌측 및 우측 리스트 각각에에 대해 퀵 정렬 수행
    return quick_sort(left_list) + [pv] + quick_sort(right_list)
    
def quick_sort(array, start, end):
    if start >= end:
        return
    pivot = start #피벗 초기값은 첫번째 요소
    left = start+1
    right = end
    
    while left <= right:
        # 피벗보다 큰 데이터를 찾을 때까지 반복
        while left <= end and array[left] <= array[pivot]:
            left+=1
            
            #피벗보다 작은 데이터를 찾을 때까지 반복
        while right > start and array[right] >= array[pivot]:
            right-=1
            
        if left>right: # 엇갈렸다면 작은 right -=1 데이터와 피벗을 교체
            array[right], array[pivot] = array[pivot], array[right]
            
        else: # 엇갈리지 않았다면 작은 데이터와 큰 데이터를 교체 
            array[left], array[right] = array[right], array[left]
            
    # 분할 이후 왼쪽 부분과 오른쪽 부분에서 각각 정렬 수행
    quick_sort(array, start, right-1)
    quick_sort(array, right+1, end)    
"""