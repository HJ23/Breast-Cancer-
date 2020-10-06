import torch
import numpy as np
import cv2
import torchvision
from matplotlib import  pyplot
import torchvision.transforms as transforms
from PIL import Image


class Dmodel(torch.nn.Module):
  def __init__(self):
    super(Dmodel,self).__init__()
    self.featureEX=torchvision.models.densenet201(pretrained=True)
    for layer in self.featureEX.parameters():
      layer.requires_grad=False
    self.featureEX.classifier=torch.nn.Linear(1920,2)
    self.featureEX.classifier.requires_grad=True
  def forward(self,inp):
    return self.featureEX(inp)

class CellScanner:
    def __init__(self):
        self.transformer=transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
        self.model=Dmodel()
        self.model.load_state_dict(torch.load("cell.pth",map_location=torch.device('cpu')))
        self.model.eval()
        
    def forward(self,image):
        tensor=self.transformer(image)
        out=self.model(tensor.unsqueeze(dim=0))
        out=torch.nn.Softmax()(out)[0]

        if(out[0]>out[1]):
            return 0
        else:
            return 1
            