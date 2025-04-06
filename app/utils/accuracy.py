def evaluate_hierarchical_metrics(true_keywords, predictions):
    # Step 1: Define the function to calculate the hierarchical score
    def get_relationship_score(pred_kw, pred_path, true_kw):
        if pred_kw == true_kw:
            return 1.0  # exact match

        if pred_path is None:
            return 0.0

        if true_kw in pred_path and pred_kw in pred_path:
            pred_idx = pred_path.index(pred_kw)
            true_idx = pred_path.index(true_kw)
            dist = pred_idx - true_idx

            if dist == 1 or dist == -1:
                return 0.75  # parent or child
            elif abs(dist) == 2:
                return 0.5  # grandparent/grandchild or siblings
            elif abs(dist) == 3:
                return 0.25  # great-grandparent or great-grandchild
            elif abs(dist) > 3:
                return 0.25  # further away in the branch

        return 0.0

    # Step 2: Calculate Hierarchical Recall (AccuracyScore)
    recall_scores = []
    print("📊 Score breakdown per true keyword:\n")
    for true_kw in true_keywords:
        best_score = 0.0
        print(f"True keyword: {true_kw}")
        for pred_kw, path in predictions.items():
            score = get_relationship_score(pred_kw, path, true_kw)
            if score > 0:
                print(f"  ↳ {pred_kw} → path: {path} → score: {score}")
            best_score = max(best_score, score)
        recall_scores.append(best_score)
        print(f"✅ Best score for {true_kw}: {best_score}\n")

    accuracy_score = sum(recall_scores) / len(recall_scores)
    print("🎯 Hierarchical Recall (AccuracyScore):", accuracy_score)

    # Step 3: Calculate Hierarchical Precision
    precision_scores = []
    print("\n📊 Score breakdown per predicted keyword:\n")
    for pred_kw, pred_path in predictions.items():
        best_score = 0.0
        print(f"Predicted keyword: {pred_kw}")
        for true_kw in true_keywords:
            score = get_relationship_score(pred_kw, pred_path, true_kw)
            if score > 0:
                print(f"  ↳ match with {true_kw} → score: {score}")
            best_score = max(best_score, score)
        precision_scores.append(best_score)
        print(f"✅ Best score for {pred_kw}: {best_score}\n")

    precision_score = sum(precision_scores) / len(precision_scores)
    print("🎯 Hierarchical Precision:", precision_score)

    # Step 4: Calculate Hierarchical F1 Score
    if (precision_score + accuracy_score) > 0:
        f1_score = 2 * (precision_score * accuracy_score) / (precision_score + accuracy_score)
    else:
        f1_score = 0.0

    print(f"\n📦 Hierarchical F1 Score: {f1_score}")
    return f1_score
