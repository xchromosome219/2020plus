"""
The mutation_types module stratifies counts by mutation types
for amino acids (missense, indel, frame shift, nonsense, and synonymous)
and nucleotides (substitution, insertions, and deletions).
"""

from utils.python.cosmic_db import get_cosmic_db
import utils.python.util as _utils
import plot_data
import pandas as pd
import pandas.io.sql as psql
import logging

logger = logging.getLogger(__name__)  # module logger

def count_amino_acids(conn):
    """Count the amino acid mutation types (missense, indel, etc.).
    """
    df = psql.frame_query("""SELECT * FROM `nucleotide`""", con=conn)
    unique_cts = _utils.count_mutation_types(df['AminoAcid'])
    return unique_cts


def count_nucleotides(conn):
    """Count the nucleotide mutation types (substitution, indels)
    """
    sql = "SELECT Nucleotide FROM `nucleotide`"
    df = psql.frame_query(sql, con=conn)
    unique_cts = _utils.count_mutation_types(df['Nucleotide'], kind='nucleotide')
    return unique_cts


def count_oncogenes(conn):
    logger.info('Counting oncogene mutation types . . .')

    # prepare sql statement
    oncogenes = _utils.oncogene_list
    sql = "SELECT * FROM `nucleotide` WHERE Gene in " + str(oncogenes)
    logger.debug('Oncogene SQL statement: ' + sql)

    df = psql.frame_query(sql, con=conn)  # execute query

    # count mutation types
    aa_counts = _utils.count_mutation_types(df['AminoAcid'])
    nuc_counts = _utils.count_mutation_types(df['Nucleotide'],
                                             kind='nucleotide')
    logger.info('Finished counting oncogene mutation types.')
    return aa_counts, nuc_counts


def count_tsg(conn):
    logger.info('Counting tumor suppressor gene mutation types . . .')

    # prepare sql statement
    tsgs = _utils.tsg_list
    sql = "SELECT * FROM `nucleotide` WHERE Gene in " + str(tsgs)
    logger.debug('Oncogene SQL statement: ' + sql)

    df = psql.frame_query(sql, con=conn)  # execute query

    # count mutation types
    aa_counts = _utils.count_mutation_types(df['AminoAcid'])
    nuc_counts = _utils.count_mutation_types(df['Nucleotide'],
                                             kind='nucleotide')
    logger.info('Finished counting tumor suppressor gene mutation types.')
    return aa_counts, nuc_counts


def count_gene_types(file_path=_utils.result_dir + 'gene_design_matrix.txt'):
    """Returns protein mutation type counts by gene type (oncogenes, tsg, other).

    Kwargs:
        file_path (str): path to mutation type cts by gene file

    Returns:
        pd.DataFrame: mutation type counts by gene type
    """
    df = pd.read_csv(file_path, sep='\t')
    df['gene_type'] = df['gene'].apply(_utils.classify_gene)
    mut_ct_df = df.iloc[:, 1:]  # remove the "gene" column
    mut_ct_df = mut_ct_df.groupby('gene_type').sum()  # get counts for each gene type
    return mut_ct_df


def main():
    conn = get_cosmic_db()  # connect to COSMIC_nuc
    out_dir = _utils.result_dir  # output directory for text files
    plot_dir = _utils.plot_dir  # plotting directory

    # handle DNA nucleotides
    mut_nuc_cts = count_nucleotides(conn)
    mut_nuc_cts.to_csv(out_dir + 'nuc_mut_type_cts.txt', sep='\t')
    tmp_plot_path = plot_dir + 'nuc_mut_types.barplot.png'  # plot path
    plot_data.mutation_types_barplot(mut_nuc_cts,
                                     save_path= tmp_plot_path,
                                     title='DNA Mutations by Type')

    # handle amino acids
    mut_cts = count_amino_acids(conn)  # all mutation cts
    mut_cts.to_csv(out_dir + 'aa_mut_type_cts.txt', sep='\t')
    plot_data.mutation_types_barplot(mut_cts,
                                     title='Protein Mutations by Type')

    # handle oncogene mutation types
    onco_aa_cts, onco_nuc_cts = count_oncogenes(conn)  # oncogene mutation cts
    onco_aa_cts.to_csv(out_dir + 'aa_onco_mut_type_cts.txt', sep='\t')
    onco_nuc_cts.to_csv(out_dir + 'nuc_onco_mut_type_cts.txt', sep='\t')
    plot_data.mutation_types_barplot(onco_aa_cts,
                                     save_path=plot_dir + \
                                     'aa_onco_mut_types.barplot.png',
                                     title='Oncogene Protein Mutations'
                                     ' By Type')
    plot_data.mutation_types_barplot(onco_nuc_cts,
                                     save_path=plot_dir + \
                                     'nuc_onco_mut_types.barplot.png',
                                     title='Oncogene DNA Mutations'
                                     ' By Type')

    # handle tumor suppressor mutation types
    tsg_aa_cts, tsg_nuc_cts = count_tsg(conn)
    tsg_aa_cts.to_csv(out_dir + 'aa_tsg_mut_type_cts.txt', sep='\t')
    tsg_nuc_cts.to_csv(out_dir + 'nuc_tsg_mut_type_cts.txt', sep='\t')
    plot_data.mutation_types_barplot(tsg_aa_cts,
                                     save_path=plot_dir + \
                                     'aa_tsg_mut_types.barplot.png',
                                     title='Tumor Suppressor Protein '
                                     'Mutations By Type')
    plot_data.mutation_types_barplot(tsg_nuc_cts,
                                     save_path=plot_dir + \
                                     'nuc_tsg_mut_types.barplot.png',
                                     title='Tumor Suppressor DNA '
                                     'Mutations By Type')

    # plot protein mutation type counts by gene type
    tmp_mut_df = count_gene_types()
    tmp_mut_df.to_csv(out_dir + 'gene_mutation_counts_by_gene_type.txt',
                      sep='\t')
    plot_data.all_mut_type_barplot(tmp_mut_df)

    conn.close()  # close connection