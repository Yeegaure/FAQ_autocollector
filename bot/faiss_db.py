import faiss
import numpy as np
from pathlib import Path
from utilities import faiss_encode, vectorizer

np.random.seed(42)

DIM = len(vectorizer.vocabulary_)
PATH_INDEX = Path(__file__).resolve().parent.parent / 'data' / 'faiss.index'
PATH_MAP = Path(__file__).resolve().parent.parent / 'data' / 'map.npy'

def load_index():
    PATH_INDEX.parent.mkdir(parents=True, exist_ok=True)
    if PATH_INDEX.exists():
        index = faiss.read_index(str(PATH_INDEX))
        return index
    return faiss.IndexFlatL2(DIM)

def load_mapping():
    if PATH_MAP.exists():
        return np.load(PATH_MAP).tolist()
    return []

def save_index(index):
    faiss.write_index(index, str(PATH_INDEX))

def save_mapping(mapping):
    np.save(PATH_MAP, np.array(mapping))

def add_vector(vector: np.ndarray, sqlite_id: int):
    index = load_index()
    mapping = load_mapping()

    vector = vector.astype('float32').reshape(1, -1)
    if vector.shape[1] != DIM:
        raise ValueError(f"Vector dimension {vector.shape[1]} != expected {DIM}")

    index.add(vector)
    faiss_id = len(mapping)
    mapping.append(sqlite_id)

    save_index(index)
    save_mapping(mapping)
    return faiss_id

def search_vector(vector: np.ndarray, k : int = 10):
    index = load_index()
    mapping = load_mapping()
    vector = vector.astype('float32').reshape(1, -1)
    distances, faiss_ids = index.search(vector, k)
    sqlite_ids = [mapping[i] for i in faiss_ids[0]]
    return sqlite_ids, distances[0]

def search_and_encode(message : str, k : int = 10):
    vector = faiss_encode(message)
    return search_vector(vector, k)


if __name__ == '__main__':
    print("Testing FAISS...")

    test = "интересно😮 так а толку то от педиатра, скажет аллергия или энтеровирус (былотакое), напишите пожалуйста как сьездите. а к дерматологу куда? на сухэ батора?"
    print("input:", test)
    vec = faiss_encode(test)
    print("\nencoded vector shape:", vec.shape)

    print("\nfull vector:")
    print(vec)

    faiss_id = add_vector(vec, sqlite_id=12345)
    print("\nAdded FAISS ID:", faiss_id)

    ids, dist = search_and_encode(test)
    print("\nsearch result SQLite IDs:", ids)
    print("distances:", dist)
