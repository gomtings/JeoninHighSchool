#include "pch.h"
#include <stdio.h>

int main() {
    int arr[] = {3,5,2,1,5,6,20,7,99,35};
    int tmp = 0;
    printf("배열 정렬전...\n");
    printf("{");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        printf("%d , ", arr[i]);
    }
    printf("} \n");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        for (int j = (i+1); j < sizeof(arr)/sizeof(int); j++) {
            if (arr[i] > arr[j]) { // 오름차순 으로 정렬 함.
                tmp = arr[i];      // 옮길 데이터를 임시로 저장
                arr[i] = arr[j];   // i 와 j 두개의 데이터를 서로 바꿔 준다.
                arr[j] = tmp;      // 임시로 저장 했던 데이터를 j 에 저장해 준다.
            }
        }
    }
    printf("배열 정렬후...\n");
    printf("{");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        printf("%d , ",arr[i]);
    }
    printf("} \n");
    return 0;
}