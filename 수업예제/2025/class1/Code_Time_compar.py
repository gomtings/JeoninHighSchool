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
    
Bubble=[]
rand_list(Bubble,size)
Bubble_start_time = time.process_time_ns()
sortAcendingArr(Bubble)
Bubble_end_time = time.process_time_ns()

print('python_ 버블 정렬 실행시간 : {} 초'.format(str((Bubble_end_time - Bubble_start_time)/1000000000)))
