from db.models import Assembly, Chromosome, Organism
from errors import NotFound
from ..utils import ncbi_client
from ..organism import organisms_service
from mongoengine.queryset.visitor import Q
from datetime import datetime

ASSEMBLY_FIELDS = ['display_name','chromosomes','assembly_accession','biosample','bioproject_lineages','biosample_accession','org']

ASSEMBLY_LEVELS = ['Chromosome', 'Scaffold', 'Complete Genome', 'Contig']


def get_assemblies(filter=None, filter_option='assembly_name', 
                    offset=0, submitter=None,
                    limit=20, start_date=None, 
                    end_date=datetime.today().strftime('%Y-%m-%d'), assembly_level=None,
                    sort_order=None, sort_column=None):  
    query=dict()
    ## filter match for accession, assembly name or species name
    if filter:
        filter_query = get_filter(filter, filter_option)
    else:
        filter_query = None
    if assembly_level and assembly_level in ASSEMBLY_LEVELS:
        query['metadata__assembly_level'] = assembly_level
    if submitter:
        query['metadata__submitter'] = submitter
    if start_date:
        date_query = (Q(metadata__submission_date__gte=start_date) & Q(metadata__submission_date__lte=end_date))
    else:
        date_query = None
    if filter_query and date_query:
        visitor_query = filter_query & date_query
        assemblies = Assembly.objects(visitor_query, **query).exclude('id','created')
    elif filter_query:
        assemblies = Assembly.objects(filter_query, **query).exclude('id','created')
    elif date_query:
        assemblies = Assembly.objects(date_query, **query).exclude('id','created')
    else:
        assemblies = Assembly.objects(**query).exclude('id','created')
    if sort_column:
        if sort_column == 'submission_date':
            sort_column = 'metadata.submission_date'
        elif sort_column == 'size':
            sort_column = 'metadata.estimated_size'
        elif sort_column == 'contig_n50':
            sort_column = 'metadata.contig_n50'
        sort = '-'+sort_column if sort_order == 'desc' else sort_column
        assemblies = assemblies.order_by(sort)
    return assemblies.count(), assemblies[int(offset):int(offset)+int(limit)]

def get_filter(filter, option):
    if option == 'taxid':
        return (Q(taxid__iexact=filter) | Q(taxid__icontains=filter))
    elif option == 'scientific_name':
        return (Q(scientific_name__iexact=filter) | Q(scientific_name__icontains=filter))
    else:
        return (Q(assembly_name__iexact=filter) | Q(assembly_name__icontains=filter))


def create_assembly_from_ncbi_data(assembly):
    print('CREATING ASSEMBLY FROM NCBI DATA')
    ass_data = dict(accession = assembly['assembly_accession'],assembly_name= assembly['display_name'],scientific_name=assembly['org']['sci_name'],taxid=assembly['org']['tax_id'])
    taxid = ass_data['taxid']
    organism = organisms_service.get_or_create_organism(ass_data['taxid'])
    if not organism:
        print(f"organism with taxid: {taxid} not found!")
        return
    ass_metadata=dict()
    for key in assembly.keys():
        if key not in ASSEMBLY_FIELDS:
            ass_metadata[key] = assembly[key]
        ass_obj = Assembly(metadata=ass_metadata, **ass_data).save()
        organism.modify(add_to_set__assemblies=ass_obj.accession)
        organism.save()
        if 'chromosomes' in assembly.keys():
            create_chromosomes(ass_obj, assembly['chromosomes'])
        return ass_obj


def create_chromosomes(assembly,chromosomes):
    for chr in chromosomes:
        if not 'accession_version' in chr.keys():
            continue
        chr_obj = Chromosome.objects(accession_version = chr['accession_version']).first()
        if not chr_obj:
            metadata=dict()
            for k in chr.keys():
                if k != 'accession_version':
                    metadata[k] = chr[k]
            chr_obj = Chromosome(accession_version=chr['accession_version'], metadata=metadata).save()
        assembly.modify(add_to_set__chromosomes=chr_obj.accession_version)

def get_chromosomes(accession):
    assembly = Assembly.objects(accession=accession).first()
    if not assembly or not assembly.chromosomes:
        return
    return Chromosome.objects(accession_version__in=assembly.chromosomes).as_pymongo()

##return response obj
def create_assembly_from_accession(accession):
    resp_obj=dict()
    assembly_obj = Assembly.objects(accession=accession).first()
    if assembly_obj:
        resp_obj['message'] = f"{accession} already exists"
        resp_obj['status'] = 400
        return resp_obj
    ncbi_response = ncbi_client.get_assembly(accession)
    if not ncbi_response:
        resp_obj['message'] = f"{accession} not found in INSDC"
        resp_obj['status'] = 400
        return resp_obj
    assembly_obj = create_assembly_from_ncbi_data(ncbi_response)
    if assembly_obj:
        resp_obj['message'] = f'{assembly_obj.accession} correctly saved' 
        resp_obj['status'] = 201
        return resp_obj
    resp_obj['message'] = 'Unhandled error'
    resp_obj['status'] = 500
    return resp_obj
    
def delete_assembly(accession):
    assembly_obj = Assembly.objects(accession=accession).first()
    if not assembly_obj:
        raise NotFound 
    organism = Organism.objects(taxid=assembly_obj.taxid).first()
    organism.modify(pull__assemblies=assembly_obj.accession)
    organism.save()
    assembly_obj.delete()
    return accession
