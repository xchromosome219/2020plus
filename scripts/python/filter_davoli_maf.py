#!/usr/bin/env python
"""
Uses the CRAVAT Variant file from SNVGet to filter out lines
in the davoli MAF file that had mappability warnings.
"""
import pandas as pd
import argparse


def fix_tumor_type(ttype):
    ttype_dict = {'Ovarian Carcinoma': 'Ovarian',
                  'Ovarian Adenocarcinoma': 'Ovarian',
                  'Colorectal Adenocarcinoma': 'Colorectal',
                  'Glioblastoma': 'Glioblastoma Multiforme',
                  'Thyroic Carcinoma' : 'Thyroid Carcinoma',
                  'Endometerial Carcinoma ': 'Endometrial Carcinoma',
                  'Uterin Carcinoma': 'Endometrial Carcinoma',
                  'Bladder Carcinoma': 'Bladder Urothelial Carcinoma',
                  'Skin Melanoma': 'Melanoma'}
    if ttype_dict.has_key(ttype):
        return ttype_dict[ttype]
    else:
        return ttype


def fix_tumor_sample(tsample):
    if 'tumor' in tsample.lower():
        return tsample.strip('-Tumor')
    else:
        return tsample


def parse_arguments():
    parser = argparse.ArgumentParser()
    help_str = 'Cravat output (optional), filters on mappability'
    parser.add_argument('-c', '--cravat',
                        type=str, default=None,
                        help=help_str)
    help_str = 'Path to MAF file from davoli2maf.py script'
    parser.add_argument('-m', '--maf',
                        type=str, required=True,
                        help=help_str)
    help_str = 'Output MAF path after filtering using CRAVAT txt file'
    parser.add_argument('-o', '--output',
                        type=str, required=True,
                        help=help_str)
    args = parser.parse_args()
    return vars(args)


def main(opts):
    davoli_df = pd.read_csv(opts['maf'], sep='\t')

    # filter list based on mappability warning from cravat
    if opts['cravat']:
        cravat_df = pd.read_csv(opts['cravat'], sep='\t')
        prev_len = len(davoli_df)
        passed_qc = cravat_df[cravat_df['Mappability Warning'].isnull()]['ID']
        davoli_df = davoli_df.ix[passed_qc]
        after_len = len(davoli_df)
        print('Before mappability filtering: {0} lines'.format(prev_len))
        print('After mappability filtering: {0} lines'.format(after_len))
        print('Line difference: {0}'.format(prev_len-after_len))

    # fix tumor names
    davoli_df['Tumor_Type'] = davoli_df['Tumor_Type'].apply(fix_tumor_type)
    davoli_df['Tumor_Sample'] = davoli_df['Tumor_Sample'].apply(fix_tumor_sample)

    # save filtered file
    davoli_df.to_csv(opts['output'], sep='\t', index=False)


if __name__ == "__main__":
    opts = parse_arguments()
    main(opts)
