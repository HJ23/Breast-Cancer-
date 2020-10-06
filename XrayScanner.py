import torch
import numpy as np
import cv2
import torchvision
from matplotlib import  pyplot
import torchvision.transforms as transforms
from PIL import Image




def conv_block(in_ch,out_ch):
  network=[torch.nn.Conv2d(in_ch,out_ch,3,1,1)]
  network+=[torch.nn.BatchNorm2d(out_ch)]
  network+=[torch.nn.LeakyReLU(0.1)]
  return torch.nn.Sequential(*network)





class custom_model(torch.nn.Module):
  def __init__(self):
    super(custom_model,self).__init__()
    
    self.downsample=torch.nn.MaxPool2d(2)
    
    self.network1=conv_block(3,64)
    self.network2=conv_block(64,64)
    # 128
    self.network3=conv_block(64,128)
    self.network4=conv_block(128,128)
    # 64
    self.network5=conv_block(128,256)
    self.network6=conv_block(256,256)
    # 32
    self.network7=conv_block(256,512)
    self.network8=conv_block(512,512)
    # 16
    self.network9= conv_block(512,512)
    self.network10=conv_block(512,512)
    # 8
    self.network11=conv_block(512,1024)
    self.network12=conv_block(1024,1024)
    # 4
#    self.network13=conv_block(512,1024)
#    self.network14=conv_block(1024,1024)
    # 2
#    self.network15=conv_block(1024,2048)
#    self.network16=conv_block(2048,2048)
    # 1

    self.features=conv_block(1024,2)

  def forward(self,input):
    a=self.network1(input)
    b=a+self.network2(a)
    c=self.downsample(b)
    
    a=self.network3(c)
    b=a+self.network4(a)
    c=self.downsample(b)
    
    a=self.network5(c)
    b=a+self.network6(a)
    c=self.downsample(b)
    
    a=self.network7(c)
    b=a+self.network8(a)
    c=self.downsample(b)
    
    a=self.network9(c)
    b=a+self.network10(a)
    c=self.downsample(b)
    
    a=self.network11(c)
    b=a+self.network12(a)
    c=self.downsample(b)
    ###
#    a=self.network13(c)
#    b=a+self.network14(a)
#    c=self.downsample(b)
    
#    a=self.network15(c)
#    b=a+self.network16(a)
#    c=self.downsample(b)
    
    return self.features(c)



class  XRAY:
    def __init__(self):
        self.model=custom_model()
        self.model.load_state_dict(torch.load("xray.pth",map_location=torch.device('cpu')))
        self.transfoms=transforms.Compose([
        transforms.Resize((1024,1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
        self.model.eval()
        self.labels={0:'Benign', 1:'Malignant'}

    def forward(self,image):
        tensor=self.transfoms(image)
        out=self.model(tensor.unsqueeze(dim=0))

        out=torch.nn.Softmax(dim=1)(out)
        
        # get label of output 
        preds = torch.softmax(out, dim=1)
        pred, class_idx = torch.max(preds, dim=1)
        row_max, row_idx = torch.max(pred, dim=1)
        col_max, col_idx = torch.max(row_max, dim=1)
        predicted_class = class_idx[0, row_idx[0, col_idx], col_idx]
        
        print('Predicted Class : ', self.labels[predicted_class.item()])
        
        # start displaying heatmap result

        ten=out[0].detach().cpu()[predicted_class.item()]
        ten=(ten-ten.min())/(ten.max()-ten.min())

        ten.apply_(lambda x:1 if(x>0.80) else 0)



        ten=255*ten.numpy()
        ten=np.array(ten,dtype=np.uint8)
        abc=cv2.applyColorMap(ten, cv2.COLORMAP_JET)
        abc=cv2.resize(abc,(1024,1024))

        opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        imgray=cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)

        _,imbin=cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)

        heatmap=cv2.bitwise_and(abc,abc,mask=imbin)
        dst = cv2.addWeighted(opencvImage, 0.4, heatmap, 0.6, 0.0)

        cv2.imwrite("./static/results/res.png",dst)

        return self.labels[predicted_class.item()]
        
