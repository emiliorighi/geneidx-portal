from flask import Response, request
from flask import current_app as app
from flask_restful import Resource
from . import geneid_service
from errors import InternalServerError
from subprocess import check_output
from datetime import datetime
import requests
import os

GENEID = '/soft/GeneID/bin/geneid'
TMP_STORAGE = '/server/tmp'
PARAM_FILES_URL = 'https://raw.githubusercontent.com/guigolab/geneid-parameter-files/main/parameter_files'
DEFAULT_PARAM_FILE = 'Homo_sapiens.9606.param'
GENEID_ARGS = ['strand','output']

class GeneIdServerApi(Resource):

    """
    TODO:
        1) execute geneid
        2) convert fasta to 2bit, tabindex gff
        3) store for 24h gff and 2bit results to visualize in jbrowse2
        4) create form to block more than 100 requests per IP
    
    """
    
    def post(self):
        try:
            data = request.form
            files = request.files
            geneid_exec_args = [GENEID]

            #parse params
            if 'paramFile' in data.keys():
                param_filename = data['paramFile']
            else:
                param_filename = DEFAULT_PARAM_FILE
            param_filepath = f'{TMP_STORAGE}/{param_filename}'
            ##check if paramfile is already present 
            if not os.path.isfile(param_filepath):
                param_file_to_store = requests.get(f'{PARAM_FILES_URL}/{param_filename}').content
                with open(param_filepath, 'wb') as p:
                    p.write(param_file_to_store)

            geneid_exec_args.extend(['-P', param_filepath])

            tmp_uid = f'{datetime.now().isoformat()}_{request.remote_addr}'
            if not 'fastaInput' in files.keys():
                return 
            fasta_input = files['fastaInput']
            fasta_path = f'{TMP_STORAGE}/{tmp_uid}.fa'
            fasta_input.save(fasta_path)

            geneid_exec_args.append(fasta_path)
            #validate mandatory fields
                #fasta 
            for key in data.keys():
                if key in GENEID_ARGS and data[key]:
                    geneid_exec_args.append(data[key])

            if 'options' in data.keys():
                geneid_exec_args.extend(data['options'].split(','))
            gff_path = f'{TMP_STORAGE}/{tmp_uid}.gff'
            
            if 'gffInput' in files.keys():
                gff_input = files['gffInput']
                gff_path = f'{TMP_STORAGE}/{tmp_uid}.gff'
                gff_input.save(gff_path)
                if 'mode' in data.keys() and data['mode'] == '-O':
                    mode = data['mode']
                else:
                    mode = '-R'
                geneid_exec_args.extend([mode, gff_path])
                
            if 'mode' in data.keys() and data['mode'] == '-o':
                geneid_exec_args.append(data['mode'])

            output = check_output(geneid_exec_args)
            
            os.remove(fasta_path)
            if os.path.isfile(gff_path):
                os.remove(gff_path)

        except Exception as e:
            app.logger.error(e)
        raise InternalServerError
