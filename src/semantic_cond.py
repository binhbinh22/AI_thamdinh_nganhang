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
        # query_embedding = model.encode(query, convert_to_tensor=True)
        # Sử dụng ngram_range từ 7 đến 10
        vectorizer = CountVectorizer(ngram_range=(7,10)).fit(text_sentences)
        phrases = vectorizer.get_feature_names_out()


        # Kiểm tra nếu không tìm thấy cụm từ nào
        if len(phrases) == 0:
            return None

        phrase_embeddings = model.encode(phrases, convert_to_tensor=True).to("cuda")
        # phrase_embeddings = model.encode(phrases, convert_to_tensor=True)
        phrase_scores = util.pytorch_cos_sim(query_embedding, phrase_embeddings)

        max_phrase_idx = phrase_scores.argmax()
        most_similar_phrase = phrases[max_phrase_idx.cpu().item()]

        if phrase_scores.max().cpu().item() > 0.717:
            return most_similar_phrase
        
        return None

    except Exception as e:
        logger.error(f"An error occurred in DK32: {e}")
        return None
    
def DK120(row):
    row['CT120'] = None
    text1 = str(row.get('PTK1', ''))
    text2 = str(row.get('PTK2', ''))


#     text1 = str(row['PTK1']) 
#     text2 = str(row['PTK2'])
    
    if 0 < len(text1.split()) < 50:
        text1=''
    if 0 < len(text2.split()) < 50:
        text2 = ''
    text = text1 + '\n' +text2
    ptk = text
    query = 'thu mua thuỷ hải sản tôm'
    most_similar_phrase = similarity_phrase_hs(ptk,query, model)
    if similarity_phrase_hs(ptk,query, model):
        row['CT120'] = most_similar_phrase
        row['DK120'] = 'False' 
        return '''-Chưa thỏa mãn điều kiện 120 Lĩnh vực thu mua hải
        sản: Khách hàng sẽ phải ứng trước khoản tiền cho bên bán cho các ghe thuyền => Có thể ghi nhận vào khoản phải thu để căn cứ tính hạn mức'''
    row['DK120'] = 'Pass'
    return None    


# ===================DANG KY KINH DOANH===============================
 
def similarity_phrase_dDKd(text, query, model):
    text_sentences = text.split("\n")
    query_embedding = model.encode(query, convert_to_tensor=True).to("cuda")
    # query_embedding = model.encode(query, convert_to_tensor=True)
    # Sử dụng ngram_range từ 5 đến 10
    try:
        vectorizer = CountVectorizer(ngram_range=(7,10)).fit(text_sentences)
        phrases = vectorizer.get_feature_names_out()

 
    # Kiểm tra nếu không tìm thấy cụm từ nào
        if len(phrases) == 0:
            return None
    except Exception as e:
        logger.error(f"An error occurred in DK33: {e}")
        return None
 
    phrase_embeddings = model.encode(phrases, convert_to_tensor=True).to("cuda")
    # phrase_embeddings = model.encode(phrases, convert_to_tensor=True)
    phrase_scores = util.pytorch_cos_sim(query_embedding, phrase_embeddings)
   
    max_phrase_idx = phrase_scores.argmax()
    most_similar_phrase = phrases[max_phrase_idx.cpu().item()]
    if phrase_scores.max().cpu().item()>0.83:
        return   most_similar_phrase
    return None
 
def DK121(row):
    try:
        row['CT121']= None
        # Lấy dữ liệu từ các trường Phương án vay vốn_Phân tích khác và Phương án vay vốn_Phân tích khác
        text1 = str(row.get('PTK1', ''))
        text2 = str(row.get('PTK2', ''))


    #     text1 = str(row['PTK1']) 
    #     text2 = str(row['PTK2'])

        if 0 < len(text1.split()) < 50:
            text1=''
        if 0 < len(text2.split()) < 50:
            text2 = ''
        text = text1 + '\n' +text2
        ptk = text
        query = 'trùng địa chỉ kinh doanh'
        # Kiểm tra điều kiện 'cùng địa chỉ'
        if re.search(r'cùng địa chỉ', ptk, re.IGNORECASE):
            row['CT121'] = 'cùng địa chỉ kinh doanh'
            row['DK121'] = 'False'
            return '''-Chưa thỏa mãn điều kiện 121 ĐVKD làm rõ nguyên nhân: vì sao địa điểm KD trùng với cá nhân/hộ gia đình/tổ chức khác. KH và cá nhân/hộ gia đình/tổ chức khác có mối quan hệ như thế nào?
            CIC của bên có liên quan. Đánh giá có mượn kho/cơ sở kinh doanh hay không ?'''

        # Sử dụng hàm similarity_phrase_dDKd để kiểm tra sự tương đồng
        most_similar_phrase = similarity_phrase_dDKd(ptk, query, model)
        if most_similar_phrase:
            row['CT121'] = most_similar_phrase
            
            address = most_similar_phrase
        # Kiểm tra từ 'không' trong 3 từ trước địa chỉ
            ptk_words = ptk.split()
            address_words = address.split()
            address_start_idx = ' '.join(ptk_words).find(address)

            if address_start_idx != -1:  # Nếu tìm thấy DK33 trong PTK
                # Lấy danh sách 3 từ trước địa chỉ nếu có
                print('có')
                prior_words = ptk_words[max(0, address_start_idx - 3):address_start_idx]
                print(prior_words)
                # Kiểm tra từ "không" trong các từ trước
                if 'không' in prior_words:
                    print('okeoke')
                    row['CT121'] = None
                    row['DK121'] = 'Pass'
                    return None
            if re.search(r'liền', most_similar_phrase, re.IGNORECASE) or re.search(r'lai', most_similar_phrase, re.IGNORECASE):
                row['CT121'] = None
                row['DK121'] = 'Pass'
                return None
            return '''-Chưa thỏa mãn điều kiện 121 ĐVKD làm rõ nguyên nhân: vì sao địa điểm KD trùng với cá nhân/hộ gia đình/tổ chức khác. KH và cá nhân/hộ gia đình/tổ chức khác có mối quan hệ như thế nào?
            CIC của bên có liên quan. Đánh giá có mượn kho/cơ sở kinh doanh hay không ?'''
        
        # Nếu không thỏa mãn điều kiện nào, gán giá trị None
        row['DK121'] = 'Pass'
        return None
    except Exception as e:
        # Ghi log lỗi nếu có sự cố
        logger.error(f"An error occurred in DK33: {e}")
        row['DK121'] = 'Pass'
        return None
 