count = 0
while count < 10:
    count += 1
    if count % 3 == 0: 
        continue
    #print(count)
    
    
values = [123, 124, 643, 0]
for value in values:
    print(value) # 123 124 643 0    
    
    
count = 0
values = []
while count < 10:
    values.append(count)
    count += 1

print(values) # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

for elem in range(10):
    print(elem, end=" ") # 0 1 2 3 4 5 6 7 8 9    