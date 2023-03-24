import random
import numpy as np
import pandas as pd
import csv
#pip3 install numpy
#pip3 install pandas

class suffle:
    music_list = None
    suffle_size = 0
    suffle_list = []
    currentname = ''
    def __init__(self,path):
        #music_list=["1. 애국가", "2. 인생", "3. 소주한잔", "4. 밥만 잘 먹더라", "5. GEE", "6. 태양을 피하는 법", "7. 하루하루", "8. 너 말야", "9. 어쩌라고", "10. 비밀"]
        self.music_list = pd.read_csv(path) #top_view  그래프를 찍기 위한 파일을 open 합니다. 
        self.music_list.columns=["name"]
        self.suffle_list = self.music_list['name'].copy ().to_numpy() # y
        self.suffle_size = len(self.suffle_list) # 전체 플레이 리스트의 크기
        self.currentname = ''
        self.playlist()
    def playlist(self):
        self.suffle_size = len(self.suffle_list)
        for i in range(0,int(self.suffle_size-1)):
            print("{},{}".format(i,self.suffle_list[i]))
    def suffle(self):
        for i in range(0,int(self.suffle_size-1)):
            # 한번 전체가 재생되었으면, 다시 처음부터.
            
            #랜덤하게 하나씩 뽑는다.
            randValue = random.randint(1,self.suffle_size+1) # 4 
            self.currentname = self.suffle_list[randValue]; # 현재 값,,? 4
            self.suffle_list[randValue] = self.suffle_list[self.suffle_size-1]; #8 { 0, 1, 2, 3, 9, 5, 6, 7, 8, 9 };
            self.suffle_list[self.suffle_size-1] = self.currentname; #{ 0, 1, 2, 3, 9, 5, 6, 7, 8, 4 };
            
            self.suffle_size-= 1;
        #A = np.array(self.randIndex,self.suffle_list)    
        #DF3 = pd.DataFrame(A)    
        np.savetxt('C:/Users/LSW/Desktop/전인고/play_list.csv',self.suffle_list, fmt='%s',encoding='UTF-8-sig')
if __name__ == "__main__":
    play_list = 'C:/Users/LSW/Desktop/전인고/play_list.csv'
    print("\n섞기 전 재생 리스트\n");
    mix = suffle(play_list)
    mix.suffle()
    print("\nsuffle 후 재생 리스트\n");
    mix.playlist()
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