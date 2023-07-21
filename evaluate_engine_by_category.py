from typing import Literal

from puzzle.evaluate_engine import evaluate_engine_by_category


def evaluate_category(category: str, depth: int, algorithm: Literal["minimax", "abp", "abpi"] = "abpi", limit=None):
    print(f'\nEvaluating for depth = "{depth}" and algorithm = "{algorithm}"...')
    
    score, average_time = evaluate_engine_by_category(category, depth, algorithm=algorithm, limit=limit)

    print(f'Average time per move for category "{category}": {average_time} s')
    print(f'Score for category "{category}": {score*100}%')


# for algorithm in ["minimax", "abp", "abpi"]:
#     evaluate_category("mateIn2", 1, algorithm=algorithm, limit=100)
#     evaluate_category("mateIn2", 2, algorithm=algorithm, limit=100)
#     evaluate_category("mateIn2", 3, algorithm=algorithm, limit=100)

# for algorithm in ["minimax", "abp", "abpi"]:
#     evaluate_category("mateIn3", 1, algorithm=algorithm, limit=100)
#     evaluate_category("mateIn3", 2, algorithm=algorithm, limit=100)
#     evaluate_category("mateIn3", 3, algorithm=algorithm, limit=100)

for algorithm in ["abpi"]:
    evaluate_category("middlegame", 1, algorithm=algorithm, limit=10)
    evaluate_category("middlegame", 2, algorithm=algorithm, limit=10)
    evaluate_category("middlegame", 3, algorithm=algorithm, limit=10)
    evaluate_category("middlegame", 4, algorithm=algorithm, limit=10)
    evaluate_category("middlegame", 5, algorithm=algorithm, limit=10)
