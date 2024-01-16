import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import random
class RQnet(nn.Module):  # Qnet
    def __init__(self, input_layer, output_layer):
        super(Qnet, self).__init__()
        self.input_layer = input_layer
        self.output_layer = output_layer
        self.fc1 = nn.Linear(self.input_layer, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return x
