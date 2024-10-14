import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import config
model = SentenceTransformer(config.model_emb)
from log import *
#=======================THU MUA HAI SAN===============================
 
def similarity_phrase_hs(text, query, model):
    try:
        text_sentences = text.split("\n")
        query_embedding = model.encode(query, convert_to_tensor=True).to("cuda")
 
        # Sử dụng ngram_range từ 7 đến 10
        vectorizer = CountVectorizer(ngram_range=(7,10)).fit(text_sentences)
        phrases = vectorizer.get_feature_names()
 
        # Kiểm tra nếu không tìm thấy cụm từ nào
        if len(phrases) == 0:
            return None
 
        phrase_embeddings = model.encode(phrases, convert_to_tensor=True).to("cuda")
        phrase_scores = util.pytorch_cos_sim(query_embedding, phrase_embeddings)
 
        max_phrase_idx = phrase_scores.argmax()
        most_similar_phrase = phrases[max_phrase_idx.cpu().item()]
 
        if phrase_scores.max().cpu().item() > 0.717:
            return most_similar_phrase
        return None
 
    except Exception as e:
        logger.error(f"An error occurred in dk32: {e}")
        return None
def dk32(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])
    ptk = ptk1 + ptk2
    query = 'thu mua thuỷ hải sản tôm'
    most_similar_phrase = similarity_phrase_hs(ptk,query, model)
    if similarity_phrase_hs(ptk,query, model):
        row['dk32'] = most_similar_phrase
        return '''- Chưa thỏa mãn điều kiện 32:\n -> Giải pháp là: Lĩnh vực thu mua hải
        sản: Khách hàng sẽ phải ứng trước khoản tiền cho bên bán cho các ghe thuyền => Có thể ghi nhận vào khoản phải thu để căn cứ tính hạn mức'''
    row['dk32'] = None
    return None    
 

