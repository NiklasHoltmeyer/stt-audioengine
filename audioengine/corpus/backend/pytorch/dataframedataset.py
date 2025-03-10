import math
import os

import torch
from torch.utils.data import Dataset
from multiprocessing import Pool
from tqdm import tqdm


class DataframeDataset(Dataset):
    """Load Pytorch Dataset from Dataframe
    
    """

    def __init__(self, data_frame, input_key, target_key, transform=None, features=None, load_max_input_length=False, **kwargs):
        super(DataframeDataset).__init__()
        self.data_frame = data_frame
        self.input_key = input_key
        self.target_key = target_key
        self.inputs = self.data_frame[input_key]
        self.targets = self.data_frame[target_key]
        self.transform = transform
        self.features = [input_key, target_key] if features is None else features
        self.len = len(self.inputs)

        self.num_workers = self._load_num_workers(**kwargs)
        self.max_input_length_quantile = .98

        self.max_input_length = self._load_max_input_length() if load_max_input_length else None

    def __len__(self):
        return self.len

    def __str__(self):
        return str(self.info())

    def info(self):
        info = {
            'features': self.features,
            'num_rows': len(self)
        }
        return "Dataset(" + str(info) + ")"

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        data = {
            self.input_key: self.inputs[idx],
            self.target_key: self.targets[idx]
        }

        if self.transform:
            return self.transform(data)

        return data

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:
            return map(self.__getitem__, range(self.__len__()))

        per_worker = int(math.ceil((self.__len__()) / float(worker_info.num_workers)))
        worker_id = worker_info.id
        iter_start = worker_id * per_worker
        iter_end = min(iter_start + per_worker, self.__len__())
        return map(self.__getitem__, range(iter_start, iter_end))
        # return iter(range(iter_start, iter_end))

    def _load_num_workers(self, **kwargs):
        num_workers = kwargs.get("num_workers", None)
        if not num_workers:
            worker_info = torch.utils.data.get_worker_info()
            num_workers = worker_info.num_workers if worker_info else os.cpu_count()
        return num_workers

    def _load_max_input_length(self):
        print(self.inputs[0])
        print("*"*32)
        with Pool(self.num_workers) as p:
            self.input_seq_lengths = list(
                tqdm(p.imap(get_input_len, self.inputs), total=len(self.inputs), miniters=100,
                     desc='getting train input lengths'))
        self.max_input_length = torch.tensor(self.input_seq_lengths).float().quantile(
            self.max_input_length_quantile).int().item()

    @staticmethod
    def collate_fn(input_key, output_key):
        def __call__(batch):
            speeches = [data[input_key] for data in batch]
            sentences = [data[output_key] for data in batch]
            return speeches, sentences

        return __call__


#    @staticmethod
#    def collate_fn(batch):
#        return [(data["input"], data["output"]) for data in batch]
def get_input_len(f):
    t = torch.load(f).squeeze().tolist()
    print(t)
    print("-")
    print(len(t))
    return len(t)

if __name__ == "__main__":
    import pandas as pd
    from torch.utils.data import DataLoader

    data = [("ax", "ay", "asd"), ("bx", "by", "b3"), ("cx", "cy", "c3"), ("dx", "dy", "d3")]
    df = pd.DataFrame(data, columns=['input', 'target', 'random'])
    print(df.head())

    ds = DataframeDataset(data_frame=df, input_key="input", target_key="target", transform=None)
    print("*" * 40)
    print("Len:", len(ds))
    print("Ds", ds)

    # loader = DataLoader(ds, batch_size=3, shuffle=False, num_workers=4)  # collate_fn=DataframeDataset.collate_fn
    # print(loader)
    print("o" * 33)
    for idx in range(0, len(ds)):
        data = ds[idx]
        print(idx, "->", data)
        # pass
    print("*" * 23)
    for d in iter(ds):
        print("dö", d)
    print("xo" * 12)
    print(list(torch.utils.data.DataLoader(ds, num_workers=3)))
    print("ox" * 12)
    print(list(torch.utils.data.DataLoader(ds)))
#    for idx, (x, y) in enumerate(loader):
#        print("x", x, "\t", "y", y)

# asd
