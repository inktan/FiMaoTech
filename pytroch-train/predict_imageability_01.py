# -*- coding: utf-8 -*-

import torch
from tqdm import tqdm

torch.cuda.empty_cache()
import torch
from torchvision import transforms,datasets,models
import os
import pandas as pd
from torch.utils.data import Dataset, DataLoader 
from PIL import Image
import numpy as np
  
class CustomDataset(Dataset): 
    '''
    这里定义预测图像数据所在文件夹
    ''' 
    def __init__(self, img_dir, transform=None):  
        self.img_dir = img_dir  
        self.transform = transform  

        self.roots = []
        self.img_names = []
        self.img_paths = []

        accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")
        for root, dirs, files in os.walk(img_dir):
            for file in files:
                if file.endswith(accepted_formats):
                    self.roots.append(root)
                    self.img_names.append(file)
                    file_path = os.path.join(root, file)
                    self.img_paths.append(file_path)

    def __len__(self):  
        return len(self.img_names)  
  
    def __getitem__(self, idx):  
        image = Image.open(self.img_paths[idx]).convert('RGB')  # 打开图片，转换为RGB格式
        if self.transform:  
            image = self.transform(image)  # 如果有定义转换，则应用转换  
        return image, self.img_names[idx]  # 返回图片和对应的索引  
  
# 定义转换  
transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()]) 

def load_dataset(data_path, batch_size):
    '''
    创建数据集和数据加载器
    '''
    # 训练集图像预处理：缩放裁剪、图像增强、转 Tensor、归一化
    transformation = transforms.Compose(
            [transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
    
    # Load all the images, and transform
    full_dataset = CustomDataset(data_path, transform=transformation)
    
    loader = torch.utils.data.DataLoader(full_dataset, batch_size, shuffle=False)
    return loader
  
def predict(model,device,predict_loader,predict_csv):
    model.to(device)
    model.eval()

    df_list = []
    for batchidx_predict, dt_predict in enumerate(predict_loader):
        images_predict,out_name = dt_predict[0].to(device),dt_predict[1]
        outputs = model(images_predict)
           
        probs, out_label = outputs.max(axis=1)
        probs = probs.detach().cpu().numpy()
        # # print(probs)
        out_label = out_label.detach().cpu().numpy()

        label = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        
        out_label = [label[i] for i in out_label]
        img_df = pd.DataFrame({'out_name':list(out_name),'out_label': out_label,})
        df_list.append(img_df)

        print((batchidx_predict+1)*batch_size,len(predict_loader.dataset))

    result = pd.concat(df_list)
    result.to_csv(predict_csv,index=False)

    print(f'预测结束，已结果文件生成文件，地址位{predict_csv}')

if __name__ == "__main__":
    categories= ['安全度']
    batch_size = 5
    predictn_folder = r'./数据/澳门街景'  # split into training(80%) and validation(20%)
    predict_csv= r"./sense_security__.csv"
    model_path= r"./sense_security_.pth"
    model = torch.load(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    predict_loader = load_dataset(predictn_folder, batch_size)
    predict(model,device,predict_loader,predict_csv)






