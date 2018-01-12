# coding: utf-8
import requests
cookie = 'shshshfpa=d3b60fed-4440-80ea-6726-99b17daa3f66-1515377069; TrackerID=j85qtJ0zzsPR825QvqbejAMsNFCtHzh4p0n6CG223cvzU6AKIWzpmefeRBcCAp57jpMWGc1NQWnVPjXUGzL8gmw3V_Hfgcb0J_uJ6GoUiJA; pt_key=AAFaUtJNADBOSI2zE91YvQDhivD8iG2Smamo-1CvnfuhNXTS93X4T-UnBt-6qBUsmqizpbfeIOA; pt_pin=maxwell119; pt_token=zc83r9p5; pwdt_id=maxwell119; webp=1; sc_width=1920; visitkey=45186441903526501; wq_logid=1515377492_1804289383; retina=0; cid=9; __wga=1515377492471.1515377253095.1515377253095.1515377253095.2.1; PPRD_P=UUID.786040380; shshshfp=53d23b68f1a5a06c182a4b44c9130bc8; shshshfpb=1f0cbf30bfc6c442eb435c54a9a51238a875f530b33fbc4615a52d1aec; wq_ufc=5c249006b10b9084a5cf579332d3f4dc; mobilev=html5; unpl=V2_ZzNtbRdRRhd9DUZXeBBbAmIHRg0RUUEQIg9OAHNLDFdhVEdZclRCFXwUR1RnGFUUZwYZXkBcQBxFCEZkexhdBGMDEVpKVXMldQlHVXoYVQBiBiJeQmdDJXMBQVV%2bGF4MZjMiXUdUcxV1C0dUfBxUB28CIgYXOURCcF1GAX0dVVczVEFtQ2dCJXQ4Bzp4GFUGbgtfW0tQQhB0Ck9VSxhsBg%3d%3d; __jdv=108460702|other_x_short|t_1000512693_|tuiguang|d7439412286645eab734f69e9cac7fd5|1515392608517; mba_muid=786040380; PCSYCityID=1607; user-key=dcdc3c20-a25c-43a6-99fd-b0172019cfb6; cn=1; ssid="MNRIkjeYTcCn5mmx/IuykQ=="; wlfstk_smdl=kke1ypyrsm34mp7m4n4o8nts9v7u8wcs; _jrda=2; 3AB9D23F7A4B3C9B=F4WH6HFC4JHNSVFJ3HI3BU7S4CRA6YOGQ4APJGGUMQDAF3DFXJSDVM3NR42XIYPZQJNDM6VSVUOSKOQ3O6VV4X4Q4E; TrackID=1gfnm-poSougA-DpNIhkNn5Siw-q2ekknon8agMzb3TacHli83RA9N_h3BSQ4H_28-CZCjxqYp3w6vvVTyNhQIOw1wKS-SNK1wxMpWvpZ978; pinId=w3pIVJCCxt3L47_FLDR6Sg; _tp=ZHTcbon0qrgTlRgFhXG%2BtQ%3D%3D; logining=1; _pst=maxwell119; ceshi3.com=000; thor=4BB677CFAB93B02296B0AC44CAAC092F327539CEDCFC5D827CAE5844719AF97D090107763ACA27A0011F97A655F2B079082E8E5E506A72C903AA7D7FA2B5D92870DBFA7BA642E0D1E7A46CBE8D3895602AB0F81276E31178C123BDA5FDB1EE535C1B9372738324E9006E4687D348165BC41B7AF69934DBA50F32E6D5F0B4D830B4431B333EA3E51248AD9D4A68592036; pin=maxwell119; unick=maxwell119; masterClose=yes; showNoticeWindow=false; __jda=108460702.786040380.1510053754.1515485973.1515552990.15; __jdb=108460702.7.786040380|15.1515552990; __jdc=108460702; __jdu=786040380'
form_data = {
    'adtType' : '31',
    'siteName' : '-1',
    'unionWebId' : '-1',
    'protocol' : '2',
    'codeType' : '2',
    'type' : '2',
    'positionId' : '0',
    'sizeId' : '-1',
    'logSizeName' : '-1',
    'unionAppId' : '-1',
    'unionMediaId' : '-1',
    'logTitle' : 'Anytime银首饰品s925女士镶闪钻锆石皇冠时尚百搭耳钉耳饰女一对0265',
    'imgUrl' : 'http://img14.360buyimg.com/n1/jfs/t5632/213/4138807937/179937/3f9a9b7b/59487ec0N59347d0c.jpg',
    'logUnitPrice' : '160.00',
    'wareUrl' : 'http://item.jd.com/1010954017.html',
    'materialType' : '1',
    'actId' : '1010954017',
    'couponLink' : 'http://coupon.jd.com/ilink/couponSendFront/send_index.action?key##0b37cffdf78746649fc8a83bbcd88eac&roleId##9398833&to##anytime.jd.com',
    'orienPlanId' : '-1',
    'landingPageType' : '-1',
    'PopId' : '26386',
    'materialId' : '1010954017',
    'adOwner' : 'p_26386',
    'skuIdList' : '1010954017',
    'planId' : '25779',
    'category' : 'Anytime珠宝官方旗舰店',
    'saler' : '1',
    'logCommissionRate' : '80.00',
    'requestId' : 's_1515553400726_1000512693###st3###kt0###13c1b27d-d5fb-4e27-a8b9-98f7696db945',
    'isApp' : '-1',
}

url = 'https://media.jd.com/gotoadv/getCustomCodeURL'
for i in range(1, 2001):
    form_data.update({'positionName':'jd{}'.format(i)})
    resp = requests.post(url, data=form_data, headers={'Cookie': cookie})
    print resp.json()['showMsg']


