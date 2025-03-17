import os 
import shutil
dir_path1 = "E:/GitHub/JeoninHighSchool/수업예제/class9/test"
dir_path2 = "E:/GitHub/JeoninHighSchool/수업예제/class9/test2"  

try: 
	os.rmdir(dir_path1) # 파일이 존재 하면 삭제가 불가능 하다.
except OSError as e: 
	print("rmdir - Error: %s : %s" % (dir_path1, e.strerror))
	
try: 
	shutil.rmtree(dir_path2) # 파일이 존재하는 폴더를 삭제 한다. 
except OSError as e: 
	print("rmtree - Error: %s : %s" % (dir_path2, e.strerror))