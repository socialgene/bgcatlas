import pandas as pd
from pathlib import Path
import pickle
import multiprocessing
from socialgene.clustermap.serialize import SerializeToClustermap
from socialgene.neo4j.neo4j import GraphDriver # grab the the neo4j connection
from socialgene.config import env_vars
env_vars["NEO4J_URI"] = "bolt://localhost:7687"


def main(pickle_filepath, json_dirpath):
    pickle_filepath = Path(pickle_filepath)
    search_object = pickle.load(open(pickle_filepath, 'rb'))
    json_path = Path(json_dirpath, f"{pickle_filepath.stem}.json")
    df = search_object.link_df
    df = pd.merge(
            search_object._compare_bgcs_by_jaccard_and_levenshtein(),
            search_object._compare_bgcs_by_median_bitscore(),
            left_on="query_gene_cluster",
            right_on="target_gene_cluster",
            how="inner",
        )
    df.sort_values(["modscore","score"], ascending=False, inplace=True)
    df['assembly'] = df['target_gene_cluster_y'].apply(lambda x: x.parent.parent)
    df.drop_duplicates(subset="assembly", keep="first", inplace=True)
    df = df[df['jaccard'] >= 0.4]
    # drop rows in search_object.link_df where search_object.link_df['target_gene_cluster'] is not in df['target_gene_cluster_y']
    search_object.link_df = search_object.link_df[search_object.link_df['target_gene_cluster'].isin(df['target_gene_cluster_y'])]
    search_object.link_df.reset_index(drop=True, inplace=True)
    to_report = [i.parent.parent for i in  df.target_gene_cluster_y.to_list()]
    for assembly in to_report:
        for lk,lv in assembly.loci.items():
            lv.gene_clusters = [i for i in lv.gene_clusters if i in search_object.link_df.target_gene_cluster.to_list()]
    search_object.link_df['assembly_uid'] = search_object.link_df.target_gene_cluster.apply(lambda x: x.parent.parent.uid)
    with GraphDriver() as db:
        for i in db.run(
            """
        MATCH (a1:assembly)
        WHERE a1.uid in $ids 
        RETURN a1.uid as assembly_uid, a1.organism as organism
        """, ids=list(search_object.link_df.assembly_uid.unique()
    )
        ).values():
            search_object.sg_object.assemblies[i[0]].name = f'{i[0]}; {i[1]}'
    with GraphDriver() as db:
        for i in db.run(
            """
        MATCH (a1:assembly)-[:FOUND_IN]->(cc:culture_collection)
        WHERE a1.uid in $ids 
        RETURN a1.uid as assembly_uid, cc.uid as culture_collection_uid
        """, ids=list(search_object.link_df.assembly_uid.unique()
    )
        ).values():
            search_object.sg_object.assemblies[i[0]].name = f"{search_object.sg_object.assemblies[i[0]].name}; {i[1]}"
    assemblies = [search_object.input_assembly] + to_report
    zz = SerializeToClustermap(
        sg_object=search_object.sg_object,
        sorted_bgcs=assemblies[:100],
        link_df=search_object.link_df,
        group_df=search_object.group_df,
    )
    zz.write(json_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle_dir", help="Path to pickle file", default="clustermap/pickles", type=str, required=False)
    parser.add_argument("--json_dirpath", help="Path to directory where json file will be saved", default="clustermap/jsons", type=str, required=False)
    parser.add_argument("--cpus", help="Number of processes to use", default=1, type=int, required=False)
    args = parser.parse_args()
    pickles_paths = list(Path(args.pickle_dir).glob("*.pickle"))
    pickles_paths=[i for i in pickles_paths if not Path(args.json_dirpath, f"{i.stem}.json").exists()]            
    print(f"Number of pickles to process: {len(pickles_paths)}")
    with multiprocessing.Pool(args.cpus) as p:
        p.starmap(main, [(pickle_path, args.json_dirpath) for pickle_path in pickles_paths])

