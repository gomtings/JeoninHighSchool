End_Line = 20
String_Size = 11
Data_array = []
data = """Lorem ipsum
dolor sit amet
consectetur
adipiscing elit
Duis tristique
Nunc congue nisi
vitae suscipit tellus mauris
<CENTER>
Nunc congue nisi
vitae suscipit tellus mauris
Integer quis
Id venenati
a condimentum vitae
</CENTER>
<RIGHT>
Nisi est sit
amet facilisis magna
Volutpat ac tincidunt
vitae semper quis
</RIGHT>"""

# \n 를 기준으로 문자열을 분리함. 각각 개별 문자열로 만듬....
lines = data.split('\n')
new_data  =[]
temp_string = ""
for d in lines:
    temp =""
    if len(d) > String_Size:
        for i in range(len(d)):
            if d[i] ==' ':
                if i >= 10:
                    if i == 11:
                        temp+='\n'
                    temp+='--'
                else:
                    temp+='-'
            else:
                temp+=d[i]
        print(temp)
        new_data.append(temp)
    else:
        new_data.append(d.replace(" ", "-"))