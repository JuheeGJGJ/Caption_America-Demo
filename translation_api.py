import os
import sys
import json
import urllib.request
import csv
#from google.cloud import translate_v2 as translate
#from googletrans import Translator

client_id = []
client_secret = []

def main():
    mode = input ('1 if papago 2 if google 3 if input : ')
    if mode == '1':
        papago()
    elif mode == '2':
        google()
    elif mode == '3' : #input string by user
        string = input ('input string : ')
        print (papagoEngToKo(string))
    else :
        print ('mode ' + mode + ' is wrong')

def papago () :
    print("papago")

    f = open ('caption.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)

    out = open ('result.csv', 'w', newline ='')
    wr = csv.writer (out)

    i = 0
    for line in rdr :
        try :
           wr.writerow([line[0], papagoEngToKo(line[0], i)])
        except : # papago 제한 수 초과
            i = i + 1
            print (i)
            wr.writerow([line[0], papagoEngToKo(line[0], i)])

    f.close()
    out.close()


def google() :
    print ("google")

    f = open ('caption.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)

    out = open ('result.csv', 'w', newline ='')
    wr = csv.writer (out)

    #r = list (rdr)
    #for i in range (49, 161) :
       # wr.writerow([r[i][0], googleEngToKo(r[i][0]).replace('\u200b', "")])
    #   except :
    #       wr.writerow([r[i][0], 'error'])
     #      print ('error')

#    i = 0;
 #   for line in rdr :
  #      i = i+1
   #     try:
    #        wr.writerow([line[0], googleEngToKo(line[0]).replace('\u200b', "")])
     #       print (i)
      #  except :
       #     wr.writerow([line[0], 'error'])
        #    print ('error')

    f.close()
    out.close()


def googleEngToKo (string) :
    translator = Translator()
    result = translator.translate(string, dest="ko")
    return (result.text)

def papagoEngToKo (string, i) :
    encText = urllib.parse.quote(string)
    data = "source=en&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id[i])
    request.add_header("X-Naver-Client-Secret",client_secret[i])
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read().decode ('utf-8')
        result = json.loads (response_body)
        return result['message']['result']['translatedText']
    else:
        return "Error Code:" + rescode

if __name__ == "__main__":
    main()