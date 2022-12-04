
from Levenshtein import distance as l_dist
import argparse

from google.cloud import bigquery




class PlasticSearch:
    def __init__(self, table_ref: str):

        # Construct a BigQuery client object.
        client = bigquery.Client()

        query = """
                SELECT * FROM `{}` WHERE _PARTITIONDATE = "2022-06-18"
                """.format(table_ref)


        query_job = client.query(query)  # Make an API request.
    



        print("The query data:")
        for row in query_job:
            # Row values can be accessed by field name or index.
            print("name={}, steps={}, ingredients_clean={}".format(row["name"], row["steps"], row["ingredients_clean"]))

        


def compare(s1: str, s2: str):
    return l_dist(s1, s2)










if __name__ == "__main__":
    
    plast = PlasticSearch("plenary-line-305512.flaska_data.recipes_raw")
    

    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-f','--foo', help='Description for foo argument', required=True)
    parser.add_argument('-b','--bar', help='Description for bar argument', required=True)
    args = vars(parser.parse_args())
    print(args["foo"])
    print(args)

    


