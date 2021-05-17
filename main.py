import sys
import os
import os.path
import time
import schedule
import json

from fontmeta import FontMeta

import openapi_client
from openapi_client.api import default_api
from openapi_client.model.font import Font

metaRecordPath = 'meta_record.json'

configuration = openapi_client.Configuration(
        host='http://172.17.0.2'
)

font_user = 'apiuser'


def getFontDirs():
    """Returns a list of directories in which fonts may exist"""

    res = []
    if(sys.platform.startswith('linux')):
        res = ['/usr/share/fonts', '~/fonts']
    elif(sys.platform.startswith('win32')):
        res = ['C:\\Windows\\Fonts']
    elif(sys.platform.startswith('darwin')):
        res = ['~/Library/Fonts']

    return list(filter(os.path.isdir, res))


def getFontPaths():
    """Returns a list of paths to fonts existing in system folders"""

    for fontDir in getFontDirs():
        for dirPath, subDirNames, fileNames in os.walk(fontDir):
            for fileName in fileNames:
                filePath = os.path.join(dirPath, fileName)
                if(os.path.isfile(filePath)):
                    root, ext = os.path.splitext(fileName)
                    if(ext in ['.otf', '.ttf']):
                        yield filePath


def getCurrentMeta():
    """Returns a dict containing font metadata in a {fontPath: fontMeta} format"""

    fontsMeta = {}
    for fontPath in getFontPaths():
        fontsMeta[fontPath] = FontMeta(fontPath).get_data()

    return fontsMeta


def readMetaRecord():
    try:

        with open(metaRecordPath, 'r') as f:
            return json.load(f)

    except OSError:

        return {}


def updateMetaRecord(newMeta):
    
    with open(metaRecordPath, 'w') as f:
        json.dump(newMeta, f)


validMetaKeys = list(Font.attribute_map.keys())
validMetaKeys.remove('user_name')
validMetaKeys.remove('font_path')


def getPrepMeta(meta, user, path):
    newMeta = {key: meta.get(key, '') for key in validMetaKeys}

    return Font(user_name=user, font_path=path, **newMeta)


def reportChanges():
    """Check for changes in all font metadata and report accordingly"""

    oldMeta = readMetaRecord()
    newMeta = getCurrentMeta()

    with openapi_client.ApiClient(configuration) as apiClient:

        apiInstance = default_api.DefaultApi(apiClient)

        validKeys = Font.attribute_map.keys()

        if(oldMeta != newMeta):
            print("Meta has changed!")

            oldPaths = set(oldMeta.keys())
            newPaths = set(newMeta.keys())

            for addedPath in newPaths - oldPaths:

                print(f"File '{addedPath}' has been added!")

                cMeta = newMeta[addedPath]
                font = getPrepMeta(cMeta, font_user, addedPath)

                try:
                    apiResponse = apiInstance.create_font_font_post(font)
                    #print(apiResponse)
                except openapi_client.exceptions.ApiException as e:
                    print(e.body)

            for removedPath in oldPaths - newPaths:
                print(f"File '{removedPath}' has been removed!")

                cMeta = newMeta[removedPath]
                font = getPrepMeta(cMeta, font_user, removedPath)
                
                try:
                    apiResponse = apiInstance.remove_font_font_delete(font)
                except openapi_client.exceptions.ApiException as e:
                    print(e.body)

            for samePath in newPaths & oldPaths:
                if(oldMeta[samePath] != newMeta[samePath]):
                    print(f"File '{samePath}' has been modified!")

                    cMeta = newMeta[samePath]
                    font = getPrepMeta(cMeta, font_user, samePath)

                    try:
                        apiResponse = apiInstance.update_font_font_put(font)
                    except openapi_client.exceptions.ApiException as e:
                        print(e.body)

            updateMetaRecord(newMeta)


def reportAll():
    """Report full account of all font metadata"""

    print("Reporting all!")

    cMetas = getCurrentMeta()

    # Talk to REST API

    res = []
    for path, cMeta in cMetas.items():
        res.append(getPrepMeta(cMeta, font_user, path))

    with openapi_client.ApiClient(configuration) as apiClient:
        
        apiInstance = default_api.DefaultApi(apiClient)
        
        try:
            apiInstance.upsert_fonts_fonts_upsert_post(res)
        except openapi_client.exceptions.ApiException as e:
            print(e.body)


    updateMetaRecord(cMetas)
    

def main():
    
    print(getFontDirs())

    schedule.every(5).seconds.do(reportChanges)
    schedule.every(30).seconds.do(reportAll)

    while True:
        schedule.run_pending()
        time.sleep(1)
 

if(__name__ == '__main__'):
    main()

