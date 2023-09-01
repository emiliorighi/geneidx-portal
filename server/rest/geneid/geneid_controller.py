from flask import Response, request, send_from_directory
from flask_restful import Resource
from . import geneid_service
import json

class GeneIdResultsApi(Resource):
    def get(self, filename):
        mime_type = 'text/gff' if 'gff' in filename else None
        return send_from_directory('tmp', filename, conditional=True, mimetype=mime_type)


class GeneIdServerApi(Resource):
    def post(self):
        resp, status = geneid_service.run_geneid(request)
        return Response(json.dumps(resp), mimetype='application/json',status=status)
     