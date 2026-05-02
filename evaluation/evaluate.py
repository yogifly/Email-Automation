import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score as bert_score
import Levenshtein

nltk.download('punkt')

# =========================
# INPUT TEXTS
# =========================

reference = "Team Lead , Thankyou for letting us know about the important client meeting,We understant the importance of the meeting and will make sure everyone involved attends without fail. Regards"

chatgpt_response = "Hello Team,Thank you for sharing the details regarding the new client requirements. I appreciate the update and the initiative to organize a discussion to better understand the scope and expectations. It will be helpful to go through the requirements collaboratively so that we can align on the deliverables, timelines, and any technical considerations involved.I would like to confirm that I am available for the meeting scheduled on 30th May. Kindly share the exact meeting time, agenda, and any supporting documents or requirement briefs in advance so that I can review them beforehand and contribute more effectively during the discussion.Additionally, if there are any specific points or areas that you would like me to focus on or prepare for, please let me know. This will help ensure that the meeting is productive and that we are able to address all key aspects of the client requirements efficiently.Looking forward to the meeting and to working together on this.Regards"

your_model_response = "Team Lead Jay,Thank you for informing us about the upcoming important client meeting scheduled for Thursday, 30th May. We understand how critical it is and will make sure everyone involved attends without fail. Your leadership continues to guide our efforts effectively.Kind Regards"

# =========================
# BLEU SCORE
# =========================
def compute_bleu(ref, pred):
    ref_tokens = [nltk.word_tokenize(ref.lower())]
    pred_tokens = nltk.word_tokenize(pred.lower())
    smoothie = SmoothingFunction().method4
    return sentence_bleu(ref_tokens, pred_tokens, smoothing_function=smoothie)

# =========================
# ROUGE SCORE
# =========================
def compute_rouge(ref, pred):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = scorer.score(ref, pred)
    return scores

# =========================
# BERT SCORE
# =========================
def compute_bert(ref, pred):
    P, R, F1 = bert_score([pred], [ref], lang="en", verbose=False)
    return float(P.mean()), float(R.mean()), float(F1.mean())

# =========================
# NORMALIZED EDIT DISTANCE
# =========================
def compute_ned(ref, pred):
    dist = Levenshtein.distance(ref, pred)
    max_len = max(len(ref), len(pred))
    return 1 - (dist / max_len)

# =========================
# EVALUATION FUNCTION
# =========================
def evaluate_model(name, ref, pred):
    print(f"\n===== {name} =====")

    bleu = compute_bleu(ref, pred)
    rouge = compute_rouge(ref, pred)
    bert_p, bert_r, bert_f1 = compute_bert(ref, pred)
    ned = compute_ned(ref, pred)

    print(f"BLEU Score: {bleu:.4f}")
    print(f"ROUGE-1: {rouge['rouge1'].fmeasure:.4f}")
    print(f"ROUGE-L: {rouge['rougeL'].fmeasure:.4f}")
    print(f"BERTScore (F1): {bert_f1:.4f}")
    print(f"Normalized Edit Distance (NED): {ned:.4f}")

# =========================
# RUN COMPARISON
# =========================
evaluate_model("ChatGPT Response", reference, chatgpt_response)
evaluate_model("Your Model Response", reference, your_model_response)