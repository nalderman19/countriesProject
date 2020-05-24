"""
Nicholas Alderman
Countries Project - scrape wikipedia data into dataframe
"""


import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

class countrySearch:
    # instance methods
    def __init__(self, url):
        self.df = self.initDataframe(url)

    def letterSearchClass(self, letter):
        self.searchDf = self.letterSearch(self.df, letter)

    def getNameClass(self, frame, index):
        self.name = self.getName(frame, index)

    def getInfoClass(self, name):
        self.info = self.getInfo(name)

    def processResultClass(self, frame):
        self.prcResult = self.processResult(frame)

    # static methods
    @staticmethod
    def initDataframe(url):
        r = requests.get(url).text
        soup = bs(r,'lxml')
        table = soup.find('table',{'class':'sortable wikitable'})
        # get every fourth <td> cell so there are only names of countries, delete headers and footers
        elements = table.findAll('span')
        del elements[0:9]
        del elements[len(elements):len(elements)-11:-1]
        # get names from each cell
        countries = []
        for e in elements:
            eT = e.get('id')
            if (eT != None and eT != "Other_states"):
                eT2 = eT.replace('_',' ')
                countries.append(eT2)
        # sort by name and generate pandas dataframe
        countries = sorted(countries)
        df = pd.DataFrame()
        df['Country'] = countries
        return df

    @staticmethod
    # Primitive search using first letter of country
    # get index of first and last appearances of searched letter
    def letterSearch(frame, letter):
        L = letter.capitalize()
        minIdx = 0
        maxIdx = 0
        # iterate through dataframe and stop when searched char is found
        for i in range(0, len(frame)):
            if (frame.iloc[i]['Country'].startswith(str(L))):
                minIdx = i # first appearance
                break
        maxIdx = minIdx
        # iterate through dataframe and stop when next letter is found
        while (frame.iloc[maxIdx]['Country'].startswith(str(L))):
            maxIdx = maxIdx+1
            if (maxIdx == len(frame)):
                break

        # return smaller dataframe consisting of query
        search = frame[minIdx:maxIdx]['Country'].values.tolist()
        dfS = pd.DataFrame()
        dfS['Country'] = search
        return dfS

    @staticmethod
    def getName(frame, index):
        try:
            name = frame.at[index,'Country']
        except:
            print("Index out of bounds")
        return name

    @staticmethod
    def getInfo(name):
        name = name.replace(" ","_")
        url = 'https://en.wikipedia.org/wiki/'+name
        print(url)
        req = requests.get(url).text
        sp = bs(req, 'lxml')
        countryTable = sp.find('table',{'class':'infobox geography vcard'})
        infoHeaders = countryTable.findAll('th',{'scope':'row'})
        infoData = countryTable.findAll('td',colspan=False)
        # headers of each row
        infoH = []
        for e in infoHeaders:
            if (e.text != None):
                infoH.append(e.text)
        # info of each row
        info = []
        for i in infoData:
            if (i.text != None):
                info.append(i.text)

        dfInfo = pd.DataFrame({'Stat':infoH})
        dfData = pd.DataFrame({'Info':info})
        src = pd.concat([dfInfo,dfData], axis=1, sort=False)
        return src

    @staticmethod
    def processResult(frame):
        print("Processing...")
        tdf = frame.copy()
        # only care about stuff after capital
        tdf = countrySearch.removeUntilCapital(tdf)
        tdf.reset_index()
        # fix spaces and footnotes for each cell under Info
        for i in range(len(tdf)):
            tdf.iloc[i]['Info'] = countrySearch.fixFootnotes(tdf.iloc[i]['Info'])
            tdf.iloc[i]['Info'] = countrySearch.fixSpaces(tdf.iloc[i]['Info'])

        tdf = countrySearch.fixCities(tdf)
        return tdf

    @staticmethod
    def removeUntilCapital(frame): # if first element isnt 'Capital': remove it and check again
        df = frame.copy()
        if (df.iloc[0]['Stat'].startswith('Capital') == False):
            df = df[1:]
            return countrySearch.removeUntilCapital(df)
        df.index = range(len(df.index))
        return df

    @staticmethod
    def fixSpaces(string): # fixes spaces where necessary and checks again
        string = string.replace(u'\xa0',u' ')
        #string = string.replace(u'\"',chr(96))
        for i,l in enumerate(string):
            if (i != len(string)-1):
                # remove double spaces
                if (string[i] == ' ' and string[i+1] == ' '):
                    string = string[:i] + string[i+1:]
                    #print("Case 1 at index " + str(i))
                    return countrySearch.fixSpaces(string)
                #    (is in alphabet      &    current letter is lowercase &  next letter is uppercase)
                if ((string[i].isalpha() and string[i].isupper() == False and string[i+1].isupper())):
                    string = string[:i+1] + ', ' + string[i+1:]
                    #print("Case 2 at index " + str(i))
                    return countrySearch.fixSpaces(string)
                #  letter to number
                if (string[i].isalpha() and string[i+1].isdigit()):
                    string = string[:i+1] + ', ' + string[i+1:]
                    #print("Case 3 at index " + str(i))
                    return countrySearch.fixSpaces(string)
                # number next to letter should have space inbetween
                if (string[i].isdigit() and string[i+1].isalpha()):
                    string = string[:i+1] + ' ' + string[i+1:]
                    #print("Case 4 at index " + str(i))
                    return countrySearch.fixSpaces(string)
        return string

    @staticmethod
    def fixFootnotes(string): # finds footnote, removes it and checks again
        sLoc = string.rfind('[')
        fLoc = string.rfind(']')
        if (sLoc != -1 and fLoc != -1):
            string = string[:sLoc] + string[fLoc+1:]
            return countrySearch.fixFootnotes(string)
        else:
            return string

    @staticmethod
    def fixCities(frame):
        df = frame.copy()
        # process capital and largest city - determine if a country's capital and largest cities are different
        if (df.iloc[0]['Stat'].endswith('y')): # returns true if both are same city
            df.iloc[0]['Stat'] = "Capital" # replace incorrect header
            # now must insert largest city cell
            row  = pd.DataFrame({'Stat':"Largest City", 'Info':df.iloc[0]['Info']}, index=[1])
            df = pd.concat([df.iloc[:1], row, df.iloc[1:]]).reset_index(drop=True)
        # removing coordinates of cities
        i=0
        j=1
        for i in range(0,2):
            temp = [df.iloc[i]['Info']]
            for j in range(1,10):
                temp = temp[0].split(str(j))
            df.iloc[i]['Info'] = temp[0]
            if (df.iloc[i]['Info'].endswith(', ')):
                df.iloc[i]['Info'] = df.iloc[i]['Info'][:-2]
        return df



"""def start():
    df = initDf()
    L = input("Enter first letter of desired country: ")
    result = letterSearch(df, L)
    print("------------------------------------------\n")
    print(result)
    print("------------------------------------------\n")
    I = input("Enter index of country you would like to search: ")
    iName = getName(result, int(I))
    ins = input("You chose index " + str(I) + ", " + iName + ". \nWould you like to search? (y/n): ")
    if (ins == 'y'):
        #run request
        info = getInfo(iName)
    elif (ins == 'n'):
        start()
    else:
        ins = input("Please enter 'y' for yes and 'n' for no")

    #data = processResult(info)
    return info


#countryInfo = start()
#processedData = processResult(countryInfo)"""

first = countrySearch('https://en.wikipedia.org/wiki/List_of_sovereign_states')
second = countrySearch('https://en.wikipedia.org/wiki/List_of_sovereign_states')



