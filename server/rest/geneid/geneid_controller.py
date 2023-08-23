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


class GeneIdServerApi(Resource):

    def post(self):
        try:
            # app.logger.info(request)
            # app.logger.info(request.__dict__)

            tmp_uid = f'{datetime.now().isoformat()}_{request.remote_addr}'

            #validate mandatory fields

            #save files

            #parse params

            #exec geneid

            #parse output
            # app.logger.info(request.form)
            # app.logger.info(request.files)

            data = request.form
            files = request.files
            fasta_path = f'{TMP_STORAGE}/{tmp_uid}.fa'
            gff_path = f'{TMP_STORAGE}/{tmp_uid}.gff'
            fasta = files['fastaInput']
            fasta.save(fasta_path)
            # with open(f'/tmp/{tmp_uid}.fa', 'wb') as f:
            #     f.write(fasta.read())
            # app.logger.info(fasta.__dict__)

            output = check_output([GENEID, f'-P {PARAM_FILES_URL}/{DEFAULT_PARAM_FILE}' ,fasta_path])

            # app.logger.info(output)
            # geneid_result = service.programs_configs(data,files)
            # if geneid_result:
            #     #create stat object
            #     if geneid_result.ps:
            #         gff2ps=True
            #     else:
            #         gff2ps=False
            #     # stats = GeneIdStats(ip=request.remote_addr,run_time=geneid_result.geneid_cmd,gff2ps=gff2ps)
            #     # app.logger.info(geneid_result.to_json())
            # # list_response = []
            # # for file in output_files:
            # #     list_response.append(file.name) ## we pass the path of the files to the client (an interval scheduler will remove them)
            #     return Response(geneid_result.to_json(), mimetype="application/json", status=200)
            # else:
            #     return 'something passed..', 500
        except Exception as e:
            app.logger.error(e)
        raise InternalServerError
