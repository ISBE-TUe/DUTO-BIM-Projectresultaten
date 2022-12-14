import sys

from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout 
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import viewsets, permissions
from rest_framework.parsers import JSONParser
from .forms import NewIlsProjectForm, NewIfcProjectForm, NewIlsCheckProjectForm
from .forms import NewUserForm
from .models import Project, User, Check, File, Report, Result, ILSFile
from .serializers import ProjectSerializer, ReportSerializer, ResultSerializer, CheckSerializer
from validator.online import models
import os
import mimetypes
from datetime import datetime
import threading
from pathlib import Path
from urllib.request import pathname2url
import urllib.parse
import requests
import ifcopenshell
#from ifcopenshell import ids
from rest_framework.decorators import api_view
from .ifctester import ids, reporter
from pprint import pprint


def settings(request):
    sparql_endpoint_1 = models.sparql_endpoint_1
    sparql_endpoint_2 = models.sparql_endpoint_2
    default_namespace = models.default_namespace
    org_default_namespace = models.o_oms
    current_org = models.current_org
    return render(request, 'settings.html', {'sparql_endpoint_1':sparql_endpoint_1, 'sparql_endpoint_2':sparql_endpoint_2, 'default_namespace':default_namespace, 'org_default_namespace':org_default_namespace, 'current_org':current_org})

def getProjects(request):    
    if request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user.id)
        context={       
            'projects': projects,
        } 
        return render(request, 'projects.html', context)
    else:
        return redirect('login')

def getAllChecks(request):
    if request.user.is_authenticated:
        allChecks = Check.objects.all()
        projects = Project.objects.filter(user=request.user.id)
        checks = []
        for check in allChecks:
            for project in projects :
                if check.project == project :
                    checks.append(check)
        context={
            'checks': checks,
        } 
        return render(request, 'checks.html', context)
    else:
        return redirect('login')

def getAllReports(request):
    if request.user.is_authenticated:
        allReports = Report.objects.all()
        projects = Project.objects.filter(user=request.user.id)
        reports = []
        for report in allReports:
            for project in projects :
                if report.check1.project == project :
                    reports.append(report)
        context={       
            'reports': reports,
        } 
        return render(request, 'reports.html', context)
    else:
        return redirect('login')

def downloadFile(request, filename):
    if request.user.is_authenticated == False:
        return redirect('login')

    if filename != '':
        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Define the full file path
        filepath = BASE_DIR + '/../uploads/' + filename
        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response
    else:
        # Load the template
        return render(request, 'projects.html')

def createNewProject(request):    
    if request.user.is_authenticated == False:
        return redirect('login')
    return render(request, 'newproject.html')

def createNewIfcProject(request):
    if request.user.is_authenticated == False:
        return redirect('login')

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewIfcProjectForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            users = models.User.objects.all()
            userAvailable = False
            theUser = models.User
            for user in users:
                if user.name == request.user.username:
                    userAvailable = True
                    theUser = user
                    break

            if not userAvailable :
                user = models.User()
                user.name = request.user.username
                user.id = request.user.id
                theUser = user
                user.save()

            file = File()
            file.fileName = form.cleaned_data['file']
            file.fileContent = request.FILES['file']
            file.save()
            # cutting away the uploads file location from the string
            name = file.fileContent.name.split("/", 1)
            file.fileNameStored = name[1]
            file.save()

            project = Project()
            project.title = form.cleaned_data['title']
            project.user = theUser
            project.type = form.cleaned_data['type']  
            project.file = file
            project.save()

#            if project.type == "IFC-SPF":
#                # transform file to XKT
#                t = threading.Thread(target=transformIFCtoXKT, args=[file.fileNameStored])
#                t.setDaemon(True)
#                t.start()
#
#            if project.type == "IFC-SPF":
#                # transform file to LBD RDF Graph
#                t = threading.Thread(target=transformIFCtoLBD, args=[file.fileNameStored])
#                t.setDaemon(True)
#                t.start()

            return redirect('projects')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewIfcProjectForm()

    return render(request, 'newifcproject.html', {'form': form})

def createNewIlsProject(request):
    if request.user.is_authenticated == False:
        return redirect('login')

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewIlsProjectForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            users = models.User.objects.all()
            userAvailable = False
            theUser = models.User
            for user in users:
                if user.name == request.user.username:
                    userAvailable = True
                    theUser = user
                    break

            if not userAvailable :
                user = models.User()
                user.name = request.user.username
                user.id = request.user.id
                theUser = user
                user.save()

            file = File()
            file.fileName = form.cleaned_data['file']
            file.fileContent = request.FILES['file']
            file.save()
            # cutting away the uploads file location from the string
            name = file.fileContent.name.split("/", 1)
            file.fileNameStored = name[1]
            file.save()

            project = Project()
            project.title = form.cleaned_data['title']
            project.user = theUser
            project.type = form.cleaned_data['type']  
            project.file = file
            project.save()
            
            return redirect('projects')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewIlsProjectForm()

    return render(request, 'newilsproject.html', {'form': form})

def createNewIlsCheckProject(request):
    if request.user.is_authenticated == False:
        return redirect('login')

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewIlsCheckProjectForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            users = models.User.objects.all()
            userAvailable = False
            theUser = models.User
            for user in users:
                if user.name == request.user.username:
                    userAvailable = True
                    theUser = user
                    break

            if not userAvailable :
                user = models.User()
                user.name = request.user.username
                user.id = request.user.id
                theUser = user
                user.save()

            ifcfile = File()
            ifcfile.fileName = form.cleaned_data['ifcfile']
            ifcfile.fileContent = request.FILES['ifcfile']
            ifcfile.save()
            # cutting away the uploads file location from the string
            ifcname = ifcfile.fileContent.name.split("/", 1)
            print(ifcname)
            ifcfile.fileNameStored = ifcname[1]
            ifcfile.save()

            ilsfile = ILSFile()
            ilsfile.ilsfileName = form.cleaned_data['ilsfile']
            ilsfile.ilsfileContent = request.FILES['ilsfile']
            ilsfile.save()
            # cutting away the uploads file location from the string
            ilsname = ilsfile.ilsfileContent.name.split("/", 1)
            print(ilsname)
            ilsfile.ilsfileNameStored = ilsname[1]
            ilsfile.save()

            project = Project()
            project.title = form.cleaned_data['title']
            project.user = theUser
            project.type = form.cleaned_data['type']  
            project.file = ifcfile
            project.ilsfile = ilsfile
            project.save()
            
            return redirect('projects')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewIlsCheckProjectForm()

    return render(request, 'newilscheckproject.html', {'form': form})

#def transformIFCtoXKT(filename):
#    try:     
#        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#        fileIFC = BASE_DIR + '/../uploads/' + fileName
#       
#    except Exception as e:
#        print(e)
#    return

def transformIFCtoLBD(fileName):
    try:        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fileIFC = BASE_DIR + '/../uploads/' + fileName
        fileTTL = os.path.splitext(fileIFC)[0]+'.ttl'   
        #fileGLTF = os.path.splitext(fileIFC)[0]+'.gltf'   
        #print(fileIFC)
        #print(fileTTL)
        #jarpath = BASE_DIR + '\\..\\static\\scripts\\' + 'IFCtoLBD-0.1-shaded.jar'
        #jarpath = jarpath.replace(' ', '%20')

        ## Transform to LBD graph
        jarpath = "C:/" + "IFCtoLBD-0.1-shaded.jar"
        os.system("java -jar \"" + jarpath + "\" \"" + fileIFC + "\" \"" + fileTTL + "\"")
        #print(settings.GRAPHDB_BIN + "\importrdf load -f -i DHRD -m parallel " + fileTTL)
        #os.system(settings.GRAPHDB_BIN + "\importrdf load -f -i DHRD -m parallel " + fileTTL)  

        ## Load into GraphDB
        headers = {
            'Content-Type': 'application/x-turtle',
            'Accept': 'application/json'
        }
        with open(fileTTL, 'rb') as f:
            requests.post("http://localhost:7200/repositories/DHRD/statements", data=f, headers=headers)   

        ## Transform to IfcConvert matter
        #print('\"' + BASE_DIR + '\\..\\static\\scripts\\' + 'IfcConvert\" \"' + fileIFC + '\" \"' + fileGLB + '\"')
        #x = '\"' + BASE_DIR + '\\..\\static\\scripts\\' + 'IfcConvert\" \"' + fileIFC + '\" \"' + fileGLTF + '\"'
        #works#######x1 = r'C:/IfcConvert' + ' \"' + fileIFC + '\" \"' + fileGLTF + '\"'
        #works#######print(x1)
        #works#######os.system(x1)

    except Exception as e: 
        print(e)
    return

def deleteProject(request, projectId):
    if request.user.is_authenticated == False:
        return redirect('login')

    projects = Project.objects.all() 
    project = projects.get(id=projectId)
    project.delete()

    projects = Project.objects.all() #for all the records 
    context={       
      'projects': projects,
    } 
    return render(request, 'projects.html', context)

def getChecks(request, projectId):
    if request.user.is_authenticated == False:
        return redirect('login')

    neededchecks = getTheChecks(projectId)
    context={       
        'projectId': projectId,
        'checks': neededchecks,
    } 
    return render(request, 'checks.html', context)

def createNewCheck(request, projectId):
    if request.user.is_authenticated == False:
        return redirect('login')

    check = Check()
    projects = Project.objects.all() #for all the records 
    check.project = projects.get(id=projectId)
    check.created = datetime.now()
    check.save()

    neededchecks = getTheChecks(projectId)
            
    context={       
        'projectId': projectId,
        'checks': neededchecks,
    } 

    return render(request, 'checks.html', context)

def deleteCheck(request, checkId):
    if request.user.is_authenticated == False:
        return redirect('login')

    checks = Check.objects.all() 
    check = checks.get(id=checkId)
    projectId = check.project.id
    check.delete()

    neededchecks = getTheChecks(projectId)
            
    context={       
        'projectId': projectId,
        'checks': neededchecks,
    } 

    return render(request, 'checks.html', context)

def deleteReport(request, reportId):
    if request.user.is_authenticated == False:
        return redirect('login')

    reports = Report.objects.all() 
    report = reports.get(id=reportId)
    report.delete()

    return redirect('allchecks')

def getReports(request, checkId, type):  
    print('report type: ' + str(type))  
    if request.user.is_authenticated == False:
        return redirect('login')

    neededReports = getTheReports(checkId, type)
    if len(neededReports) == 1:
        neededResults = getTheResults(neededReports[0].id)
    context={
        'checkId': checkId,
        'reports': neededReports, 
        'results': neededResults,
        'ifcURL' : neededReports[0].check1.project.file.fileNameStored       
    }
    return render(request, 'reports.html', context)

### login functionality
def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )            
			return redirect('projects')##../projects/
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="registration/register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect('projects')
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="registration/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect('/')

# Helper functions
def getTheChecks(projectId):
    checks = Check.objects.all()
    neededchecks = []
    for check in checks:
        if check.project.id == projectId:
            neededchecks.append(check)
    return neededchecks

def getTheReports(checkId, type):
    print('getReports type'+ str(type))
    reports = Report.objects.all()
    neededReports = []
    for report in reports:
        if report.check1 is not None:
            if report.check1.id == checkId:
                if report.type.startswith(type):
                    neededReports.append(report)
    if len(neededReports) == 0:
        newReport = createNewReport(checkId, type)
        neededReports.append(newReport)
    return neededReports

def getTheResults(reportId):
    results = Result.objects.all()
    neededResults = []
    for result in results:
        if result.report.id == reportId:
            neededResults.append(result)
    return neededResults

def createNewReport(checkId, type):
    r = Report()
    r.check1 = Check.objects.get(pk=checkId)
    r.type = type
    r.created = datetime.now()
    r.save()

    #compute result
    if(type == 'IFC-SPF'):
        print("IFC-SPF check")
        doTheIFCSPFCheck(r)        
    elif (type == 'ILS'):
        # in the user interface, all ILS reports are grouped under one link. So over here we need to figure out what kind of actual ILS was uploaded and to a corresponding check.
        print("ILS check")
        if(r.check1.project.type == 'ILS-PDF'):
            r.type = 'ILS-PDF'
            doTheILSPDFCheck(r)
        elif(r.check1.project.type == 'ILS-SHACL'):
            r.type = 'ILS-SHACL'
            doTheILSSHACLCheck(r)
        elif(r.check1.project.type == 'ILS-XML'):
            r.type = 'ILS-XML'
            doTheILSXMLCheck(r)
        elif(r.check1.project.type == 'ILS-JSON'):
            r.type = 'ILS-JSON'
            doTheILSJSONCheck(r)
        elif(r.check1.project.type == 'ILS-CHECK'):
            r.type = 'ILS-XML'
            doTheILSXMLCheck(r)
        elif(r.check1.project.type == 'ICDD'):
            r.type = 'ILS-XML'
            doTheILSXMLCheck(r)
        else:
            print("oh no, we missed this project type: " + r.check1.project.type)        
    elif (type == 'ILS-PDF'):
        print("ILS-PDF check")
        doTheILSPDFCheck(r)
    elif (type == 'ILS-SHACL'):
        print("ILS-SHACL check")
        doTheILSSHACLCheck(r)
    elif (type == 'ILS-JSON'):
        print("ILS-JSON check")
        doTheILSJSONCheck(r)
    elif (type == 'ILS-XML'):
        print("ILS-XML check")
        doTheILSXMLCheck(r)
    elif (type == 'ILS-CHECK'):
        print("ICDD check")
        doTheICDDCheck(r)
    elif (type == 'ICDD'):
        print("ICDD check")
        doTheICDDCheck(r)
    else : 
        print("oh no, we missed this project type: " + type)

    return r

def doTheIFCSPFCheck(report):
    checkFileType(report)
    checkIFCFileMetadata(report)
    calculateTotalScores(report)
    return

def doTheILSPDFCheck(report):
    checkFileType(report)
    calculateTotalScores(report)
    return
    
def doTheILSSHACLCheck(report):
    checkFileType(report)
    calculateTotalScores(report)
    return
    
def doTheILSJSONCheck(report):
    checkFileType(report)
    calculateTotalScores(report)
    return

def doTheILSXMLCheck(report):
    checkFileType(report)
    calculateTotalScores(report)
    return
    
def doTheICDDCheck(report):
    checkFileType(report)
    checkIFCFileMetadata(report)
    checkIDS(report)
    calculateTotalScores(report)
    return

def calculateTotalScores(report):
    results = getTheResults(report.id)
    print("start")
    for result in results:
        if (result.code == "metadata"):
            report.metadataScore += result.gain
            report.metadataTotal += result.total
        elif(result.code == "content"):
            report.contentScore += result.gain
            report.contentTotal += result.total 
        else:
            print("nothing happened")
        report.save()
    return

def checkIFCFileMetadata(report):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = BASE_DIR + '/../uploads/' + report.check1.project.file.fileNameStored
    path = open(filepath, 'rb')
    
    f = ifcopenshell.open(filepath)
    # check if there is something filled for the IFC schema
    if(f.schema != None): 
        addNewResult(report, "IFC Schema", "The IFC schema is included inside the IFC file header", "metadata", "IFC Schema", f.schema, True, 4, 4)
    else:
        addNewResult(report, "IFC Schema", "The IFC schema is included inside the IFC file header", "metadata", "IFC Schema", f.schema, False, 0, 4)

    # check if correct IFC schema
    if(f.schema != "IFC2X3" and f.schema != "IFC4"): 
        addNewResult(report, "IFC Schema", "An existing and published IFC schema is included inside the IFC file header", "metadata", "Correct IFC Schema", f.schema, False, 0, 4)
    else:
        addNewResult(report, "IFC Schema", "An existing and published IFC schema is included inside the IFC file header", "metadata", "Correct IFC Schema", f.schema, True, 4, 4)

    file_name = f.wrapped_data.header.file_name
    #check file name exists
    if(file_name.name != None and file_name.name != ""): 
        addNewResult(report, "File name in metadata tags", "The file name is given inside the IFC file header (FILE_NAME())", "metadata", "File name in metadata tags", file_name.name, True, 1, 1)
    else :
        addNewResult(report, "File name in metadata tags", "The file name is given inside the IFC file header (FILE_NAME())", "metadata", "File name in metadata tags", file_name.name, False, 0, 1)

    #check whether file name matches with actual file name
    #TODO

    # The time of creation of the IFC file is given inside the IFC file header (FILE_NAME())
    if(file_name.time_stamp != None and file_name.time_stamp != ""): 
        addNewResult(report, "Time Stamp", "The time of creation of the IFC file is given inside the IFC file header (FILE_NAME())", "metadata", "Time Stamp", file_name.time_stamp, True, 2, 2)
    else :
        addNewResult(report, "Time Stamp", "The time of creation of the IFC file is given inside the IFC file header (FILE_NAME())", "metadata", "Time Stamp", file_name.time_stamp, False, 0, 2)

    # The time of creation of the IFC file in the IFC file header matches with time of creation of the file (file settings)
    # TODO

    # The time of creation of the IFC file in the IFC file header matches with time of last modification of the file (file settings)
    # TODO

    # The author name is given inside the IFC file header (FILE_NAME())
    if(file_name.author[0] != None and file_name.author[0] != ""): 
        addNewResult(report, "Author", "The author name is given inside the IFC file header (FILE_NAME())", "metadata", "Author", file_name.author[0], True, 2, 2)
    else:
        addNewResult(report, "Author", "The author name is given inside the IFC file header (FILE_NAME())", "metadata", "Author", file_name.author[0], False, 0, 2)

    # The authoriser's name is given inside the IFC file header (FILE_NAME())
    if(file_name.author[0] != None and file_name.author[0] != ""): 
        addNewResult(report, "Authorization", "The authoriser's name is given inside the IFC file header (FILE_NAME())", "metadata", "Authorization", file_name.authorization, True, 2, 2)
    else:
        addNewResult(report, "Authorization", "The authoriser's name is given inside the IFC file header (FILE_NAME())", "metadata", "Authorization", file_name.authorization, False, 0, 2)

    # The organization name is given inside the IFC file header (FILE_NAME())
    if(file_name.organization[0] != None and file_name.organization[0] != ""): 
        addNewResult(report, "Organization", "The organization name is given inside the IFC file header (FILE_NAME())", "metadata", "Organization", file_name.organization[0], True, 1, 1)
    else: 
        addNewResult(report, "Organization", "The organization name is given inside the IFC file header (FILE_NAME())", "metadata", "Organization", file_name.organization[0], False, 0, 1)

    # The name of the originating system is given inside the IFC file header (FILE_NAME())
    if(file_name.originating_system != None and file_name.originating_system != ""): 
        addNewResult(report, "Originating System", "The name of the originating system is given inside the IFC file header (FILE_NAME())", "metadata", "Originating System", file_name.originating_system, True, 2, 2)
    else:
        addNewResult(report, "Originating System", "The name of the originating system is given inside the IFC file header (FILE_NAME())", "metadata", "Originating System", file_name.originating_system, False, 0, 2)

    # The name of the toolbox used to create the IFC file are given inside the IFC file header (FILE_NAME())
    if(file_name.originating_system != None and file_name.originating_system != ""): 
        addNewResult(report, "Preprocessor Version", "The name of the toolbox used to create the IFC file are given inside the IFC file header (FILE_NAME())", "metadata", "Preprocessor Version", file_name.preprocessor_version, True, 3, 3)
    else: 
        addNewResult(report, "Preprocessor Version", "The name of the toolbox used to create the IFC file are given inside the IFC file header (FILE_NAME())", "metadata", "Preprocessor Version", file_name.preprocessor_version, False, 0, 3)

    file_description = f.wrapped_data.header.file_description
    # The underlying view definition is named (Coordination View, Reference View, etc.)
    if(file_description.description[0] != None and file_description.description[0] != ""): 
        addNewResult(report, "View Definition", "The underlying view definition is named (Coordination View, Reference View, etc.)", "content", "View Definition", file_description.description[0], True, 4, 4)
    else: 
        addNewResult(report, "View Definition", "The underlying view definition is named (Coordination View, Reference View, etc.)", "content", "View Definition", file_description.description[0], False, 0, 4)

    # The implementation level of the view definition is given (e.g. 2;1)
    if(file_description.implementation_level != None and file_description.implementation_level != ""): 
        addNewResult(report, "Implementation Level of View Definition", "The implementation level of the view definition is given (e.g. 2;1)", "content", "Implementation Level of View Definition", file_description.implementation_level, True, 3, 3)
    else: 
        addNewResult(report, "Implementation Level of View Definition", "The implementation level of the view definition is given (e.g. 2;1)", "content", "Implementation Level of View Definition", file_description.implementation_level, False, 0, 3)
    
    # Sites are present in the file
    sites = f.by_type("IfcSite")
    if(sites is not None and len(sites) != 0):
        addNewResult(report, "Number of Sites", "Sites are present in the file", "content", "Number of Sites", len(sites), True, 4, 4)
    else: 
        addNewResult(report, "Number of Sites", "Sites are present in the file", "content", "Number of Sites", 0, False, 0, 4)

    # Buildings are present in the file   
    buildings = f.by_type("IfcBuilding")
    if(buildings is not None and len(buildings) != 0):
        addNewResult(report, "Number of Buildings", "Buildings are present in the file", "content", "Number of Buildings", len(buildings), True, 3, 3)
    else:        
        addNewResult(report, "Number of Buildings", "Buildings are present in the file", "content", "Number of Buildings", 0, False, 0, 3)

    # Building Storeys are present in the file  
    storeys = f.by_type("IfcBuildingStorey")
    if(storeys is not None and len(storeys) != 0):
        addNewResult(report, "Number of Building Storeys", "Building Storeys are present in the file", "content", "Number of Building Storeys", len(storeys), True, 1, 1)
    else:
        addNewResult(report, "Number of Building Storeys", "Building Storeys are present in the file", "content", "Number of Building Storeys", 0, True, 0, 1)

    # Building Elements are present in the file  
    products = f.by_type("IfcProduct")
    if(products is not None and len(products) != 0):
        addNewResult(report, "Number of Building Elements", "Building Elements are present in the file ", "content", "Number of Building Elements", len(products), True, 2, 2)
    else:
        addNewResult(report, "Number of Building Elements", "Building Elements are present in the file ", "content", "Number of Building Elements", 0, False, 0, 2)

    return

def checkFileType(report):
    print("starting checkFileType")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = BASE_DIR + '/../uploads/' + report.check1.project.file.fileNameStored
    path = open(filepath, 'rb')

    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    if(mime_type is None):        
        mime_type = os.path.splitext(filepath)[1]
    if(mime_type is not None): 
        res1 = Result()
        res1.created = datetime.now()
        res1.title = "Filetype"
        res1.description = "Check if there is a file type available (MIME type, file extension)"
        res1.report = report
        res1.code = "metadata"
        res1.property = "Filetype"
        res1.value = mime_type
        res1.success = True
        res1.gain = 1
        res1.total = 1
        res1.save()
    else:
        res1 = Result()
        res1.created = datetime.now()
        res1.title = "Filetype"
        res1.description = "Check if there is a file type available (MIME type, file extension)"
        res1.report = report
        res1.code = "metadata"
        res1.property = "Filetype"
        res1.value = mime_type
        res1.success = True
        res1.gain = 0
        res1.total = 1
        res1.save()


    mimetype = str(mimetypes.guess_type(filepath))
    extension = str(os.path.splitext(filepath)[1])
    print("mimetype : " + mimetype)
    print("extension : " + extension)
    res2 = Result()
    res2.created = datetime.now()
    res2.title = "Filetype Match"
    res2.description = "Check if the file extension matches with the MIME type and therefore is correct"
    res2.report = report
    res2.code = "metadata"
    res2.property = "Filetype Match"
    if(("application/pdf" in mimetype and ".pdf" in extension) or
    ("application/ifc" in mimetype and ".ifc" in extension) or
    ("text/xml" in mimetype and ".xml" in extension) or
    ("application/json" in mimetype and ".json" in extension)):
        res2.value = "Match"
        res2.success = True
        res2.gain = 2
        res2.total = 2
    else : 
        res2.value = "No match"
        res2.success = False
        res2.gain = 0
        res2.total = 2
    res2.save()

    return

def checkIDS(report):
    #print(models.default_ids)
    #checks = ids.open(models.default_ids)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ifc_model = ifcopenshell.open(  BASE_DIR + '/../uploads/' + report.check1.project.file.fileNameStored)
    ilsfile = ids.open(BASE_DIR + '/../uploads/' + report.check1.project.ilsfile.ilsfileNameStored)
    ilsfile.validate(ifc_model)
    #res = ids.report
    ids_report = reporter.Json(ilsfile)
    res = ids_report.report()
    
    for s in res['specifications']:
        for x in s['requirements']:
            pprint(x)
        res1 = Result()
        res1.created = datetime.now()
        res1.title = "DUTO IDS/ILS"
        res1.description = "Conformance with IDS/ILS"
        res1.report = report
        res1.code = "content"
        res1.property = "Information Delivery Specification "
        res1.value =  f"Requirement '{s['name']}' succeeded in {s.get('total_successes')} times of {s['total']}"
        res1.success = True
        res1.gain = s.get('total_successes')
        res1.total = s['total']
        res1.save()
    return


def addNewResult(report, title, description, code, property, value, success, gain, total):
    res = Result()
    res.created = datetime.now()
    res.title = title
    res.description = description
    res.report = report
    res.code = code
    res.property = property
    res.value = value
    res.success = success
    res.gain = gain
    res.total = total
    res.save()
    return


#####################################
# API matter
#####################################


class api:

    @api_view(['GET'])
    def getProjects(request):
        """
        List all projects.
        """
        #if request.method == 'GET':
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(serializer.data, safe=False)

        #elif request.method == 'POST':
        #    data = JSONParser().parse(request)
        #    serializer = SnippetSerializer(data=data)
        #    if serializer.is_valid():
        #        serializer.save()
        #        return JsonResponse(serializer.data, status=201)
        #    return JsonResponse(serializer.errors, status=400)

    @api_view(['GET'])
    def getChecks(request):
        """
        List all checks.
        """
        checks = Check.objects.all()
        serializer = CheckSerializer(checks, many=True)
        return JsonResponse(serializer.data, safe=False)
      
    @api_view(['GET'])  
    def getReports(request):
        """
        List all reports.
        """
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return JsonResponse(serializer.data, safe=False)
      
    @api_view(['GET'])  
    def getResults(request):
        """
        List all results.
        """
        results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return JsonResponse(serializer.data, safe=False)
