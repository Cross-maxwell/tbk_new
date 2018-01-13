import sys
sys.path.append('/home/new_taobaoke/taobaoke')
import os
os.environ.update({"DJANGO_SETTINGS_MODULE": "fuli.settings"})
import django
django.setup()

from broadcast.models.user_models import JDAdzone
import requests

url = 'https://media.jd.com/gotoadv/selectProMediaType'
cookie = 'shshshfpa=d3b60fed-4440-80ea-6726-99b17daa3f66-1515377069; TrackerID=j85qtJ0zzsPR825QvqbejAMsNFCtHzh4p0n6CG223cvzU6AKIWzpmefeRBcCAp57jpMWGc1NQWnVPjXUGzL8gmw3V_Hfgcb0J_uJ6GoUiJA; pt_key=AAFaUtJNADBOSI2zE91YvQDhivD8iG2Smamo-1CvnfuhNXTS93X4T-UnBt-6qBUsmqizpbfeIOA; pt_pin=maxwell119; pt_token=zc83r9p5; pwdt_id=maxwell119; webp=1; sc_width=1920; visitkey=45186441903526501; wq_logid=1515377492_1804289383; retina=0; cid=9; __wga=1515377492471.1515377253095.1515377253095.1515377253095.2.1; shshshfp=53d23b68f1a5a06c182a4b44c9130bc8; shshshfpb=1f0cbf30bfc6c442eb435c54a9a51238a875f530b33fbc4615a52d1aec; wq_ufc=5c249006b10b9084a5cf579332d3f4dc; mobilev=html5; PCSYCityID=1607; user-key=dcdc3c20-a25c-43a6-99fd-b0172019cfb6; ssid="MNRIkjeYTcCn5mmx/IuykQ=="; masterClose=yes; showNoticeWindow=false; mt_xid=V2_52007VwUbVVxdU1gWSCkPDWELFQJfDE4PT08bQAAzVxNODl9UDgNNG1xQZgYWAgkMUA4vShhcDHsCEk5dWUNaGUIcXQ5jBSJQbVtiXhxPGVkCVwMWUw%3D%3D; wlfstk_smdl=v9ye46m8npln674knii3si3250yc8i14; _jrda=3; TrackID=1gDWfW2tPUVvdoTgKRM4EGsM-FMoQdcvmklykFoUCkkhkn_E6oBcgoXxZAijurtJrgJRxRHbPXdZoyOFHZiZIGaGFgrB6fAj10KEPllNd-7Y; pinId=w3pIVJCCxt3L47_FLDR6Sg; pin=maxwell119; unick=maxwell119; _tp=ZHTcbon0qrgTlRgFhXG%2BtQ%3D%3D; _pst=maxwell119; ceshi3.com=000; areaId=19; ipLocation=%u5e7f%u4e1c; ipLoc-djd=19-1607-3155-0.477680949; unpl=V2_ZzNtbRVQRh0iC0ZRfUsMAGIAQVgSUhEQcFtEAH8fDgdjAEVZclRCFXwUR1RnGVwUZwIZWUpcQhZFCEZkexhdBGMDEVpKVXMldQlHVXoYVQBiBiJeQmdDJXMBQVV%2bGF4MZjMiXUdUcxV9CU5TcxxbAWYCIgYXOURCcF1GAX0dVVczVEFtQ2dCJXQ4Bzp8G14NYAFfW0tQQhB0Ck9VSxhsBg%3d%3d; CCC_SE=ADC_QDgnQzeSD3r%2b01kP0oWMxs%2bPc9pvx8TbOPn8iR6cHhb4rM03IBTIxQ0UNtRLT%2fQ4iRVMZQsoqcRqbU7JEIAuy5UZUqMVQdYzNnZu6z2gA%2bAopUevihrAx0gJO%2blVE8rveUcDPFjZNDPPYAX0JMrLbyX2pKKRgokgwJCZrJ0p5PRdRS5dI1iLPfkz0A0p6cX7Qb209DKZeOw3YORCcTYTQFmguvwEMD0XxopV5As%2f8t2Dk5Jg25DB%2b4E8cgpTPvKjLY%2bIeHPrwFPpX5O4GOLgivmBXBVdkKMac57U8bdo8Y2VTtvZsTZdGsC4hKy8%2fXLyK2QvU%2fdXGyCsOIT70jabyMbkvD75reR7FGzg0JFOW8owLUL8JXYvmRwVQZdVP3061%2boRudFvO42qB9rBZ%2f3LGyZmNw%2bro4ZnVMLyo%2bZE3sKK6yEfxlkRK147ZU43jfEiWfnAVLDgEf06dRI%2fwqVfpJi2r1IxdpXJOeehMfNebfsBhssw3mkUMk%2fITmI0wlkJoIwccQG9QmCIodv0%2fJtaArtOboAfm7aL6Nbav2VClVLhqC73BVEsyYaB0WsDboIiNzt7KIhul%2fCSOP6o3OXIq2ch2iFkyKspiphqNbN6eRCxzuqc9ZV%2beE1wmi5GcmGtxfyhrQthOEi%2bjlgKF3yTJQ%3d%3d; __jdv=108460702|wx.qq.com|t_1000512693_|tuiguang|f649f2147ca442b4a4c44b3e57c352f5|1515639543012; mba_muid=786040380; cn=1; thor=0CD4A79A19A4113628050B1064DDC2C34BB51C07F974D2833CA53D4470234A513399ABF991D8BC2137501048ECC4F456BC7DBB32D9E010C33398CA3D885884BED396A0DE7D46CBCD1ED88570595B1AE3693BB73AF0373A97C089113D73851776064D62C5A6391556CC5B605235FDC80A003F04D41DB7E2A7F17BF8195FC9BB13E1E0E395F24B9F6629EF956C5449309B; 3AB9D23F7A4B3C9B=F4WH6HFC4JHNSVFJ3HI3BU7S4CRA6YOGQ4APJGGUMQDAF3DFXJSDVM3NR42XIYPZQJNDM6VSVUOSKOQ3O6VV4X4Q4E; __jda=108460702.786040380.1510053754.1515724147.1515726637.26; __jdb=108460702.5.786040380|26.1515726637; __jdc=108460702; __jdu=786040380'
form_data = {
    'id':0,
    'type' : 4,
    'status' : 1
}

resp = requests.post(url, data=form_data, headers={'Cookie':cookie}).json()['promotionSite']
created_num = 0
updated_num = 0
for i in resp:
    jda_dict = {
        'pid' : i['id'],
        'jdadzone_name' : i['spaceName']
    }
    jda, created = JDAdzone.objects.update_or_create(pid=i['id'], defaults=jda_dict)
    if created:
        created_num += 1
    else: updated_num += 1

print "{0} Updated, {1} Created.".format(updated_num, created_num)