class FastFood():
    __menu = "" # 매뉴 
    __price = 0 # 물품 가격
    __purchase_price = 0 # 구입 가격
    x = None
    def __init__(self,x):
        self.x = MenuProc()
    def costCal(self,Number):
        self.__purchase_price = self.__price * Number
        self.x.realpay +=self.__purchase_price
        print("구입 가격 : {}".format(self.__purchase_price))
    
    def set__price(self,num):
        self.__price = num

    def set__menu(self,menu):
        self.__menu = menu

    def get__price(self):
        return self.__price
    
    def get__menu(self):
        return self.__menu
    
    def getpurchase_price(self):
        return self.__purchase_price

    def toString(self):
        print("==========매뉴 선택============")
        print("햄버거(H,h)/치킨조각(C,c),아이스크림(I,i)/감자튀김(P,p)")
        return ""

class MenuProc():
    food = ""
    pay = 0
    realpay = 0
    y = None
    def menuName(self,y):
        if y =='H' or y =='h':
            self.__food="햄버거"
        elif y =='I' or y =='i':
            self.__food="아이스크림"
        elif y =='P' or y =='p':
            self.__food="감자튀김"
        elif y =='C' or y =='c':
            self.__food="치킨조각"
        else:
            pass
        return self.__food

    def vaLue(self,y):
        if y =='H' or y =='h':
            self.__pay=2500
        elif y =='I' or y =='i':
            self.__pay=1500
        elif y =='P' or y =='p':
            self.__pay=3000
        elif y =='C' or y =='c':
            self.__pay=1000
        else:
            pass
        return self.__pay
    
    def getrealpay(self):
        return self.realpay
class FastFoodTest ():
    if __name__ == "__main__":
        x = 0
        FastFood = FastFood(x)
        while True :
            print(FastFood.toString())
            x=input("해당 문자를 입력하세요. 종료는 n 또는 N:")
            if x=='N' or x=='n':
                break
            FastFood.set__price(FastFood.x.vaLue(x))
            FastFood.set__menu(FastFood.x.menuName(x))
            print("* 매뉴: "+str(FastFood.get__menu())+"      "+"* 가격: "+str(FastFood.get__price()))
            FastFood.costCal(int(input("개수를 입력하세요 : ")))
        print("전체 구입 가격 :"+str(FastFood.x.getrealpay()))
        a=int(input("받은 돈:"))
        print("거스름 돈: "+str(a- FastFood.x.getrealpay())+"입니다." )
    # Fastfood 클래스 객체  선언
    #메뉴 입력 – 문자 n을 입력하면 반복문 종료
    #Fastfood 객체 생성, 메뉴로 입력 받은 문자를 생성자 매개변수로 전달
    #사용자로부터 구입개수 입력 받아 costCal() 메소드 매개변수로 전달
    #구입 가격 출력
    #반복문 종료 후 거스름돈 계산하여 출력 