import shutil  
import os  
  
folder_path = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus_thumbnail_200px'  
  
if os.path.exists(folder_path):  
    shutil.rmtree(folder_path)  
    print(f"文件夹 '{folder_path}' 已成功删除。")
else:  
    print(f"文件夹 '{folder_path}' 不存在。")