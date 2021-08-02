# Git fork from https://gist.github.com/avidale/dc95794227d7e53985b441ec722c4d0e

from transformers import AutoModel, AutoTokenizer
from transformers import AutoModelForCausalLM
import torch
import torch.nn.functional
from tqdm.auto import tqdm
from nltk.translate.bleu_score import sentence_bleu
import pandas as pd
import numpy as np


labse_name = 'cointegrated/LaBSE-en-ru'
labse_model = AutoModel.from_pretrained(labse_name)
labse_tokenizer = AutoTokenizer.from_pretrained(labse_name)
if torch.cuda.is_available():
    labse_model.cuda()

mname = 'sberbank-ai/rugpt3small_based_on_gpt2'
gpt_tokenizer = AutoTokenizer.from_pretrained(mname)
gpt_model = AutoModelForCausalLM.from_pretrained(mname)
if torch.cuda.is_available():
    gpt_model.cuda()


def encode_labse(texts):
    encoded_input = labse_tokenizer(
        texts, padding=True, truncation=True, max_length=64, return_tensors='pt'
    ).to(labse_model.device)
    with torch.no_grad():
        model_output = labse_model(**encoded_input)
    embeddings = model_output.pooler_output
    embeddings = torch.nn.functional.normalize(embeddings)
    return embeddings.cpu().numpy()


def get_sims(df, batch_size=32):
    sims = []
    for i in range(0, df.shape[0], batch_size):
        batch = df.iloc[i: i+batch_size]
        e1 = encode_labse(batch.text1.tolist())
        e2 = encode_labse(batch.text2.tolist())
        sims.extend((e1 * e2).sum(axis=1))
    return np.array(sims)


def get_random_sims(df, batch_size=32, random_state=1):
    df2 = pd.DataFrame({
        'text1': df.text1.tolist(),
        'text2': df.text2.sample(frac=1.0, random_state=random_state).tolist()
    })
    return get_sims(df2, batch_size=batch_size)


def get_bleu(df):
    return np.array([sentence_bleu([row.text1], row.text2) for i, row in df.iterrows()])


def ngrams(word, n=3):
    return [word[i: i+n] for i in range(len(word)-n+1)]


def common_grams(text1, text2):
    g1 = {g for w in text1.lower().split() for n in range(3, 7) for g in ngrams(f' {w} ', n=n)}
    g2 = {g for w in text2.lower().split() for n in range(3, 7) for g in ngrams(f' {w} ', n=n)}
    return len(g1.intersection(g2)) / len(g1.union(g2))


def get_char_ngram_overlap(df):
    return np.array([common_grams(row.text1, row.text2) for i, row in df.iterrows()])


def calc_gpt2_ppl_corpus(test_sentences, aggregate=False, sep='\n'):
    """ Calculate average perplexity per token and number of tokens in each text."""
    lls = []
    weights = []
    for text in tqdm(test_sentences):
        encodings = gpt_tokenizer(f'{sep}{text}{sep}', return_tensors='pt')
        input_ids = encodings.input_ids.to(gpt_model.device)
        target_ids = input_ids.clone()

        w = max(0, len(input_ids[0]) - 1)
        if w > 0:
            with torch.no_grad():
                outputs = gpt_model(input_ids, labels=target_ids)
                log_likelihood = outputs[0]
                ll = log_likelihood.item()
        else:
            ll = 0
        lls.append(ll)
        weights.append(w)
    likelihoods, weights = np.array(lls), np.array(weights)
    if aggregate:
        return sum(likelihoods * weights) / sum(weights)
    return likelihoods, weights


def analyze_pairs(texts1, texts2):
    df = pd.DataFrame({'text1': texts1, 'text2': texts2})
    b1 = get_bleu(df)
    b2 = get_bleu(pd.DataFrame({'text1': texts2, 'text2': texts1}))
    p1, w1 = calc_gpt2_ppl_corpus(df.text1.tolist())
    p2, w2 = calc_gpt2_ppl_corpus(df.text2.tolist())
    return {
        'sim': get_sims(df).mean(),
        'sim_random': get_random_sims(df).mean(),
        'bleu_1': b1.mean(),
        'bleu_2': b2.mean(),
        'bleu': (b1+b2).mean() / 2,
        'char_ngram_overlap': get_char_ngram_overlap(df).mean(),
        'perp_1': (p1 * w1).sum() / w1.sum(),
        'perp_2': (p2 * w2).sum() / w2.sum(),
        'perp_mean': (p1 * w1 + p2 * w2).sum() / (w1 + w1).sum(),
}