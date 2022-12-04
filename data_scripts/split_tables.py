import re
import unicodedata
from typing import Literal

import numpy as np
import pandas as pd

keys = ['recipe', 'alcohol', 'ingredient']

def explode_fields(df: pd.DataFrame) -> pd.DataFrame:
    df.alcohol = df.alcohol.apply(lambda x: x.split('|'))
    exploded_df = df.explode('alcohol').explode('ingredient')
    for key in keys:
        exploded_df[f'{key}_id'] = exploded_df[key].apply(make_id)
    return exploded_df


def aggregate_unique_ids(df: pd.DataFrame, primary_key: Literal['recipe', 'alcohol', 'ingredient']) -> pd.DataFrame:
    foreign_keys = set(keys).difference(set(primary_key))
    cocktail_df_raw = df[df.columns.intersection(keys) & df.columns.intersection([f'{k}_id' for k in keys])].drop_duplicates(subset=['alcohol_id', 'ingredient_id'])
    cocktail_df_grouped = cocktail_df_raw.groupby(f'{primary_key}_id').agg(list)
    for fk in foreign_keys:
        cocktail_df_grouped[f'{fk}_id'] = (cocktail_df_grouped[f'{fk}_id'].apply(remove_duplicate_ids)
                                                          .apply(lambda x: '|'.join(x)))
    return cocktail_df_grouped


def make_id(string: str) -> str:
    string = string.replace(' ', '_')
    only_ascii_string = (unicodedata.normalize('NFKD', string)
                                    .encode('ASCII', 'ignore')
                                    .decode('utf-8'))
    text = re.sub('[^0-9a-zA-Z_-]', '', only_ascii_string)
    return text.casefold()

def remove_duplicate_ids(ids: list[str]) -> list[str]:
    return pd.Series(ids).drop_duplicates().to_list()


def export(df: pd.DataFrame, filename: str) -> None:
    df.to_parquet(f'./data_scripts/data/out/{filename}.parquet')


def read_df(filename: str) -> pd.DataFrame:
    df = pd.read_parquet(f'./data_scripts/data/processed/{filename}.parquet')
    df.rename({'name': 'recipe'}, axis=1, inplace=True)
    df = df.drop(['garnish',
                  'serving_suggestion',
                  'ingredients',
                  'steps',
                  'review_count',
                  'url',
                  'website',
                  'image_url',
                  'serving_suggestion_clean'], axis=1)
    
    df.ingredients_clean = df.ingredients_clean.apply(eval)
    df.rename({'ingredients_clean': 'ingredient'}, axis=1, inplace=True)
    return df


if __name__ == '__main__':
    filename = 'difford_1_5000_processed'
    raw_df = read_df(filename)
    exploded_df = explode_fields(df=raw_df)
    recipe_df = aggregate_unique_ids(df=exploded_df, primary_key='recipe')
    alcohol_df = aggregate_unique_ids(df=exploded_df, primary_key='alcohol')
    ingredients_df = aggregate_unique_ids(df=exploded_df, primary_key='ingredient')
    export(recipe_df, 'recipe_table')
    export(alcohol_df, 'alcohol_table')
    export(ingredient_df, 'ingredient_table')