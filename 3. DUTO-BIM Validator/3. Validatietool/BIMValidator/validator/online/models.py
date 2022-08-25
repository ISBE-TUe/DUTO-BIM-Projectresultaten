import pathlib

from django.db import models
from rdflib import Graph, URIRef, BNode, Literal, Namespace, Dataset
from rdflib.namespace import RDFS, XSD, FOAF, OWL, RDF
from rdflib.plugins.stores import sparqlstore
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2, XML, TURTLE, JSON
import ifcopenshell
from django.conf import settings


###############################################################
### Connected SPARQL endpoints & document storage locations ###
###############################################################

sparql_endpoint_1 = settings.SPARQL_ENDPOINT_1
sparql_endpoint_2 = settings.SPARQL_ENDPOINT_2
document_storage_location = settings.MEDIA_ROOT
default_namespace = settings.DEFAULT_NAMESPACE
o_oms = settings.ORGANIZATION_DEFAULT_NAMESPACE
current_org = settings.CURRENT_ORG
default_ids = pathlib.Path("static/ids/duto_ids.xml")

######################################
### Global semantic web namespaces ###
######################################

o_ddss = 'https://github.com/chielvanderpas/ddss#'
ns_ddss = Namespace(o_ddss)
nss_ddss = 'ddss: <https://github.com/chielvanderpas/ddss#>'

o_rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
ns_rdf = Namespace(o_rdf)
nss_rdf = 'rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'

o_rdfs = 'http://www.w3.org/2000/01/rdf-schema#'
ns_rdfs = Namespace(o_rdfs)
nss_rdfs = 'rdfs: <http://www.w3.org/2000/01/rdf-schema#>'

o_bot = 'https://w3id.org/bot#'
ns_bot = Namespace(o_bot)
nss_bot = 'bot: <https://w3id.org/bot#>'

o_org = 'http://www.w3.org/ns/org#'
ns_org = Namespace(o_org)
nss_org = 'org: <http://www.w3.org/ns/org#>'

o_foaf = 'http://xmlns.com/foaf/0.1/'
ns_foaf = Namespace(o_foaf)
nss_foaf = 'foaf: <http://xmlns.com/foaf/0.1/>'



#######################################
### Specific semantic web instances ###
#######################################

ns_oms = Namespace(o_oms)
nss_oms = str('oms: <'+o_oms+'#>')

#######################################
### The object model                ###
#######################################

# Create your models here.
class FileTypes(models.TextChoices):
        ILSSHACL = 'ILS-SHACL', ('ILS-SHACL')
        ILSJSON = 'ILS-JSON', ('ILS-JSON')
        ILSXML = 'ILS-XML', ('ILS-XML')
        ILSPDF = 'ILS-PDF', ('ILS-PDF')
        IFCSPF = 'IFC-SPF', ('IFC-SPF')
        ICDD = 'ICDD', ('ICDD')

#class Validation(models.Model):
#    created = models.DateTimeField(auto_now_add=True)
#    title = models.CharField(max_length=100, blank=True, default='')
#    code = models.TextField()

class User(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')

class File(models.Model):
    fileName = models.CharField(max_length=100, blank=True, default='')
    fileContent = models.FileField(upload_to='uploads', default='')
    fileNameStored = models.CharField(max_length=100, blank=True, default='')
   
class Project(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=10,choices=FileTypes.choices, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE, default=0)

class Check(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    #type = models.CharField(max_length=10,choices=FileTypes.choices, default='')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #file = models.ForeignKey(File, on_delete=models.CASCADE)
    
class Report(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    check1 = models.ForeignKey(Check, on_delete=models.CASCADE)
    metadataScore = models.IntegerField(blank=True, default=0, null=True)
    metadataTotal = models.IntegerField(blank=True, default=0, null=True)
    contentScore = models.IntegerField(blank=True, default=0, null=True)
    contentTotal = models.IntegerField(blank=True, default=0, null=True)
    
class Result(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=400, blank=True, default='')
    code = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    property = models.CharField(max_length=100, blank=True, default='')
    value = models.CharField(max_length=100, blank=True, default='')
    success = models.BooleanField(default=False)
    gain = models.IntegerField(blank=True, default=0, null=True)
    total = models.IntegerField(blank=True, default=0, null=True)

#######################################
### Queries                         ###
#######################################

def rq_sparql_query(query):
    input = sparqlstore.SPARQLUpdateStore()
    input.open((sparql_endpoint_1))
    q = """
    """+query+"""
    """
    result = input.query(q)
    aims = rq_aim()
    output = []
    for row in result:
        triple = str(f"{row}")
        triple_rev = triple.replace('rdflib.term.URIRef(', '').replace('rdflib.term.Literal(', '').replace('(', '').replace(')', '').replace(o_rdf, 'rdf:').replace(o_rdfs, 'rdfs:').replace(o_bot, 'bot:').replace(o_foaf, 'foaf:').replace(o_org, 'org:').replace(o_ddss, 'ddss:').replace(o_oms, '').replace("'", "").replace(',', ' |')
        for aim in aims:
            aim_namespace = aim.namespace
            aim_name = aim.name
            triple_rev = triple_rev.replace(aim_namespace, aim_name+':')
        output.append(triple_rev)
    return output
