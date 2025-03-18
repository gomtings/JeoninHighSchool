#include "pch.h"
#include <stdio.h> 
int main() {
    int a = 2;
    printf(" 정수를 입력해 주세요! = ");
    scanf_s("%d", &a);
    printf("입력한 정수는 %d 입니다.", sizeof(a));
    if (a >= 10) {}
    return 0;
}