Interactive version of the atlas is available at:

https://bgcatlas.pages.dev



## Search Parameters

SocialGene search parameters used:

```python
search_bgc(
    input=gbk_path,
    hmm_dir=hmm_dir,
    outpath_clinker=outpath_clinker,
    use_neo4j_precalc=True,
    assemblies_must_have_x_matches=0.4,
    nucleotide_sequences_must_have_x_matches=0.4,
    gene_clusters_must_have_x_matches=0.4,
    break_bgc_on_gap_of=10000,
    target_bgc_padding=10000,
    max_domains_per_protein=3,
    max_outdegree=300000,
    max_query_proteins=10,
    scatter=True,
    locus_tag_bypass_list=None,
    protein_id_bypass_list=None,
    only_culture_collection=True,
    frac=0.75,
    run_async=True,
    analyze_with="blastp",
    blast_speed='ultra-sensitive',
)
```

Plots with multiple contigs do not display well in clustermap without modifying locus coordinates. The `./only_display_best_hit_per_assembly.py` script was used to reprocess the search results to create clustermap plots where only the best single search result per assembly is shown. The script also limits the total number of genomes to 100 or less for performance reasons.
