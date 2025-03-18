#include "pch.h"
#include <stdio.h>
#include <stdlib.h> //srand, rand를 사용하기 위한 헤더파일
#include <time.h> // time을 사용하기 위한 헤더파일

void suffle() {
    srand(time(NULL)); // 난수 초기화
    int arr[] = { 3,5,2,1,5,6,20,7,99,35 };
    int randIndex[] = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 };
    int suffle_size = sizeof(arr) / sizeof(int);
    int currentPos = 0;
    int currentname = 0;
    int randValue = 0;
    for (int i = 0; i < suffle_size; i++ ){
        //랜덤하게 하나씩 뽑는다.
        randValue = rand() % suffle_size;
        currentPos = randIndex[randValue]; // 현재 값, , ? 4
        randIndex[randValue] = randIndex[suffle_size - 1]; //8 { 0, 1, 2, 3, 9, 5, 6, 7, 8, 9 };
        randIndex[suffle_size - 1] = currentPos; //{ 0, 1, 2, 3, 9, 5, 6, 7, 8, 4 };

        currentname = arr[randValue]; // 현재 값, , ? 4
        arr[randValue] = arr[suffle_size - 1]; //8 { 0, 1, 2, 3, 9, 5, 6, 7, 8, 9 };
        arr[suffle_size - 1] = currentname; //{ 0, 1, 2, 3, 9, 5, 6, 7, 8, 4 };
        suffle_size -= 1;
    }
    printf("{");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        printf("%d , ", arr[i]);
    }
    printf("} \n");
}
int main() {
    int arr[] = {3,5,2,1,5,6,20,7,99,35};
    int tmp = 0;
    printf("배열 정렬전...\n");
    printf("{");
    for (int i = 0; i < sizeof(arr) / sizeof(int); i++) {
        printf("%d , ", arr[i]);
    }
    printf("} \n");
    printf("배열 정렬후...\n");
    suffle();
    return 0;
}