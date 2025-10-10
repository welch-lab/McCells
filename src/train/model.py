import torch.nn as nn
import torch.nn.functional as F

class SimpleNN(nn.Module):
    """
    A simple feed-forward neural network based on the architecture
    from the old_reference notebooks.
    """
    def __init__(self, input_dim, output_dim):
        super(SimpleNN, self).__init__()
        
        # Hidden layer dimensions from the reference notebook
        hidden_dim_1 = 2048
        hidden_dim_2 = 1024
        hidden_dim_3 = 256

        self.input_layer = nn.Sequential(
            nn.Linear(input_dim, hidden_dim_1),
            nn.BatchNorm1d(hidden_dim_1),
            nn.ReLU()
        )
        
        self.hidden_layer_1 = nn.Sequential(
            nn.Linear(hidden_dim_1, hidden_dim_2),
            nn.BatchNorm1d(hidden_dim_2),
            nn.ReLU()
        )

        self.hidden_layer_2 = nn.Sequential(
            nn.Linear(hidden_dim_2, hidden_dim_3),
            nn.BatchNorm1d(hidden_dim_3),
            nn.ReLU()
        )
        
        self.output_layer = nn.Linear(hidden_dim_3, output_dim)
        
    def forward(self, x):
        x = self.input_layer(x)
        x = self.hidden_layer_1(x)
        x = self.hidden_layer_2(x)
        x = self.output_layer(x)
        
        # The final softmax converts the raw scores (logits) into probabilities,
        # which is what our MarginalizationLoss function expects.
        x = F.softmax(x, dim=1)
        
        return x
