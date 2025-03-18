// variable.cpp : 이 파일에는 'main' 함수가 포함됩니다. 거기서 프로그램 실행이 시작되고 종료됩니다.
//

#include <iostream>
#include <vector>

int a = 1;
static int aa = 1;

void variable() {
	// 정수형
	short b = 1;
	int c = 2;
	long d = 3;

	// 실수형
	float e = 1.1f;
	double f = 1.1;

	//문자
	char g = 'a';
	// 문자열
	std::string h = "bb";
	// bool
	bool is = true;

	// 출력 (테스트용)
	std::cout << b << std::endl;
	std::cout << c << std::endl;
	std::cout << d << std::endl;
	std::cout << e << std::endl;
	std::cout << f << std::endl;
	std::cout << g << std::endl;
	std::cout << h << std::endl;
	std::cout << is << std::endl;
}

void roop() {
	//for
	for (int a = 0; a < 100; a++) {
		std::cout << a << std::endl;
	}

	//while
	int j = 0;
	while (!(j >= 100)) {
		j += 1;
		std::cout << j << std::endl;
	}
}

void mem_delete() {
	int* ptr = new int(5);  // 동적 메모리 할당
	std::cout << *ptr << std::endl;  // 5 출력

	delete ptr;  // 기존 메모리를 해제 안해주면 메모리 누수 발생.
	ptr = new int(10);  // 새 메모리를 할당
	std::cout << *ptr << std::endl;  // 10 출력

	delete ptr;  // 새로 할당된 메모리 해제
}

void array() {
	// 배열 선언
	int arr[5];
	arr[0] = 0;
	std::cout << "Size of arr: " << sizeof(arr) / sizeof(int) << std::endl;

	// 동적 할당
	std::vector<int> myVector(10, 0);
	std::cout << "Size of vector: " << myVector.size() << std::endl;
	myVector.resize(20);
	std::cout << "Size of vector: " << myVector.size() << std::endl;
}

int main()
{
	variable(); // 변수 선언
	roop(); // 반복문 
	array();// 배열 선언
	mem_delete(); // 메모리 수동 관리 
}

// 프로그램 실행: <Ctrl+F5> 또는 [디버그] > [디버깅하지 않고 시작] 메뉴
// 프로그램 디버그: <F5> 키 또는 [디버그] > [디버깅 시작] 메뉴

// 시작을 위한 팁: 
//   1. [솔루션 탐색기] 창을 사용하여 파일을 추가/관리합니다.
//   2. [팀 탐색기] 창을 사용하여 소스 제어에 연결합니다.
//   3. [출력] 창을 사용하여 빌드 출력 및 기타 메시지를 확인합니다.
//   4. [오류 목록] 창을 사용하여 오류를 봅니다.
//   5. [프로젝트] > [새 항목 추가]로 이동하여 새 코드 파일을 만들거나, [프로젝트] > [기존 항목 추가]로 이동하여 기존 코드 파일을 프로젝트에 추가합니다.
//   6. 나중에 이 프로젝트를 다시 열려면 [파일] > [열기] > [프로젝트]로 이동하고 .sln 파일을 선택합니다.
