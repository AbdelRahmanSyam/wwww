import argparse
from .retrieval import search

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve UAEU PDF passages")
    parser.add_argument("question")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    for rank, result in enumerate(search(args.question, args.top_k), 1):
        print(f"\n[{rank}] {result['document_title']} — p. {result['page']} (score {result['score']:.3f})")
        print(result["text"])
