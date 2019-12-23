import pandas as pd
from parsing_classes import Parsing_HH, Parsing_SJ

def run(text, input_pages):

    hh = Parsing_HH()
    sj = Parsing_SJ()

    df_hh = hh.search(text, input_pages)
    df_sj = sj.search(text, input_pages)

    df_vacancy = pd.concat([df_hh, df_sj], axis=0).reset_index(drop=True)

    return df_vacancy