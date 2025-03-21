#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <chrono>

// 랜덤 리스트 생성 함수
void rand_list(std::vector<int>& numbers, int size) {
    for (int i = 1; i < size; i++) {
        int number = rand() % (size + 1) + 1; // 1부터 size+1 사이의 랜덤 숫자
        numbers.push_back(number);
    }
}

// 버블 정렬 함수 (오름차순)
void sortAcendingArr(std::vector<int>& arr) {
    for (size_t i = 0; i < arr.size(); i++) {
        for (size_t j = i + 1; j < arr.size(); j++) {
            if (arr[i] > arr[j]) {
                int tmp = arr[i];
                arr[i] = arr[j];
                arr[j] = tmp;
            }
        }
    }
}

int main() {
    int size = 20000; // 리스트 크기
    std::vector<int> Bubble;

    // 랜덤 생성 초기화
    srand(static_cast<unsigned int>(time(0)));
    rand_list(Bubble, size);

    // 버블 정렬 실행 시간 측정
    auto Bubble_start_time = std::chrono::high_resolution_clock::now();
    sortAcendingArr(Bubble);
    auto Bubble_end_time = std::chrono::high_resolution_clock::now();

    // 실행 시간 계산 및 출력
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(Bubble_end_time - Bubble_start_time).count();
    std::cout << "C++ 버블 정렬 실행시간: " << static_cast<double>(duration) / 1e9 << " 초" << std::endl;

    return 0;
}
