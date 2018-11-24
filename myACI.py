#!/usr/bin/python
import json
import requests
import getpass

ip = raw_input("APIC IP: ")
user = raw_input("APIC USER: ")
password = getpass.getpass("APIC PASSWORD: ")

#ip = "sandboxapicdc.cisco.com"
#user = "admin"
#password = "ciscopsdt"

url = "https://"+ip+"/api/aaaLogin.json"
payload = "{ \"aaaUser\" : { \"attributes\": {\"name\":\"admin\",\"pwd\":\"ciscopsdt\" } } } "
headers = {'cache-control': "no-cache"}
requests.packages.urllib3.disable_warnings()
response = requests.request("POST", url, data=payload, headers=headers, verify=False)
auth = json.loads(response.text)
login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
auth_token = login_attributes['token']
cookies = {}
cookies['APIC-Cookie'] = auth_token

def getTenants():
    '''
    GET ALL TENANTS
    '''
    url = "https://"+ip+"/api/node/class/fvTenant.json"
    response = requests.request("GET", url, data=payload, headers=headers, verify=False,cookies=cookies)
    tenants = []
    for element in response.json().get("imdata"):
        fvTenant = element.get("fvTenant").get("attributes").get("name")
        tenants.append(fvTenant)
    return tenants

def getEPG(tenantName):

    url = "https://"+ip+"/api/node/mo/uni/tn-"+tenantName+".json?rsp-subtree=full"
    response = requests.request("GET", url, data=payload, headers=headers, verify=False,cookies=cookies)
    #response.text
    j = response.json()
    # print EPG list
    for e in j.get("imdata")[0].get("fvTenant").get("children"):
        tnFvBDName = ""
        fvAEPgName = ""
        fvApName = ""
        if e.get("fvAp"):
            fvAp = e.get("fvAp")
            fvApName = fvAp.get("attributes").get("name")
            if fvAp.get("children"):
                for children in fvAp.get("children"):
                    if children.get("fvAEPg"):
                        fvAEPg = children.get("fvAEPg")
                        fvAEPgName = fvAEPg.get("attributes").get("name")
                        for c in fvAEPg.get("children"):
                            if c.get("fvRsBd"):
                                tnFvBDName = c.get("fvRsBd").get("attributes").get("tnFvBDName")
            print('fvTenant: {:30} fvAp name: {:30} fvAEPg: {:30} tnFvBDName: {}').format(tenantName,fvApName,fvAEPgName,tnFvBDName)

def getBD(tenantName):
    url = "https://"+ip+"/api/node/mo/uni/tn-"+tenantName+".json?rsp-subtree=full"
    response = requests.request("GET", url, data=payload, headers=headers, verify=False,cookies=cookies)
    #response.text
    j = response.json()
    # print BD list
    for e in j.get("imdata")[0].get("fvTenant").get("children"):
        fvBDName = ""
        subnet=""   
        if e.get("fvBD"):
            fvBD = e.get("fvBD")
            fvBDName = fvBD.get("attributes").get("name")
            for children in fvBD.get("children"):     
                if children.get("fvSubnet"):
                    subnet = children.get("fvSubnet").get("attributes").get("ip")
                    print('fvBD name: {:30} subnet: {}').format(fvBDName,subnet)
            if not subnet:
                print('fvTenant: {:30} fvBD name: {:30} subnet: {:30}').format(tenantName,fvBDName,subnet)

def main():
    #connect()
    tenants=getTenants()
    for tenant in tenants:
        getEPG(tenant)
        getBD(tenant)

main()