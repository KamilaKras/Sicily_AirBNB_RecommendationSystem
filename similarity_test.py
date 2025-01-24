from pandas import DataFrame
import numpy as np
import math

def delete_symbols(sentences_list_initial):
    symbols = [",", ".", ":", ";", "!", "?"]
    sentences_list = []
    for sentence in sentences_list_initial:
        for i in sentence:
            if i in symbols:
                sentence = sentence.replace(i, "")
        sentences_list.append(sentence)
    return sentences_list

def create_terms_list(terms_list_nested):
    terms_list = []
    for row in terms_list_nested:
        terms_list.extend(row)
    return list(set(terms_list))

def split_to_terms(sentences_list_clean):
    terms = []
    for sentence in sentences_list_clean:
        term = sentence.split()
        terms.append(term)
    return terms

def count_tf_idf(terms_list, sentences_list_clean, N):
    #Liczba wystapien kazdego termu w kazdym zdaniu
    liczba_wystapien = DataFrame(index=terms_list,
                           columns=['Sentence {}'.format(i) for i in range(len(sentences_list_clean))])
    liczba_wystapien = liczba_wystapien.fillna(0)
    for idx, sentence in enumerate(sentences_list_clean):
        for word in sentence.split():  # Split sentence into words
            if word in liczba_wystapien.index:
                liczba_wystapien.loc[word, 'Sentence {}'.format(idx)] += 1
    #maksymalna liczba wystapien slowa w zdaniu
    max_df = liczba_wystapien.max()
    #TF
    tf_df = liczba_wystapien/max_df
    #IDF
    liczba_nt_df = (liczba_wystapien != 0).sum(axis=1)

    idf = DataFrame(index=terms_list, columns=['IDF'], dtype=float)
    idf['IDF'] = np.log10(N / liczba_nt_df)

    #Tf_IDF
    tf_idf_dt = DataFrame(index=terms_list, dtype=float)
    tf_idf_dt = tf_idf_dt.fillna(0)
    for column in tf_df.columns:
        for row in tf_df.index:
            tf_idf_dt.loc[row, 'Sentence {}'.format(column)] = tf_df.loc[row, column] * idf.loc[row, 'IDF']
    tf_idf_dt.sort_index(ascending=True, inplace=True)
    return tf_idf_dt

def count_miara_iloczynu(query_list, tf_idf_dt):
    miara_iloczynu = 0
    for row in tf_idf_dt.index:
        if row in query_list:
            miara_iloczynu += tf_idf_dt.loc[row]
    return round(miara_iloczynu, 2)

def count_miara_dice(query_list, tf_idf_dt):
    licznik = 0
    suma_kw_wag = 0
    for row in tf_idf_dt.index:
        if row in query_list:
            licznik += tf_idf_dt.loc[row]
        suma_kw_wag += tf_idf_dt.loc[row]**2
    mianownik = len(query_list) * suma_kw_wag
    miara_dice = 2 * licznik / mianownik
    return round(miara_dice, 2)

def count_miara_jaccarda(query_list, tf_idf_dt):
    licznik = 0
    suma_kw_wag = 0
    for row in tf_idf_dt.index:
        if row in query_list:
            licznik += tf_idf_dt.loc[row]
        suma_kw_wag += tf_idf_dt.loc[row] ** 2
    mianownik = len(query_list) + suma_kw_wag - licznik
    miara_jaccarda = licznik / mianownik
    return round(miara_jaccarda,2)

def count_miara_cosinus(query_list, tf_idf_dt):
    licznik = 0
    suma_kw_wag = 0
    for row in tf_idf_dt.index:
        if row in query_list:
            licznik += tf_idf_dt.loc[row]
        suma_kw_wag += tf_idf_dt.loc[row]**2
    mianownik = (len(query_list)**(1/2)) * (suma_kw_wag**(1/2))
    miara_cosinus = licznik / mianownik
    return round(miara_cosinus,2)

def main():
    # Test data
    sentences_initial = [
        "City in the western Poland in the Greater Poland region",
        "You can see the Polish city in the western part",
        "Here is the capital and largest city of Poland"
    ]
    query = "western city in poland"
    num_sentences = len(sentences_initial)

    # Convert all text to lowercase
    sentences_initial = [s.lower() for s in sentences_initial]
    query = query.lower()
    query_list = query.split()

    #LISTA ZDAŃ BEZ BIAŁYCH ZNAKÓW, MAŁYMI LITERAMI
    sentences_clean = delete_symbols(sentences_initial)
    #LISTA Z UNIKALNYMI WARTOSCIAMI TERMÓW W FINALNYM FORMACIE
    terms_list = create_terms_list(split_to_terms(sentences_clean))
    #zwraca dataframe z tf_idf
    tf_idf_dt = count_tf_idf(terms_list, sentences_clean, num_sentences)

    print("\nWyniki dla każdego dokumentu:")
    for i in range(num_sentences):
        print(f"\nDokument {i+1}:")
        print(f"Tekst: {sentences_initial[i]}")
        metrics = [
            count_miara_iloczynu(query_list, tf_idf_dt)[i],
            count_miara_dice(query_list, tf_idf_dt)[i],
            count_miara_jaccarda(query_list, tf_idf_dt)[i],
            count_miara_cosinus(query_list, tf_idf_dt)[i]
        ]
        print(f"Product similarity: {metrics[0]}")
        print(f"Dice similarity: {metrics[1]}")
        print(f"Jaccard similarity: {metrics[2]}")
        print(f"Cosine similarity: {metrics[3]}")
        print(f"[{', '.join(map(str, metrics))}]")

if __name__ == "__main__":
    main()
