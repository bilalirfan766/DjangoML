from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.template.loader import render_to_string


# Create your views here.
def DisplayArtWork(request):
    try:
    ### Calling the Api to find All the Departments
        requestDepartments=requests.get('https://collectionapi.metmuseum.org/public/collection/v1/departments')
        ### Get the Json Response
        getDepartments=requestDepartments.json()
        ### Checking if its a First Request or Not
        if request.session.has_key('countGlobal') and request.session.has_key('countObjectsList'):
            ##get the Value from session
            countGlobal=request.session['countGlobal']
            countObjectsList=request.session['countObjectsList']
        else:
            ##Intializing the sessions for 1st Request to get all Departments and objects that have images
            request.session['countGlobal'] = 0
            request.session['countObjectsList'] = 0
            countGlobal = 0
            countObjectsList = 0

        if countGlobal == 0:
            ##Getting all the Department from the Response then using the First Department calling all its objects that have image
            DepartmentsLength=getDepartments['departments']
            request.session['lenDepartment'] = len(DepartmentsLength)
            request.session['countDepartment'] = 0
            ListDepartmentName=[]
            for i in range(0,len(DepartmentsLength)):
                departmentsIndex=DepartmentsLength[i]
                ##Getting all department Names
                ListDepartmentName.append(departmentsIndex["displayName"])
            request.session['DepartmentNamesList'] = ListDepartmentName
            request.session['countGlobal'] = 1
        if countObjectsList == 0:
            ##getting all the objects from that Department that has image
            getDepartmentNameValueList = request.session['DepartmentNamesList']
            getDepartmentNameListindex = request.session['countDepartment']
            LenofDept=request.session['lenDepartment']
            getDepartmentname=getDepartmentNameValueList[getDepartmentNameListindex]
            if getDepartmentNameListindex < LenofDept:
                getDepartmentNameListindex=getDepartmentNameListindex + 1
            else:
                request.session['countDepartment'] = 0
                getDepartmentNameListindex = 0
                request.session['countGlobal'] = 0
            request.session['countDepartment'] = getDepartmentNameListindex
            ###Calling the api that has images with that Department to get the all Object Ids
            ApiRequestString ='https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q='+str(getDepartmentname)
            getobjectsIDs=requests.get(ApiRequestString)
            getObjectIDres=getobjectsIDs.json()
            #Get all the objects
            getObjectIDvaluesList = getObjectIDres["objectIDs"]
            request.session['ListObjects'] = getObjectIDvaluesList
            request.session['ObjectsCount'] = 0
            request.session['countObjectsList'] = 1
        getCountsObject=request.session['ObjectsCount']
        request.session['ObjectsCount']=getCountsObject+1
        getObjectsIDvalueList = request.session['ListObjects']
        if getCountsObject >= len(getObjectsIDvalueList):
            request.session['countObjectsList'] = 0
            getCountsObject=0
            ObjectValueID = getObjectsIDvalueList[getCountsObject]
        else:
            ObjectValueID=getObjectsIDvalueList[getCountsObject]
        print("Object",ObjectValueID)
        ##Get  the images with that specific object ID
        ApiRequestImage=requests.get('https://collectionapi.metmuseum.org/public/collection/v1/objects/'+str(ObjectValueID))
        #print(ApiRequestImage.json())
        saveResponse=ApiRequestImage.json()
        print(saveResponse)
        ##Save that image
        getImage=saveResponse["primaryImage"]
        print("res",getImage)
        ##Save the Data against that Image
        department=saveResponse["department"]
        object_name=saveResponse["objectName"]
        culture=saveResponse["culture"]
        Artist_name=saveResponse["artistDisplayName"]
        repository=saveResponse["repository"]
        ###Change template text dynamically according to the Response
        html_message=render_to_string('TextDetails.html',{'department':department,'object_name':object_name,'culture':culture,'Artist_name':Artist_name,'repository':repository})
        if request.is_ajax():
            ##Return ajax Response
            return JsonResponse({'image':getImage,'html_message':html_message})
        else:
            return render(request,"index.html",{'image':getImage})
    except Exception as ex:
        getImage="No Image Found"
        return render(request, "index.html", {'image': getImage})
