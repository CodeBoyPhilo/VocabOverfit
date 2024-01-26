import os
import pathlib
import pandas as pd
import numpy as np
import torch
from transformers import BertModel, BertTokenizer
from tqdm import tqdm
import time
import copy
from typing import Tuple, Dict, List, Optional
import dgl
import logging
logging.basicConfig(level=logging.INFO)


def check_file_header(file: pd.DataFrame):
    allowed_header = ['Vocabulary', 'Parts of Speech', 'CH-meaning', 'EN-meaning']
    file_header = file.columns.tolist()
    mismatch = [head for head in file_header if head not in allowed_header]
    missing = [head for head in allowed_header if head not in file_header]
    if len(mismatch) > 0:
        raise Exception(f'The header of the file should be in {allowed_header}, but found missing: {mismatch}')
    elif len(missing) > 0:
        raise Exception(f'The following required columns are missing: {missing}')
    return None

def txt_embedding_to_dict(file_path):
    if not file_path.endswith('.txt'):
        raise ValueError("Only .txt format supported at this moment")

    to_dict = dict()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            vocab = line.split()[0]
            embedding = torch.tensor([float(i) for i in line.split()[1:]])

            if vocab not in to_dict:
                to_dict[vocab] = [embedding]
            else:
                to_dict[vocab].append(embedding)
    return to_dict


class NotLoadedError(Exception):
    def __init__(self, message):
        super().__init__(message)


class VocabCloud:
    def __init__(self):
        self.vocab = None
        self.vocab_name = None
        self.embedding = None
        self.id_lst = list()
        self.vocab_id = dict()
        self.id_vocab = dict()
        self.id_embedding = dict()
        self.similarity_matrix = None
        self.src_and_dst = None
        self.edge_features = None
        self.df_graph = None
        self.pruned_df_graph = None
        self.dgl_graph = None
        self.pruned_dgl_graph = None
        self.pruned_id_vocab = None

    def load_vocab(self, vocab_file: str) -> "VocabCloud":
        """
        Load built-in vocabulary files or from path specified, then return self for method chaining

        Parameters
        ----------
        vocab_file: str or pandas.DataFrame
            Name of built-in vocabulary files, possible options are: ['GRE'],
            or a pandas.DataFrame

        Returns
        ----------
        self: VocabCloud
            Updates the `self.vocab` attribute with loaded vocabulary


        """
        if isinstance(vocab_file, str) and vocab_file in ['GRE']:
            gre_path = os.path.join(os.path.dirname(__file__), 'built-in-data/gre.csv')
            vocab = pd.read_csv(gre_path)
            self.vocab = vocab
            self.vocab_name = vocab_file.lower()

        elif isinstance(vocab_file, pd.DataFrame):
            check_file_header(vocab_file)
            self.vocab = vocab_file
            self.vocab_name = 'custom_data'

        else:
            raise ValueError(f'Not recognised option: {vocab_file}')

        return self

    def create_embedding(self, model_name: str = 'bert-base-uncased', output_file: Optional[str] = None) -> "VocabCloud":
        """
        Using a specified model to create embeddings

        Currently only BERT models are accepted. Will expand the choices in future version.

        Parameters
        ----------
        model_name: str
            Defaults to 'bert-base-uncased'
            Path to local directory of the downloaded model, or a HuggingFace directory

        output_file: Optional[str]
            An optional parameter, specifies whether to save the generated embedding vectors to a txt file locally.
            A string of local path is expected if desires to save the file for future use.
            Defaults to None

        Returns
        -------
        self: VocabCloud
            Updates the `self.embedding` attribute with the generated embeddings.
                self.embedding: Dict[str, torch.Tensor]
                    A dictionary storing the vocabulary's embeddings

        """

        if self.vocab is None:
            raise NotLoadedError('No vocabulary file is loaded yet. Please load with load_vocab()')

        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(model_name)

        encoding = tokenizer.batch_encode_plus(self.vocab['EN-meaning'],
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
        logging.info(f"Successfully extracted embeddings - Elapsed in {time.strftime('%M:%S', time.gmtime(elapsed))}")

        self.embedding = dict()

        if output_file is None:
            for idx, vocab in tqdm(enumerate(self.vocab['Vocabulary'].to_list()), total=len(self.vocab['Vocabulary'])):
                if ' ' in vocab:
                    reformat_vocab = vocab.replace(' ', '-')
                    logging.warning(f"Word {vocab} could interfere with data writing, replaced with {reformat_vocab}")
                else:
                    reformat_vocab = vocab
                self.embedding[reformat_vocab] = word_embeddings.mean(dim=1)[idx]

        else:
            path_to_save = os.path.join(os.getcwd(), output_file, f"{self.vocab_name}_embedding.txt")
            with open(path_to_save, "w") as f:
                for idx, vocab in tqdm(enumerate(self.vocab['Vocabulary'].to_list()), total=len(self.vocab['Vocabulary'])):
                    if ' ' in vocab:
                        reformat_vocab = vocab.replace(' ', '-')
                        logging.warning(f"Word {vocab} could interfere with data writing, replaced with {reformat_vocab}")
                    else:
                        reformat_vocab = vocab
                    self.embedding[reformat_vocab] = word_embeddings.mean(dim=1)[idx]
                    f.write(reformat_vocab + ' ' + ' '.join(map(str, word_embeddings.mean(dim=1)[idx].numpy())) + '\n')
            logging.info(f"Saved embeddings to {path_to_save}")

        return self

    def load_embedding(self, embedding_path: str) -> "VocabCloud":
        """
        Load the saved embedding vectors from local.

        Parameters
        ----------
        embedding_path: str
            A string of local path to the saved embedding vectors. Only txt file is supported at the moment

        Returns
        -------
        self: VocabCloud
            Updates the self.embedding attribute with the loaded embedding vectors

        """

        if embedding_path in ['GRE']:
            embedding_path = os.path.join(os.path.dirname(__file__), 'built-in-data/gre_embedding.txt')

        self.embedding = txt_embedding_to_dict(embedding_path)
        return self

    def get_vocab_integer_id(self, embedding: Dict[str, torch.Tensor]) -> "VocabCloud":
        """
        Process the vocabs dictionary and update the object state, then return self for method chaining.

        This method processes the given vocabulary embeddings and updates the object's internal state
        with new attributes derived from the vocabs. It is designed for method chaining.

        Parameters
        ----------
        embedding : Dict[str, torch.Tensor]
            The generated vocabulary embedding in dict format.

        Returns
        -------
        self: VocabCloud
            The instance itself with updated attributes, allowing for method chaining.
            The updated attributes are:
                id_lst : List[int]
                    A list of integer node ids for each vocabulary node.
                vocab_id : Dict[str, List[int]]
                    A dictionary mapping vocabularies to their corresponding ids. A vocabulary may correspond to multiple ids.
                id_vocab : Dict[int, str]
                    A dictionary mapping each id to its corresponding vocabulary.
                id_embedding : Dict[int, torch.Tensor]
                    A dictionary storing the embedding vector for each vocabulary based on the integer id.
        """

        """
        Example usage:
        (using list to represent tensor for simplicity)

        sample = {
        'apple': [[1,1,2], [2,3,1]],
        'banana': [[1,0,1]],
        'orange': [[0,0,0], [1,1,1]]
        }

        output:
            id_list: [0, 1, 2, 3, 4]

            vocab_id: {'apple': [0, 1], 'banana': [2], 'orange': [3, 4]}

            id_vocab: {0: 'apple', 1: 'apple', 2: 'banana', 3: 'orange', 4: 'orange'}

            id_embedding: {0: [1, 1, 2], 1: [2, 3, 1], 2: [1, 0, 1], 3: [0, 0, 0], 4: [1, 1, 1]}
        """

        idx = 0
        for vocab, embedding_lst in embedding.items():
            self.vocab_id[vocab] = [idx]
            self.id_vocab[idx] = vocab
            self.id_embedding[idx] = embedding_lst[0]
            self.id_lst.append(idx)
            # Handle vocabularies with multiple embedding vectors (meanings)
            if len(embedding_lst) > 1:
                for embedding in embedding_lst[1:]:
                    idx += 1
                    self.vocab_id[vocab].append(idx)
                    self.id_vocab[idx] = vocab
                    self.id_embedding[idx] = embedding
                    self.id_lst.append(idx)
            idx += 1
        return self

    def get_cosine_similarity_matrix(self) -> "VocabCloud":
        """
        Calculates the cosine similarity of the embedding vectors

        Returns
        -------
        self: VocabCloud
            Updates the self.similarity_matrix attribute
                self.similarity_matrix: torch.Tensor
                    A tensor of square matrix of the cosine similarities

        """
        embeddings_matrix = torch.stack(list(self.id_embedding.values()))
        norm_embeddings_matrix = embeddings_matrix / embeddings_matrix.norm(dim=1, keepdim=True)
        self.similarity_matrix = torch.matmul(norm_embeddings_matrix, norm_embeddings_matrix.T)
        return self

    def get_edge_info(self) -> "VocabCloud":
        """
        Get the edge data for generating graphs

        Returns
        -------
        self: VocabCloud
            Updates the self.src_and_dst attributes and self.edge_features attributes
                self.src_and_dst: numpy.array
                    A numpy array with each row specifying the source and destination node id's.
                self.edge_features: torch.Tensor
                    A tensor of the similarity score of an edge
        """
        N = self.similarity_matrix.shape[0]
        self.src_and_dst = np.array([[src, dst] for src in range(N) for dst in range(N) if src != dst])
        self.edge_features = self.similarity_matrix[self.src_and_dst[:, 0], self.src_and_dst[:, 1]]
        return self

    def build_df_graph(self) -> "VocabCloud":
        """
        Build a dataframe with necessary data to construct a dgl graph.

        Comparing to a dgl graph, the DataFrame ignored the nodes' features.
        This is made deliberately considering the use case of such dataframe graph and computational efficiency.
        Though these node features can be always manually added outside the function.

        Returns
        -------
        self: VocabCloud
            Updates the self.df_graph attributes with the builtd dataframe.
            The resultant pandas Dataframe has the following columns:
                src: source node id
                dst: destination node id
                similarity: the cosine similarity of the edge between src and dst
                Vocab_src: the vocabulary of the source node
                Vocab_dst: the vocabulary of the destination node

        """

        if self.embedding is not None:
            self.get_vocab_integer_id(self.embedding)
            self.get_cosine_similarity_matrix()
            self.get_edge_info()

        self.df_graph = pd.DataFrame({
            'src': self.src_and_dst[:, 0],
            'dst': self.src_and_dst[:, 1],
            'similarity': self.edge_features.tolist()
        })

        self.df_graph['Vocab_src'] = self.df_graph['src'].apply(lambda x: self.id_vocab[x])
        self.df_graph['Vocab_dst'] = self.df_graph['dst'].apply(lambda x: self.id_vocab[x])

        return self

    def prune_df_graph(self, threshold: float = 0.9, prune_node=True) -> "VocabCloud":

        """
        Prune the dataframe graph based on a similarity threshold

        Parameters
        ----------
        threshold: float
            A float specifying the minimum similarity score to keep an edge.
            Defaults to 0.9.

        prune_node: bool
            Whether to also prune the nodes that do not have a connection with other nodes, after pruned the edges
            If True, the resultant pruned dataframe will only contain data of edges that have similarity score higher
            than the threshold.
            If False, the resultant pruned dataframe will force the source node to connect with itself to keep the
            node but prunes the edge.
            Defaults to True

        Returns
        -------
        self: VocabCloud
            Updates the self.pruned_df_graph attribute.


        """
        if prune_node:
            self.pruned_df_graph = self.df_graph[~(self.df_graph['similarity'] < threshold)]

            old_new = {
                old: new for new, old in enumerate(self.pruned_df_graph['src'].unique())
            }

            self.pruned_df_graph.loc[:, 'src'] = self.pruned_df_graph['src'].apply(lambda x: old_new[x])
            self.pruned_df_graph.loc[:, 'dst'] = self.pruned_df_graph['dst'].apply(lambda x: old_new[x])
        else:
            self.pruned_df_graph = self.df_graph.copy()
            mask = self.pruned_df_graph['similarity'] < threshold
            self.pruned_df_graph.loc[mask, 'dst'] = self.pruned_df_graph.loc[mask, 'src']
            self.pruned_df_graph.loc[mask, 'Vocab_dst'] = self.pruned_df_graph.loc[mask, 'Vocab_src']
            self.pruned_df_graph.loc[mask, 'similarity'] = 0

        return self

    def build_dgl_graph(self) -> "VocabCloud":
        """
        Build a dgl graph.

        Comparing to a df graph, the dgl graph failed to incorporate the corresponding vocabulary of the node, but
        contains the original embedding vector as a node feature


        Returns
        -------
        self: VocabCloud
            Updates the self.dgl_graph attributes.
        """

        if self.embedding is not None:
            self.get_vocab_integer_id(self.embedding)
            self.get_cosine_similarity_matrix()
            self.get_edge_info()

        self.dgl_graph = dgl.graph(
            (self.src_and_dst[:, 0], self.src_and_dst[:, 1])
        )

        self.dgl_graph.ndata['feature'] = torch.stack(list(self.id_embedding.values()))
        self.dgl_graph.edata['similarity'] = self.edge_features

        return self

    def prune_dgl_graph(self,
                        threshold: float = 0.9,
                        prune_node: bool = True) -> "VocabCloud":
        """
        Prune the dgl graph based on a threshold of cosine similarity

        Parameters
        ----------
        threshold: float
            A float specifying the minimum similarity score to keep an edge.
            Defaults to 0.9.

        prune_node: bool
            Whether to also prune the nodes that do not have a connection with other nodes, after pruned the edges
            If True, the resultant pruned graph will only contain of nodes and edges that have similarity score higher
            than the threshold.
            If False, the resultant pruned graph will keep these nodes with no connection/edge with other nodes
            Defaults to True

        Returns
        -------
        self: VocabCloud
            Updates the self.pruned_dgl_graph attribute.
            Updates the self.pruned_id_vocab attribute if prune_node is set to True

        """
        self.pruned_dgl_graph = copy.deepcopy(self.dgl_graph)
        edges = self.pruned_dgl_graph.edges(form='eid')
        similarities = self.pruned_dgl_graph.edata['similarity']
        edge_to_prune = edges[similarities < threshold]
        self.pruned_dgl_graph.remove_edges(edge_to_prune)
        pruned_id_vocab = None
        if prune_node:
            isolated_nodes = torch.where(self.pruned_dgl_graph.in_degrees() + self.pruned_dgl_graph.out_degrees() == 0)[0]
            self.pruned_dgl_graph.remove_nodes(isolated_nodes)
            if self.id_vocab is not None:
                self.pruned_id_vocab = {node_id: vocab for node_id, vocab in self.id_vocab.items() if
                                        node_id not in isolated_nodes.tolist()}

        return self
