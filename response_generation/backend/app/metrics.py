from rapidfuzz.distance import Levenshtein
import textstat

def compute_metrics(draft, final):
    edit_distance = Levenshtein.distance(draft.split(), final.split())
    normalized_edit = edit_distance / max(len(draft.split()), 1)

    zero_edit = int(draft.strip() == final.strip())

    fk_grade = textstat.flesch_kincaid_grade(final)
    readability_ok = 6 <= fk_grade <= 9

    return {
        "edit_distance": edit_distance,
        "normalized_edit_distance": normalized_edit,
        "zero_edit": zero_edit,
        "fk_grade": fk_grade,
        "readability_ok": readability_ok
    }
