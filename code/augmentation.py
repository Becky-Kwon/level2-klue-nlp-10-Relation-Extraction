#%%
import pandas as pd
import numpy as np
from googletrans import Translator
from tqdm.auto import tqdm
import time
import ast

#%%
train_path = '../dataset/train/train.csv'
train_df = pd.read_csv(train_path)
train_df_len = len(train_df)


trans_train_path = '../dataset/train/trans_train.csv'
trans_train = pd.read_csv(trans_train_path)

#%%
# back translation
translator = Translator()

def google_ko2en2ko(ko_text, translator):
    ko_en_result = translator.translate(ko_text, dest = 'en').text
    en_ko_result = translator.translate(ko_en_result, dest = 'ko').text
    return en_ko_result


sen1_list = train_df['sentence'] 

for idx, sentence in enumerate(tqdm(sen1_list)):
     while True:
        try:
            result = google_ko2en2ko(sentence, translator)
            train_df.loc[idx, 'sentence'] = result
            break  
        except Exception as e:
            print(f"번 째 index에서 에러 발생 {idx} {e}")
            time.sleep(1)  # 1초의 지연 후 다시 시도

train_df.to_csv('./dataset/train/trans_train.csv', index=False)



# test_text = "나는지금코드를보고있는중이다."
# print(google_ko2en2ko(test_text, translator))

# for idx, sentence in enumerate(tqdm(sen1_list)):
#     result =  google_ko2en2ko(sentence, translator)
#     test.loc[idx,'sentence_1'] = result

# for idx, sentence in enumerate(tqdm(sen2_list)):
#     result =  google_ko2en2ko(sentence, translator)
#     test.loc[idx,'sentence_2'] = result

#%%

def filter_row(row):
    return row['subject_entity']['word'] in row['sentence'] and row['object_entity']['word'] in row['sentence']

print('원래 길이', len(trans_train))

# sentence에 subject entity와 object entity가 있는지
trans_train['subject_entity'] = trans_train['subject_entity'].apply(ast.literal_eval)
trans_train['object_entity'] = trans_train['object_entity'].apply(ast.literal_eval)
trans_train = trans_train[trans_train.apply(filter_row, axis=1)]
print('sentence에 entity들 있는 거만 남기면', len(trans_train))

smooth_trans = trans_train[(trans_train['label'] != "no_relation") & (trans_train['label'] != "org:top_members/employees") & (trans_train['label'] != "per:employee_of")]
print('smoothing 후 길이', len(smooth_trans))

print('2 len', smooth_trans)
smooth_trans['id'] = range(1, len(smooth_trans)+1)
smooth_trans.reset_index(drop=True, inplace=True)
#smooth_trans.to_csv('../dataset/train/smooth_trans.csv', index=False)

# %%

trans_train_path = '../dataset/train/smooth_trans.csv'
trans_train = pd.read_csv(trans_train_path)

augmented_df = pd.merge(train_df, smooth_trans, how='outer')
augmented_df['id'] = range(1, len(augmented_df)+1)
augmented_df.reset_index(drop=True, inplace=True)
augmented_df.to_csv('../dataset/train/augmented_train.csv', index=False)
# %%
