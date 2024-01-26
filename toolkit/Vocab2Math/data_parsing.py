import pandas as pd
import torch
from transformers import BertModel, BertTokenizer
from tqdm import tqdm
import time
import os
import pickle


torch.manual_seed(42)
torch.mps.manual_seed(42)

dir_to_save = 'parsed_data'
os.makedirs(dir_to_save, exist_ok=True)


if __name__ == '__main__':
    data = {
        'Word': list(),
        'Sim_1': list(),
        'Sim_2': list(),
        'Sim_3': list()
    }
    with open('raw_data.txt', 'r') as f:
        for line in f:
            words = line.strip().split(' ')
            if words[0] == ':':
                if words[1] in ['capital-common-countries', 'capital-world', 'currency', 'city-in-state']:
                    continue
                else:
                    break
            else:
                data['Word'].append(words[0])
                data['Sim_1'].append(words[1])
                data['Sim_2'].append(words[2])
                data['Sim_3'].append(words[3])

    data = pd.DataFrame(data)

    print('=' * 100 + '\n' + 'Generated dataframe from raw!')

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    print('Model Loaded!')

    vocabs = set(data['Word'].tolist() + data['Sim_1'].tolist() + data['Sim_2'].tolist() + data['Sim_3'].tolist())
    vocabs = pd.DataFrame({'vocabs': [i for i in vocabs]})

    encoding = tokenizer.batch_encode_plus(vocabs['vocabs'],
                                           padding=True,
                                           truncation=True,
                                           return_tensors='pt',
                                           add_special_tokens=True
                                           )
    input_ids = encoding['input_ids']
    attention_mask = encoding['attention_mask']

    with torch.no_grad():
        start = time.time()
        outputs = model(input_ids, attention_mask=attention_mask)
        word_embeddings = outputs.last_hidden_state
        end = time.time()
    elapsed = end - start
    print(f'Embeddings generated! - Time elapsed: {elapsed} s')

    to_save = dict()
    for idx, word in tqdm(enumerate(vocabs['vocabs'].to_list()), total=len(vocabs['vocabs'])):
        to_save[word] = word_embeddings.mean(dim=1)[idx]

    data['y'] = data['Sim_1'].apply(lambda x: to_save[x]) + data['Sim_2'].apply(lambda x: to_save[x]) - data['Sim_3'].apply(lambda x: to_save[x])
    data['x'] = data['Word'].apply(lambda x: to_save[x])

    #
    data.to_pickle(os.path.join(dir_to_save, 'parsed_data.pkl'))
    print('=' * 100 + '\n' + 'Parsed data saved at: ' + os.path.join(os.getcwd(), dir_to_save, 'parsed_data.pkl'))

    with open(os.path.join(dir_to_save, 'embeddings.pkl'), 'wb') as f:
        pickle.dump(to_save, f)
    print('Embedding result saved at: ' + os.path.join(os.getcwd(), dir_to_save, 'embeddings.pkl') + '\n' + '=' * 100)
