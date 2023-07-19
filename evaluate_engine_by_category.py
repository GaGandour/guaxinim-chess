from puzzle.evaluate_engine import evaluate_engine_by_category


def evaluate_category(category: str, limit=None, depth=3):
    score, average_time = evaluate_engine_by_category(category, limit=limit, depth=depth)

    print(f"""Average time per move for category "{category}": {average_time} s""")
    print(f"""Score for category "{category}": {score*100}%""")


evaluate_category("mateIn2", limit=20, depth=5)
