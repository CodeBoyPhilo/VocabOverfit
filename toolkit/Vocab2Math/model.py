import torch
import torch.nn as nn
import torch.nn.functional as F


class WordMapper(nn.Module):
    def __init__(self, embedding_dim, hidden_dim_1, hidden_dim_2, embedding_set):
        super().__init__()

        self.match1 = None
        self.match2 = None
        self.match3 = None

        self.transformed1 = None
        self.transformed2 = None
        self.transformed3 = None

        self.embedding_set = F.normalize(embedding_set, p=2, dim=1)

        self.pathway1 = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim_1),
            nn.ReLU(),
            nn.Linear(hidden_dim_1, hidden_dim_2),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(hidden_dim_2, hidden_dim_1),
            nn.ReLU(),
            nn.Linear(hidden_dim_1, embedding_dim)
        )
        self.pathway2 = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim_1),
            nn.ReLU(),
            nn.Linear(hidden_dim_1, hidden_dim_2),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(hidden_dim_2, hidden_dim_1),
            nn.ReLU(),
            nn.Linear(hidden_dim_1, embedding_dim)
        )
        self.pathway3 = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim_1),
            nn.ReLU(),
            nn.Linear(hidden_dim_1, hidden_dim_2),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(hidden_dim_2, hidden_dim_1),
            nn.ReLU(),
            nn.Linear(hidden_dim_1, embedding_dim)
        )

        self.final_transform = nn.Linear(embedding_dim, embedding_dim)

    def find_most_similar(self, vect1, vect2, vect3):
        self.embedding_set = self.embedding_set.to('mps')
        vect1_norm = F.normalize(vect1, p=2, dim=1).unsqueeze(1)
        vect2_norm = F.normalize(vect2, p=2, dim=1).unsqueeze(1)
        vect3_norm = F.normalize(vect3, p=2, dim=1).unsqueeze(1)

        # Broadcasting to compare each vector in the batch against all in embedding_set
        sim_1 = F.cosine_similarity(self.embedding_set.unsqueeze(0), vect1_norm, dim=2)
        sim_2 = F.cosine_similarity(self.embedding_set.unsqueeze(0), vect2_norm, dim=2)
        sim_3 = F.cosine_similarity(self.embedding_set.unsqueeze(0), vect3_norm, dim=2)

        # Extracting indices of most similar embeddings for each vector in the batch
        max_indices_1 = torch.argmax(sim_1, dim=-1)
        max_indices_2 = torch.argmax(sim_2, dim=-1)
        max_indices_3 = torch.argmax(sim_3, dim=-1)

        # Use advanced indexing to extract the most similar embeddings

        return max_indices_1, max_indices_2, max_indices_3

    def forward(self, x):
        self.transformed1 = self.pathway1(x)
        self.transformed2 = self.pathway2(x)
        self.transformed3 = self.pathway3(x)

        return torch.stack([self.transformed1, self.transformed2, self.transformed3], dim=-2)

    def pair(self):
        max_indices_1, max_indices_2, max_indices_3 = self.find_most_similar(self.transformed1,
                                                                             self.transformed2,
                                                                             self.transformed3)

        return max_indices_1, max_indices_2, max_indices_3




