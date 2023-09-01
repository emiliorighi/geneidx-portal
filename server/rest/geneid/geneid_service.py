from db.models import GeneIdUser
from subprocess import check_output
from datetime import datetime
import requests, os, time, ipinfo

GENEID = '/soft/GeneID/bin/geneid'
TMP_STORAGE = '/server/tmp'
PARAM_FILES_URL = 'https://raw.githubusercontent.com/guigolab/geneid-parameter-files/main/parameter_files'
DEFAULT_PARAM_FILE = 'Homo_sapiens.9606.param'
GENEID_ARGS = ['strand','output']
IP_ACCESS_TOKEN = '65e933dcf49b1e'

##store geo location of ip for statistical purposes
def store_user_location(ip_address):
    user = GeneIdUser.objects(ip_address=ip_address).first()
    if user:
        user.requests = user.requests + 1
        user.save()
        return
    
    handler = ipinfo.getHandler(IP_ACCESS_TOKEN)
    details = handler.getDetails(ip_address)
    if not details.country:
        return #HERE WE SHOULD RAISE AN ERROR?
    user = GeneIdUser(ip_address=ip_address, country=details.country)
    if details.city:
        user.city = details.city
    user.save()

def get_parameter_file(data):
    if 'paramFile' in data.keys():
        param_filename = data['paramFile']
    else:
        param_filename = DEFAULT_PARAM_FILE
    param_filepath = f'{TMP_STORAGE}/{param_filename}'
    ##check if paramfile is already present 
    if not os.path.isfile(param_filepath):
        response = requests.get(f'{PARAM_FILES_URL}/{param_filename}')
        if response.status_code != 200:
            return 
        with open(param_filepath, 'wb') as p:
            p.write(response.content)
    return param_filepath



"""
1) execute geneid
2) convert fasta to 2bit, tabindex gff
3) store for 24h gff and 2bit results to visualize in jbrowse2
4) create form to block more than 100 requests per IP
"""
def run_geneid(request):
    data = request.form
    files = request.files
    geneid_exec_args = [GENEID]


    param_filepath = get_parameter_file(data)

    if not param_filepath: #param file not found
        message = 'paramFile not found, please check: https://github.com/guigolab/geneid-parameter-files for the list of the available parameter file. Provide a correct param file name (ex: Acyrthosiphon_pisum.7029.param) or leave empty to use the default (Homo_sapiens.9606.param)'
        resp = dict(message=message)
        return resp, 400

    geneid_exec_args.extend(['-P', param_filepath])

    ip_address = request.remote_addr
    tmp_uid = f'{datetime.now().isoformat()}_{ip_address}'

    #fasta
    if not 'fastaInput' in files.keys():
        resp = dict(message='fastaInput field is mandatory')
        return resp, 400
    fasta_input = files['fastaInput']
    fasta_name = f'{tmp_uid}.fa'
    fasta_path = f'{TMP_STORAGE}/{fasta_name}'
    fasta_input.save(fasta_path)

    geneid_exec_args.append(fasta_path)

    #additional args
    for key in data.keys():
        if key in GENEID_ARGS and data[key]:
            geneid_exec_args.append(data[key])

    #gff is the default output
    gff_output = 'output' in data.keys() and data['output'] == '-G' or data['output'] == '-XG'

    if 'options' in data.keys() and data['options']:
        geneid_exec_args.extend(data['options'].split(','))

    #gff
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

    #TODO: use this in prod
    # store_user_location(ip_address)

    #measure execution time
    start = time.time()
    geneid_ouput = check_output(geneid_exec_args)
    end = time.time()

    #index and zip fasta input
    indexed_fasta_name= f'{fasta_name}.fai'
    indexed_fasta_path = f'{TMP_STORAGE}/{indexed_fasta_name}'
    samtools_cmd = ['samtools','faidx', fasta_path, '-o', f'{indexed_fasta_path}']
    check_output(samtools_cmd)


    output_filename = f'{tmp_uid}.geneid'
    output_filepath = f'{TMP_STORAGE}/{output_filename}'
    with open(output_filepath, 'wb') as out:
        out.write(geneid_ouput)

    exec_time = str(round(end-start, 2))

    #make response
    response = {
        'execTime':exec_time,
        'command':" ".join(geneid_exec_args),
        'input':[
            {
                'filename':fasta_name,
                'extension':'fa'
            },
            {
                'extension':'fai',
                'filename':indexed_fasta_name
            }
        ]
    }
    
    if gff_output:
        sorted_gff_name = f'{output_filename}.gff'
        sorted_gff_path = f'{TMP_STORAGE}/{sorted_gff_name}'

        # gt gff3 -sortlines -tidy -retainids yourfile.gff > yourfile.sorted.gff
        # bgzip yourfile.sorted.gff
        # tabix yourfile.sorted.gff.gz
        gt_cmd = ['gt','gff3','-sortlines','-tidy','-retainids','-o', sorted_gff_path, output_filepath]
        check_output(gt_cmd)
        check_output(['bgzip', sorted_gff_path])
        check_output(['tabix', f'{sorted_gff_path}.gz'])

        response['output'] = [
            {
                'extension':'gz',
                'filename':f'{sorted_gff_name}.gz'
            },
            {
                'extensions':'tbi',
                'filename':f'{sorted_gff_name}.gz.tbi'
            }
        ]
    else:
        response['output'] = [
            {
                'extension':'geneid',
                'filename':output_filename
            }
        ]
    return response, 200

