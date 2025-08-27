# McCells

Modeling of the CZI Cell Census to hierarchically classify cell types. Brief explanation of each program in this repo. There are more details in each file.  


```download_cell_census```: downloads an AnnData object from the Cell Census with cell and gene metadata filtering

```external_model_test ```: Loads hand-annotated data and a trained model to evaluate the model on an unseen dataset. 

``` gene_filtering```: loads a list of genes from BioMart and filters that list

``` ontology visualization```: different visualizations of the Cell Ontology

``` ontology_search```: multiple functions to explore and characterize the Cell Ontology

``` query_cell_census```: multiple functions to explore and extract data from the Cell Census

``` structure_cellcensus_query```: creates a file with a list of cell type terms that are included in the Census that meet a user-defined requirement based on the Cell Ontology


## Modeling
The modeling programs exist in a few different formats. I'm going to leave them all in the repo, but please read the descriptions carefully so you know what is most up to date. I'll list them from oldest to newest. 

``` nn_classifier```: oldest. wouldn't bother looking at. 


```cell_classification```: everything in one file. Starts with a downloaded AnnData object, preprocessing and modeling from that file. 

After developing ```cell_classification``` for a while, I realized it makes more computational sense to have the preprocessing and modeling in different files, so I took ```cell_classification``` and split it in two steps:

``` mccell_preprocessing```: preprocesses AnnData object on the disk and saves files for modeling

``` mccell_model```: loads the results of ``` mccell_preprocessing``` to do the modeling

The final step was getting a local version of the whole Census so that we could stream the data from disk. This enables scaling of the modeling. 

``` mccell_preprocess_from_disk```: same as above, but references a version of the whole Census that is stored locally, for data streaming in the modeling step. 

``` model_from_disk```: loads results of ``` mccell_preprocess_from_disk``` and does the modeling while streaming data from disk to save memory 




