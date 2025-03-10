from argparse import ArgumentParser
import os
from index_utils import convert_pdf   

def cli(params): 
    file_path = params.path

    for filename in os.listdir(file_path):
        convert_pdf.delay(filename)
        print(f"File {filename} was indexed")

if __name__== "__main__":

    args = ArgumentParser('CV indexing')
    
    args.add_argument('--path', help='path of CV folder', default='cd ')

    params = args.parse_args()

    cli(params)
