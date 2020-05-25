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

    def getNameClass(self, inp):
        if (len(str(inp)) == 1):
            self.name = self.getName(self.searchDf, inp)
        else:
            self.name=inp

    def processResultClass(self):
        self.info = self.getInfo(self.name)
        self.prcResult = self.processResult(self.info)
        cunt = pd.DataFrame({'Stat':"Country", 'Info':self.name}, index=[1])
        self.finalResult = pd.concat([cunt,self.finalInfo(self.prcResult)]).reset_index(drop=True)

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
            return None
        return name

    @staticmethod
    def getInfo(name):
        name = name.replace(" ","_")
        url = 'https://en.wikipedia.org/wiki/'+name
        print(url)
        req = requests.get(url).text
        sp = bs(req, 'lxml')
        countryTable = sp.find('table',{'class':'infobox geography vcard'})
        # infoHeaders = countryTable.findAll('th',{'scope':'row'},'th',{'colspan':'2'})
        infoHeaders = countryTable.findAll('th',{'scope':'row'})
        infoData = countryTable.findAll('td',colspan=False)
        # headers of each row
        infoH = []
        for e in infoHeaders:
            #if (e.text != None):
                infoH.append(e.text)
        # info of each row
        info = []
        for i in infoData:
            #if (i.text != None):
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
                #    (current lis in alphabet      &    current  is lowercase &  next letter is uppercase)
                if ((string[i].isalpha() and string[i].isupper() == False and string[i+1].isupper())):
                    string = string[:i+1] + ', ' + string[i+1:]
                    #print("Case 2 at index " + str(i))
                    return countrySearch.fixSpaces(string)
                #  letter to number and not km2
                if (string[i].isalpha() and string[i+1].isdigit() and string[i-1:i+2] != "km2"):
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

    @staticmethod
    def finalInfo(frame):
        # want to extract only capital, Area, Population, GDPs (pretty much manually)
        df = frame.copy()
        newdf = pd.DataFrame(columns=['Stat','Info'])
        # set capital
        newdf.loc[1] = df.loc[1]
        # find area info  using first km2
        areaIdx = []
        for i in range(len(df)):
            string = df.iloc[i]['Info']
            for j,l in enumerate(string):
                if (string[j-1:j+2] == "km2"):
                    areaIdx.append(i)
                    break
        areaDf = pd.DataFrame(columns=['Stat','Info'])
        area = pd.DataFrame({'Stat':"Area", 'Info':""}, index=[1])
        areaDf = pd.concat([area,df.iloc[areaIdx[0]:areaIdx[0]+2]]).reset_index(drop=True)
        # find GDP data
        for i in range(len(df)):
            string = df.iloc[i]['Stat']
            if ("PPP" in string):
                gdpIdx = i
                break
        gdpDf = pd.DataFrame(columns=['Stat','Info'])
        gdpDf = pd.concat([df.iloc[gdpIdx:gdpIdx+6]]).reset_index(drop=True)
        # find population data using location of gdp
        if (len(areaIdx) == 2):
            popIdx = areaIdx[0]+2
        elif (len(areaIdx) == 3):
            popIdx = areaIdx[1]+1
        else:
            popIdx = areaIdx[0]+2
        pop = pd.DataFrame({'Stat':"Population", 'Info':""}, index=[1])
        popDf = pd.concat([pop,df.iloc[popIdx:gdpIdx]]).reset_index(drop=True)

        newdf = pd.concat([newdf,areaDf,popDf,gdpDf]).reset_index(drop=True)
        return newdf
        return newdf
