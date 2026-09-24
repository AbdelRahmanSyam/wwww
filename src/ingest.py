from .extract import main as extract
from .retrieval import rebuild_index

if __name__ == "__main__":
    extract()
    rebuild_index()
