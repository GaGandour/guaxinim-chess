from puzzle.evaluate_engine import evaluate_engine_by_category


def evaluate_category(category: str, limit=None):
    score, average_time = evaluate_engine_by_category(category, limit=limit)

    print(f"""Average time for category "{category}": {average_time} s""")
    print(f"""Score for category "{category}": {score*100}%""")


evaluate_category("mateIn2", limit=100)
