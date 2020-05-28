"""
Nicholas Alderman
Countries Project - uses countriesClass
"""

import countriesClass as cc


search = cc.countrySearch('https://en.wikipedia.org/wiki/List_of_sovereign_states')

in1 = input("Enter the first letter of desired country, or type in name of country: ")
if (len(in1) == 1):
    search.letterSearchClass(in1)
    print(search.searchDf)
    name = input("Enter the index of desired country, or type in name of country: ")
    search.getNameClass(int(name))
else:
    in2 = search.df[search.df['Country'].str.match(in1)].reset_index()
    in3 = str(in2.iloc[0][1])
    search.getNameClass(in3)
search.processResultClass()

search.saveImageClass()

