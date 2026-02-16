from app.metrics import compute_metrics

def compute_reward(draft, final):
    metrics = compute_metrics(draft, final)

    edit_score = 1 - metrics["normalized_edit_distance"]
    zero_edit_score = metrics["zero_edit"]
    quality_score = 1 if metrics["readability_ok"] else 0.5

    reward = (
        0.4 * zero_edit_score +
        0.3 * edit_score +
        0.2 * quality_score +
        0.1 * zero_edit_score
    )

    return reward, metrics
