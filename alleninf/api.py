import json
import urllib2
import os
import pandas as pd

api_url = "http://api.brain-map.org/api/v2/data/query.json"

def get_probes_from_genes(gene_names):
    if not isinstance(gene_names,list):
        gene_names = [gene_names]
    #in case there are white spaces in gene names
    gene_names = ["'%s'"%gene_name for gene_name in gene_names]
    
    api_query = "?criteria=model::Probe"
    api_query += ",rma::criteria,[probe_type$eq'DNA']"
    api_query += ",products[abbreviation$eq'HumanMA']"
    api_query += ",gene[acronym$eq%s]"%(','.join(gene_names))
    api_query += ",rma::options[only$eq'probes.id','name']"
    
    data = json.load(urllib2.urlopen(api_url + api_query))
    
    d = {probe['id']: probe['name'] for probe in data['msg']}
    
    if not d:
        raise Exception("Could not find any probes for %s gene. Check " \
        "http://help.brain-map.org/download/attachments/2818165/HBA_ISH_GeneList.pdf?version=1&modificationDate=1348783035873 " \
        "for list of available genes."%gene_name)
    
    return d

def get_expression_values_from_probe_ids(probe_ids):
    if not isinstance(probe_ids,list):
        probe_ids = [probe_ids]
    #in case there are white spaces in gene names
    probe_ids = ["'%s'"%probe_id for probe_id in probe_ids]
    
    api_query = "?criteria=service::human_microarray_expression[probes$in%s]"%(','.join(probe_ids))
    data = json.load(urllib2.urlopen(api_url + api_query))
    
    expression_values = [[float(expression_value) for expression_value in data["msg"]["probes"][i]["expression_level"]] for i in range(len(probe_ids))]
    well_ids = [sample["sample"]["well"] for sample in data["msg"]["samples"]]
    donor_names = [sample["donor"]["name"] for sample in data["msg"]["samples"]]
    well_coordinates = [sample["sample"]["mri"] for sample in data["msg"]["samples"]]
    
    return expression_values, well_ids, well_coordinates, donor_names

def get_mni_coordinates_from_wells(well_ids):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    frame = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)
    
    return list(frame.ix[well_ids].itertuples(index=False))
    
if __name__ == '__main__':
    probes_dict = get_probes_from_genes("SLC6A2")
    expression_values, well_ids, well_coordinates, donor_names = get_expression_values_from_probe_ids(probes_dict.keys())
    print get_mni_coordinates_from_wells(well_ids)
    