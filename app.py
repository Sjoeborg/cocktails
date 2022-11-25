import concurrent.futures

import flask

from google.cloud import bigquery


app = flask.Flask(__name__)
bigquery_client = bigquery.Client()
import logging
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def main():
    return flask.render_template("home.html")


@app.route("/results")
def results():

    ingredient_query = flask.request.args.get("ingredient")
    query = """
           WITH dat AS (SELECT name, steps, SPLIT(ingredients_clean, "|") as ingredients FROM `plenary-line-305512.flaska_data.recipes_raw` WHERE DATE(_PARTITIONTIME) = "2022-06-18" )

        SELECT name, ingredients FROM dat, UNNEST(ingredients) ingredient  WHERE CONTAINS_SUBSTR(ingredient, @ingredient)  LIMIT 20
        """


    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ingredient", "STRING", ingredient_query),
        ]
    )
    query_job = bigquery_client.query(query, job_config=job_config)


    # Make an API request.

    try:
        # Set a timeout because queries could take longer than one minute.
        results = query_job.result(timeout=30)
        results_rows = [row for row in results]

        print("\nresults:{}".format(results_rows))
    except concurrent.futures.TimeoutError:
        return flask.render_template("timeout.html", job_id=query_job.job_id)

    return flask.render_template("query_result.html", results=results_rows)


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="127.0.0.1", port=8000, debug=True)
# [END gae_python3_bigquery]
# [END gae_python38_bigquery]