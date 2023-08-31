from flask import Response
from db.models import GeneIdUser
from subprocess import check_output
from datetime import datetime
import requests, os, time, ipinfo, json

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
        return Response(json.dumps(resp), mimetype='application/json', status=400)

    geneid_exec_args.extend(['-P', param_filepath])

    ip_address = request.remote_addr
    tmp_uid = f'{datetime.now().isoformat()}_{ip_address}'

    #fasta
    if not 'fastaInput' in files.keys():
        resp = dict(message='fastaInput field is mandatory')
        return Response(json.dumps(resp), mimetype='application/json',status=400)
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

    #save output     output_filepath = 

    output_filename = f'{tmp_uid}.output'
    output_filepath = f'{TMP_STORAGE}/{output_filename}'
    with open(output_filepath, 'wb') as out:
        out.write(geneid_ouput)

    exec_time = str(round(end-start, 2))

    #make response
    response = {
        'execTime':exec_time,
        'command':" ".join(geneid_exec_args),
        'input':{
            'fasta':fasta_name,
            'indexedFasta':indexed_fasta_name
        }
    }
    
    if gff_output:
        sorted_gff_name = f'{output_filename}.sorted.gff'
        sorted_gff_path = f'{TMP_STORAGE}/{sorted_gff_name}'
        gt_cmd = ['gt','gff3','-sortlines','-tidy','-retainids','-o', sorted_gff_path, output_filepath]
        check_output(gt_cmd)
        check_output(['bgzip', sorted_gff_path])
        check_output(['tabix', f'{sorted_gff_path}.gz'])
        # gt gff3 -sortlines -tidy -retainids yourfile.gff > yourfile.sorted.gff
        # bgzip yourfile.sorted.gff
        # tabix yourfile.sorted.gff.gz
        response['output'] = output_filename
    # else:
        #create all the file needed to visualize in the genome browser


    #
# def parse_params(data, files):
#     #parse files
#     try:
#         geneid_result = GeneIdResults()
#         options = list()
#         options.append(GENEID)
#         fasta = create_tempfile('fasta')
#         files['fasta'].save(fasta.name)
#         if 'evidences' in files.keys():
#             gff = create_tempfile('gff')
#             files['evidences'].save(gff.name)
#         else:
#             gff = None
#         app.logger.info(data)
#         param = create_tempfile('param')
#         param_file = TaxaFile.objects(name=data['param']).first()
#         geneid_result.param_species = param_file.organism ## name field is required
#         param.write(param_file.file.read())
#         options.append('-3P')
#         options.append(param.name) ##param tmpfile path
#         if 'options' in data:
#             for value in data.getlist('options'):
#                 if value:
#                     options.extend(value.split(","))
#         if 'output' in data:
#             options.append(data['output'])
#         if 'mode' in data and data['mode'] == '-o':
#             options.append(data['mode'])  
#         if 'mode' in data.keys() and gff and gff.name:
#             cmd = '-R' if data['mode'] == 'normal' or data['mode'] == '-o' else data['mode']
#             options.extend([cmd, gff.name])
#             fasta.seek(0)
#         options.append(fasta.name)
#         geneid_result.geneid_cmd = ' '.join(options)
#         output = create_tempfile('stdout')
#         launch_geneid(options, output, geneid_result)
#         output.seek(0)
#         app.logger.info(geneid_result.run_time)
#     except Exception as e:
#         app.logger.info(e)
#         shutil.rmtree('/tmp') 

#     #parse data



# def programs_configs(data,files):
#     geneid_result = GeneIdResults()
#     param = create_tempfile('param')
#     options = geneid_options(data,geneid_result,param)
#     # add this line to get fasta size
#     if 'fastaFile' in files.keys():
#         app.logger.info('fastafile')
#         fasta = create_tempfile('fasta')
#         files['fastaFile'].save(fasta.name)
#     elif 'fastaText' in data.keys():
#         fasta = create_tempfile('fasta')
#         fasta.write(data['fastaText'].encode())
#         fasta.seek(0)
#     if 'gffFile' in files.keys():
#         gff = create_tempfile('gff')
#         files['gffFile'].save(gff.name)
#     elif 'gffText' in data.keys():
#         gff = create_tempfile('gff')
#         gff.write(data['gffText'].encode())
#         gff.seek(0)
#     else:
#         gff = None
#     if 'mode' in data.keys() and gff and gff.name:
#         cmd = '-R' if data['mode'] == 'normal' or data['mode'] == '-o' else data['mode']
#         options.extend([cmd, gff.name])
#     psfile = create_tempfile('ps') if 'gff2ps' in data.keys() and data['gff2ps'] else None
#     ##run geneid
#     fasta.seek(0)
#     options.append(fasta.name)
#     geneid_result.geneid_cmd = ' '.join(options)
#     output = create_tempfile('stdout')
#     launch_geneid(options, output, geneid_result)

#     app.logger.info('AFTER GENEID')

#     param.close()
#     output.seek(0)
#     fasta.close()
#     if gff:
#         gff.close()
#     if psfile:
#         jpg = create_tempfile('jpg')
#         ##run gff2ps
#         psfile.write(launch_gff2ps(output))
#         psfile.seek(0)

#         app.logger.info('AFTER GFF2PS')
        
#         os.system('convert -rotate 90 ' + psfile.name + ' ' + jpg.name) #convert ps to jpg 

#         # ps_file = ResultFiles(file=psfile, type='application/PostScript', name = psfile.name).save()
#         # jpg_file = ResultFiles(file=jpg, type='image/jpg', name=jpg.name).save()
#         geneid_result.ps = ps_file
#         geneid_result.jpg = jpg_file
#         psfile.close()
#         jpg.close()
#     try:
#         if os.path.getsize(output.name) >= 15000000:
#             # output_file = ResultFiles(file = output, type='text/plain', name = output.name).save()
#             geneid_result.output_file = output_file
#         else:
#             with open(output.name, 'r') as output:
#                 geneid_result.output = "\n".join(output.readlines())
#         geneid_result.save()
        
#     except Exception as e:
#         app.logger.error(e)
#     return geneid_result
    
# def launch_geneid(options,output,model):
#     app.logger.info("LAUNCHING GENEID...")
#     start_time = time.time()
#     popen = subprocess.Popen(tuple(options), stdout=output,  stderr=output)
#     while popen.poll() is None:
#         time.sleep(0.5)
#     end_time = time.time()
#     model.run_time = str(round(end_time - start_time, 2))


# def launch_gff2ps(output):
#     args = (GFF2PS,'-C',GFF2PS_PARAM, output.name)
#     app.logger.info("LAUNCHING GFF2PS...")
#     popen = subprocess.Popen(args, stdout=subprocess.PIPE)
#     ouput, error = popen.communicate()
#     if ouput:
#         return ouput
#     elif error:
#         return error
#     else:
#         return 

# def geneid_options(data,geneid_model,param):
#     options= []
#     options.append(GENEID)
#     param_file = TaxonFile.objects(name=data['param']).first()
#     geneid_model.param_species = param_file.organism.fetch().name ## name field is required
#     param.write(param_file.file.read())
#     options.append('-P')
#     options.append(param.name) ##param tmpfile path
#     if 'options' in data:
#         for value in data.getlist('options'):
#             if value:
#                 options.extend(value.split(","))
#     if 'output' in data:
#         options.append(data['output'])
#     if 'mode' in data and data['mode'] == '-o':
#         options.append(data['mode'])  
#     return options

