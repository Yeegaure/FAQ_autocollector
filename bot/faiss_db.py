import faiss
import numpy as np
from pathlib import Path

np.random.seed(42)

PATH_INDEX = Path(__file__).resolve().parent.parent / 'data' / 'faiss.index'
PATH_MAP = Path(__file__).resolve().parent.parent / 'data' / 'map.npy'


def load_index(DIM):
    PATH_INDEX.parent.mkdir(parents=True, exist_ok=True)
    if PATH_INDEX.exists():
        return faiss.read_index(str(PATH_INDEX))
    return faiss.IndexFlatL2(DIM)


def load_mapping():
    if PATH_MAP.exists():
        return np.load(PATH_MAP).tolist()
    return []


def save_index(index):
    faiss.write_index(index, str(PATH_INDEX))

def save_mapping(mapping):
    np.save(PATH_MAP, np.array(mapping))


def add_vector(vector, sqlite_id):
    from utilities import vectorizer

    dim = len(vectorizer.vocabulary_)
    index = load_index(dim)
    mapping = load_mapping()

    vector = vector.astype('float32').reshape(1, -1)
    index.add(vector)

    mapping.append(sqlite_id)

    save_index(index)
    save_mapping(mapping)

def search_vector(vector, k=10):
    from utilities import vectorizer

    dim = len(vectorizer.vocabulary_)
    index = load_index(dim)
    mapping = load_mapping()

    if index.ntotal == 0 or not mapping: return [], []

    safe_k = min(k, index.ntotal)

    vector = vector.astype('float32').reshape(1, -1)
    dist, faiss_ids = index.search(vector, safe_k)

    sqlite_ids, distances = [], []

    for faiss_id, distance in zip(faiss_ids[0], dist[0]):
        if faiss_id == -1: continue
        if faiss_id >= len(mapping): continue

        sqlite_ids.append(mapping[faiss_id])
        distances.append(float(distance))
    return sqlite_ids, distances

def search_and_encode(message, k=10):
    from utilities import faiss_encode
    vector = faiss_encode(message)
    return search_vector(vector, k)


if __name__ == '__main__':
    print("Testing FAISS...")

    test = "интересно😮 так а толку то от педиатра, скажет аллергия или энтеровирус (былотакое), напишите пожалуйста как сьездите. а к дерматологу куда? на сухэ батора?"
    print("input:", test)
    vec = faiss.faiss_encode(test)
    print("\nencoded vector shape:", vec.shape)

    print("\nfull vector:")
    print(vec)

    faiss_id = add_vector(vec, sqlite_id=12345)
    print("\nAdded FAISS ID:", faiss_id)

    ids, dist = search_and_encode(test)
    print("\nsearch result SQLite IDs:", ids)
    print("distances:", dist)
