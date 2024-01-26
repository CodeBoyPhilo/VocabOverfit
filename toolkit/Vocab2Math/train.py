import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from model import WordMapper
from tqdm import tqdm
torch.manual_seed(42)


if __name__ == '__main__':
    device = 'mps'
    data = 'parsed_data/parsed_data.pkl'
    data = pd.read_pickle(data)

    with open('parsed_data/embeddings.pkl', 'rb') as f:
        embeddings = pickle.load(f)

    dim = data.loc[0,'x'].shape[0]

    embedding_set = torch.empty((0, dim))
    for tensor in embeddings.values():
        tensor = torch.reshape(tensor, (1, dim))
        embedding_set = torch.cat((embedding_set, tensor), dim=0)

    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

    train_x = trainset['x'].tolist()
    train_y = trainset['y'].tolist()
    test_x = testset['x'].tolist()
    test_y = testset['y'].tolist()

    train_x_y = [(x, y) for x, y in zip(train_x, train_y)]
    test_x_y = [(x, y) for x, y in zip(test_x, test_y)]

    trainset = TensorDataset(*map(torch.stack, zip(*train_x_y)))
    testset = TensorDataset(*map(torch.stack, zip(*test_x_y)))
    trainloader = DataLoader(trainset, batch_size=256, shuffle=True)
    testloader = DataLoader(testset)

    model = WordMapper(dim, dim*4, dim*2, embedding_set).to(device)

    num_epochs = 10
    optimizer = torch.optim.Adam(model.parameters(), lr=4e-3)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=4e-3,
                                                    steps_per_epoch=len(trainloader), epochs=num_epochs,
                                                    three_phase=True)

    total_batches =  num_epochs * len(trainloader)

    op = torch.tensor([1.0, 1.0, -1.0]).to('mps')

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0

        pbar = tqdm(trainloader, total=len(trainloader), desc='Epoch {:d}'.format(epoch))
        for X_batch, y_batch in pbar:
            X_g = X_batch.to(device)
            y_g = y_batch.to(device)

            optimizer.zero_grad()
            output = model(X_g)[0]
            loss = -F.cosine_similarity(torch.matmul(op, output), X_g).mean()
            loss.backward()
            optimizer.step()
            scheduler.step()

            train_loss += loss.item()

            avg_loss = train_loss / (pbar.n + 1)
            pbar.set_postfix_str(f"Average Loss: {avg_loss:.4f}")

        avg_loss = train_loss / len(trainloader)
        print(f"Epoch {epoch} Average Loss: {avg_loss:.4f}")

    # test_x_tensor = torch.stack(test_x).to(device)
    # test_y_tensor = torch.stack(test_y).to(device)

    # Switch to evaluation mode
    model.eval()

    single_test_x = embeddings['man']

    for key, val in embeddings.items():
        if torch.equal(val, single_test_x):
            print(key)

    single_test_x = single_test_x.unsqueeze(0).to(device)  # Add batch dimension and send to device
    with torch.no_grad():
        # Make prediction on the single observation
        single_output = model(single_test_x)

        # Compute cosine similarity between the output and the label for this single observation
        cos_sim_single = F.cosine_similarity(torch.matmul(op, single_output), single_test_x)
        final_cos_sim_single = cos_sim_single.item()

    # Print or use the cosine similarity for the single observation
    print(f"Cosine Similarity for Single Observation: {final_cos_sim_single}")
    # match1 = model.match1.flatten().to('cpu')

    all_words = [(word, embed) for word, embed in embeddings.items()]

    match1, match2, match3 = model.pair()

    print(all_words[match1.to('cpu')][0])
    print(all_words[match2.to('cpu')][0])
    print(all_words[match3.to('cpu')][0])
