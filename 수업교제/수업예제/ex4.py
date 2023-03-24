class Dictionary():
    __Dictionary = {'APPLE':'사과'}
    def add_Dictionary(self,key,value):
        if key in self.__Dictionary:
            print("이미 있는 단어 입니다.")
        else:
            self.__Dictionary[key] = value
            print("추가 되었습니다.") 
    def Search(self,key):
        if key in self.__Dictionary:
            value = self.__Dictionary.get(key)
            print("{} 의 뜻은 : {} 입니다.".format(key,value))
        else:
            print("단어를 찾을수 없습니다.")

class main():
    if __name__ == "__main__":
        Dictionary = Dictionary()