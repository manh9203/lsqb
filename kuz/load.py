import kuzu
from os import listdir
from os.path import isfile, join
import logging
import shutil
import sys

def load_schema(conn):
    schema_file = open('kuz/schema.cypher').read().split(';')

    for schema in schema_file:
        print(schema)
        print()

        if schema == "":
            continue
        logging.info(f"Loading schema {schema}")
        conn.execute(f"{schema}")

    logging.info("Loaded schema")

def load_lsqb_dataset(conn, sf):
    data_path = f'data/social-network-sf{sf}-projected-fk'

    lsqb_node_files = ["Company", "University", "Continent", "Country", "City", "Tag", "TagClass", "Forum", "Comment", "Post", "Person"]
    lsqb_edge_files = ["City_isPartOf_Country", "Comment_hasCreator_Person", "Comment_hasTag_Tag", "Comment_isLocatedIn_Country", "Comment_replyOf_Comment", "Comment_replyOf_Post", "Company_isLocatedIn_Country", "Country_isPartOf_Continent", "Forum_containerOf_Post", "Forum_hasMember_Person", "Forum_hasModerator_Person", "Forum_hasTag_Tag", "Person_hasInterest_Tag", "Person_isLocatedIn_City", "Person_knows_Person_bidirectional", "Person_likes_Comment", "Person_likes_Post", "Person_studyAt_University", "Person_workAt_Company", "Post_hasCreator_Person", "Post_hasTag_Tag", "Post_isLocatedIn_Country", "TagClass_isSubclassOf_TagClass", "Tag_hasType_TagClass", "University_isLocatedIn_City"]

    load_schema(conn)

    extension = ".csv"
    copy_options = "(HEADER=True, DELIM='|')"

    for lsqb_file in lsqb_node_files:
        logging.debug(f"Loading {lsqb_file}")
        conn.execute(f"""COPY {lsqb_file} from '{data_path}/{lsqb_file}{extension}' {copy_options}""")

    for lsqb_file in lsqb_edge_files:
        logging.debug(f"Loading {lsqb_file}")
        if "Person_knows_Person_bidirectional" in lsqb_file:
            conn.execute(f"""COPY Person_knows_Person from '{data_path}/{lsqb_file}{extension}' {copy_options}""")
        else:
            conn.execute(f"""COPY {lsqb_file} from '{data_path}/{lsqb_file}{extension}' {copy_options}""")
    logging.info("Loaded data files")


def main():
    if len(sys.argv) < 1:
        print("Usage: client.py sf")
        print("Where sf is the scale factor)")
        exit(1)
    else:
        sf = sys.argv[1]

    database_file_location = 'kuz/scratch/lsqb-database'
    shutil.rmtree(database_file_location, ignore_errors=True)

    db = kuzu.Database('kuz/scratch/lsqb-database')

    conn = kuzu.Connection(db)


    logging.info("Successfully connected")

    load_lsqb_dataset(conn, sf)


if __name__ == "__main__":
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', level=logging.DEBUG)
    main()