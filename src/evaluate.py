import json, statistics, time
from .config import DATA
from .retrieval import search

def main():
    cases = json.loads((DATA / "evaluation_questions.json").read_text(encoding="utf-8"))
    results, timings = [], []
    for case in cases:
        started = time.perf_counter(); hits = search(case["question"]); timings.append(time.perf_counter() - started)
        expected = (case.get("expected_document_id"), case.get("expected_page"))
        found = expected[0] and any((h["document_id"], h["page"]) == expected for h in hits)
        results.append({"id": case["id"], "supported": case["supported"], "top5_hit": bool(found), "seconds": timings[-1]})
    supported = [r for r in results if r["supported"]]
    print(json.dumps({"questions": len(results), "top5_recall": sum(r["top5_hit"] for r in supported) / len(supported) if supported else None, "median_seconds": statistics.median(timings), "results": results}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
