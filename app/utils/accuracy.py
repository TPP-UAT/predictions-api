def evaluate_predictions(original_keywords_with_paths, predictions_with_prob):
    # 🔧 SCORE CONFIGURATION
    EXACT_SCORE = 1.0
    PARENT_CHILD_SCORE = 0.9
    GRAND_REL_SCORE = 0.75       # grandparent, grandchild, almost full branch
    GREAT_REL_SCORE = 0.5        # great-grandparent/child, nearby paths
    NO_REL_SCORE = 0.0

    def get_relationship_score(pred_kw, pred_path, true_kw, true_path):
        if pred_path is None or true_path is None:
            return NO_REL_SCORE, "no path"

        # ✅ Case 1: exact match
        if pred_kw == true_kw:
            return EXACT_SCORE, "exact match"

        # ✅ Case 2: true_kw is in the predicted path → ancestor
        if true_kw in pred_path:
            idx = pred_path.index(true_kw)
            dist_to_leaf = len(pred_path) - 1 - idx
            if dist_to_leaf == 1:
                return PARENT_CHILD_SCORE, "parent"
            elif dist_to_leaf == 2:
                return GRAND_REL_SCORE, "grandparent"
            elif dist_to_leaf == 3:
                return GREAT_REL_SCORE, "great-grandparent"

        # ✅ Case 3: pred_kw is in the true path → descendant
        if pred_kw in true_path:
            idx = true_path.index(pred_kw)
            dist_to_leaf = len(true_path) - 1 - idx
            if dist_to_leaf == 1:
                return PARENT_CHILD_SCORE, "child"
            elif dist_to_leaf == 2:
                return GRAND_REL_SCORE, "grandchild"
            elif dist_to_leaf == 3:
                return GREAT_REL_SCORE, "great-grandchild"

        # ❗ Case 4: no direct relationship → measure steps in the tree
        shared = 0
        for a, b in zip(pred_path, true_path):
            if a == b:
                shared += 1
            else:
                break

        up_steps = len(pred_path) - shared
        down_steps = len(true_path) - shared
        total_steps = up_steps + down_steps

        score = max(1.0 - 0.15 * total_steps, NO_REL_SCORE)
        explanation = f"{up_steps}↑ + {down_steps}↓ = {total_steps} steps → score {score:.2f}"
        return score, explanation

    # --- Weighted Recall ---
    recall_scores = []
    print("\n📊 Comparing each original term with all predicted paths (probability-weighted):\n")

    for true_kw, true_paths in original_keywords_with_paths.items():
        best_weighted_score = 0.0
        best_explanation = ""
        best_pred_kw = None

        print(f"# {true_kw}")
        for pred_kw, pred_data in predictions_with_prob.items():
            pred_path = pred_data.get('path')
            prob = pred_data.get('prob', 1.0)

            # ✅ Special case: exact match
            if pred_kw == true_kw:
                score = EXACT_SCORE
                weighted_score = score * prob
                explanation = "exact match"

                print(f"#   {pred_kw} (exact) → score {score:.2f}, prob {prob:.2f} → weighted {weighted_score:.2f} ({explanation})")

                if weighted_score > best_weighted_score:
                    print(f"✔️ New best score for {true_kw}: {weighted_score:.2f} with {pred_kw} (exact) → {explanation}")
                    best_weighted_score = weighted_score
                    best_explanation = f"{explanation} with prob {prob:.2f}"
                    best_pred_kw = pred_kw
                continue  # skip the path loop

            for true_path in true_paths:
                score, explanation = get_relationship_score(pred_kw, pred_path, true_kw, true_path)
                weighted_score = score * prob

                if score > 0:
                    print(f"#   {pred_kw} → {pred_path} vs {true_path}: score {score:.2f}, prob {prob:.2f} → weighted {weighted_score:.2f} ({explanation})")

                if weighted_score > best_weighted_score:
                    print(f"✔️ New best score for {true_kw}: {weighted_score:.2f} with {pred_kw} vs {true_path} → {explanation}")
                    best_weighted_score = weighted_score
                    best_explanation = f"{explanation} with prob {prob:.2f}"
                    best_pred_kw = pred_kw

        recall_scores.append(best_weighted_score)

        if best_weighted_score == 0:
            print("#   ❌ not even close\n")
        else:
            print(f"#   ✅ Best score for {true_kw}: {best_weighted_score:.2f} ({best_pred_kw}: {best_explanation})\n")

    recall_weighted = sum(recall_scores) / len(recall_scores)
    print(f"# 🎯 Weighted Recall = ({' + '.join(f'{s:.2f}' for s in recall_scores)}) / {len(recall_scores)} = {recall_weighted:.4f}")
    print("# Weighted recall shows how well we covered the real terms, adjusted by model certainty")

    # --- Weighted Precision ---
    precision_scores = []
    print("\n📌 Evaluating precision of predicted terms (probability-weighted):\n")

    for pred_kw, pred_data in predictions_with_prob.items():
        pred_path = pred_data.get('path')
        prob = pred_data.get('prob', 1.0)

        best_score = 0.0
        best_explanation = ""

        for true_kw, true_paths in original_keywords_with_paths.items():
            if pred_kw == true_kw:
                score = EXACT_SCORE
                explanation = "exact match"
            else:
                score = 0.0
                explanation = ""
                for true_path in true_paths:
                    s, expl = get_relationship_score(pred_kw, pred_path, true_kw, true_path)
                    if s > score:
                        score = s
                        explanation = expl

            if score > best_score:
                best_score = score
                best_explanation = explanation

        weighted_score = best_score * prob
        precision_scores.append(weighted_score)

        print(f"# {pred_kw:5} | Path: {pred_path} | Score: {best_score:.2f}, prob: {prob:.2f} → weighted: {weighted_score:.2f} → {best_explanation}")

    precision_weighted = sum(precision_scores) / len(precision_scores)
    print(f"\n# ✅ Weighted Precision = ({' + '.join(f'{s:.2f}' for s in precision_scores)}) / {len(precision_scores)} = {precision_weighted:.4f}")
    print("# Weighted precision reflects how useful and reliable our predictions were")

    # --- F1-score ---
    if precision_weighted + recall_weighted == 0:
        f1_score = 0.0
    else:
        f1_score = 2 * (precision_weighted * recall_weighted) / (precision_weighted + recall_weighted)

    print(f"\n# 📊 Hierarchical F1-score")
    print(f"# F1 = 2 * ({precision_weighted:.4f} * {recall_weighted:.4f}) / ({precision_weighted:.4f} + {recall_weighted:.4f}) = {f1_score:.4f}")
    print("# It's the balance between recall (we covered real terms well) and precision (predictions were useful)")

    return f1_score
