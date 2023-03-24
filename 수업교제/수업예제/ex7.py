import random
import numpy as np
import pandas as pd
import csv
#pip3 install numpy
#pip3 install pandas

class suffle:
    music_list = None
    suffle_size = 0
    randIndex = []
    suffle_list = []
    currentPos = 0
    def __init__(self,path):
        self.music_list=["애국가", "인생", "소주한잔", "밥만 잘 먹더라", "GEE", "태양을 피하는 법", "하루하루", "너 말야", "어쩌라고", "비밀"]
        self.randIndex = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
        self.suffle_size = len(self.music_list)
        self.currentPos = 0
        self.currentname = ''
        #self.playlist()
    def playlist(self):
        for i in range(0,self.suffle_size):
            print("{} , {}".format(self.randIndex[i],self.music_list[i]))
     
    def suffle(self):
        # 한번 전체가 재생되었으면, 다시 처음부터.
        for i in range(0,self.suffle_size):
            #랜덤하게 하나씩 뽑는다.
            randValue = random.randint(0,self.suffle_size) # 4 
            self.currentPos = self.randIndex[randValue]; # 현재 값,,? 4
            self.randIndex[randValue] = self.randIndex[self.suffle_size-1]; #8 { 0, 1, 2, 3, 9, 5, 6, 7, 8, 9 };
            self.randIndex[self.suffle_size-1] = self.currentPos; #{ 0, 1, 2, 3, 9, 5, 6, 7, 8, 4 };
            
            self.currentname = self.music_list[randValue]; # 현재 값,,? 4
            self.music_list[randValue] = self.music_list[self.suffle_size-1]; #8 { 0, 1, 2, 3, 9, 5, 6, 7, 8, 9 };
            self.music_list[self.suffle_size-1] = self.currentname; #{ 0, 1, 2, 3, 9, 5, 6, 7, 8, 4 };
            self.suffle_size-= 1;
            
        return self.music_list;
if __name__ == "__main__":
    play_list = 'C:/Users/LSW/Desktop/전인고/play_list.csv'
    mix = suffle(play_list)
    print(mix.suffle())
"""
using namespace std;


char * music_array[10] = { "1. 애국가", "2. 인생", "3. 소주한잔", "4. 밥만 잘 먹더라", "5. GEE", "6. 태양을 피하는 법", "7. 하루하루", "8. 너 말야", "9. 어쩌라고", "10. 비밀" };
char randIndex[10] = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 };

int currentPos;

char* random()
{
	static int suffle_pos = 10;

	// 한번 전체가 재생되었으면, 다시 처음부터.
	if(suffle_pos < 1) {
		printf("\n[전체 1회 재생완료]\n\n");
		suffle_pos = 10;
	}

	// 랜덤하게 하나씩 뽑는다.
	int randValue = rand() % suffle_pos;
	currentPos = randIndex[randValue];
	randIndex[randValue] = randIndex[suffle_pos-1];
	randIndex[suffle_pos-1] = currentPos;
	
	suffle_pos--;
	return music_array[currentPos];
}


char* sequence() {
	if(++currentPos > 9) { currentPos = 0; }
	return music_array[currentPos];
}


int main(void) 
{
	srand((unsigned)time(NULL));
	
	printf("=============== 랜덤 재생 ============\n");
	for(int i = 0; i < 23; i++) {
		printf("%s\n", random());
	}

	printf("=============== 순차 재생 ============\n");
	for(int i = 0; i < 10; i++) {
		printf("%s\n", sequence());
	}

	return 0;            
 
"""