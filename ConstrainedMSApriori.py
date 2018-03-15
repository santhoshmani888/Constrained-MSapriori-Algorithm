'''
Authors:  Santhosh Mani
Email:  smani6@uic.edu
Date: Feb-20-2018
'''
### Import Statements
import itertools
import re

### Different modules to perform specific task
## Module to read the input-data and parameter files
def inputfile(data,parameter):
    with open(data,"r") as f:
        lines = f.read().splitlines()
        i=0
        for each in lines:
            lines[i] = lines[i].replace('{', '')
            lines[i] = lines[i].replace('}', '')
            lines[i] = lines[i].split(', ')
            i=i+1
        n = i;

    with open(parameter,"r") as p:
        parameter_line = p.read().splitlines()
        for i in parameter_line:
            #Regex to get MIS and digits
            listmis = re.findall(r'^MIS.*\d*\.\d+$',i)
            if listmis:
                temp_list = re.findall(r'\d*\.\d+|\d+',str(listmis))
                temp_dict = {temp_list[0] : float(temp_list[1])}
                mis.update(temp_dict)
                
            if i[:3] == "SDC":
                sdc = i.split(" = ")
                sdc = float(sdc[1])
            
            if "must-have" in i:
                must_have = i.strip()
                must_have = must_have.split(": ")
                must_have = must_have[1].split(" or ")

            if "cannot_be_together" in i:
                pair = i.strip()
                pair = pair.split(": ")[1]
                pair= re.findall("\d+",str(i))
                not_together.append(pair)
    return lines, mis, must_have, sdc, not_together, n

## Module to create a list of items according to their MIS values
def sort_key(joined_dict):
    joined_list = [[k,v] for k, v in joined_dict.items()]
    joined_list.sort(key=lambda pair: pair[1][0])
    return joined_list

## Module to get MIS value of an element in mis_list 
def find_mis(element, mis_list):
    for i in range(len(mis_list)):
        if element in mis_list[i]:
            mis = mis_list[i][1]
            break
    return mis

## Module to get support value of an element in support_list
def count_sup(element, support_list):
    for i in range(len(support_list)):
        if element[0] in support_list[i]:
            support = support_list[i][1]
            break
    return support
    
## Module to generate level2_candidates
def C2gen(joined_list, l):
    level2_candidate_list = []
    for j in range(len(joined_list)):
        if joined_list[j][0] in l and joined_list[j][1][1] >= joined_list[j][1][0]:
            for i in range(j+1, len(joined_list)):
                if joined_list[i][1][1] >= joined_list[j][1][0] and abs(joined_list[i][1][1] - joined_list[j][1][1]) <= sdc:
                    temp = []
                    temp.append(joined_list[j][0])
                    temp.append(joined_list[i][0])
                    level2_candidate_list.append(temp)
    return level2_candidate_list

    
## Module to generate candidates for values of k greater than 2
def Ckgen(ftemp, mis_list, support_list):
    freqlist,freqjoin = [],[]    
    for i in range(len(ftemp)):
        f1 = ftemp[i][0:(len(ftemp[i])-1)]
        for j in range(i+1, len(ftemp)):
            f2 = ftemp[j][0:(len(ftemp[j])-1)]
            if f1==f2 and abs(count_sup(ftemp[j][(len(ftemp[j])-1):],support_list)-count_sup(ftemp[i][(len(ftemp[i])-1):],support_list))<=sdc:
                freqjoin = ftemp[i] + ftemp[j][(len(ftemp[j])-1):]
                freqlist.append(freqjoin)
                freqjoin = []
    i = 0
    while i < len(freqlist):
		# finding all combination of subset
        subsets = list(set(itertools.combinations(freqlist[i], len(freqlist[i])-1)))
        for subset in subsets:
            if (freqlist[i][0] in subset) or (find_mis(freqlist[i][0], mis_list) == find_mis(freqlist[i][1], mis_list)):
                ftcounter = 0
                for ft in ftemp:
                    if list(subset) == list(ft):
                        ftcounter = ftcounter + 1
                        break
                if ftcounter == 0:
                    freqlist.pop(i)
                    i = i - 1
                    break
            if i == len(freqlist):
                break
        i = i + 1
    return(freqlist)

## Module to clean extra blank lines present at the send from the output-data file
def clean_file(filename):
    # check if the line can be deleted
    def is_all_whitespace(line):
        for char in line:
            if char != ' ' and char != '\n':
                return False
        return True

    # generates the new lines
    with open(filename, 'r') as file:
        file_out = []
        for line in file:
            if is_all_whitespace(line):
                line = '\n'
            file_out.append(line)

    # removes whitespaces at the end of file
    while file_out[-1] == '\n':  # while the last item in lst is blank
        file_out.pop(-1)  # removes last element
    file_out[-1] = file_out[-1].strip('\n')
    
    # writes the new the output to file
    with open(filename, 'w') as file:
        file.write(''.join(file_out))
        
#############################################################################################################################################################
### Program flow starts from here
## Reading files and storing the data required for MSApriori Algorithm
not_together=[]
support = {}
count = 0
mis={}
sdc = 0.0
lines, mis, must_have, sdc, not_together, n = inputfile("input-data.txt","parameter-file.txt")
## Creating a dictionary and then a list containing items and their mis and support values
## Creating two different lists. One with items and their MIS values only and another one with items and their Support values only
## Finding the support for all the items in transaction
for key in mis:
    for transaction in lines:
        if key in transaction:
                count = count + 1
    support[key] = round(count/len(lines),2)
    count = 0
    
joined_dict = dict([(k,[mis[k],support[k]]) for k in mis])
mis_list = [[k,v] for k, v in mis.items()]
support_list = [[k,v] for k, v in support.items()]
#############################################################################################################################################################
## Algorithm Starts Here
## Sorting the list based on MIS values
joined_list = sort_key(joined_dict)


## Finding L and F1 Values after initial pass
l,f = [],[]
f1,f2,f3 = [],[],[]

flag = -1
for i in range(len(joined_list)):
    firstelement=joined_list[i][1][0]
    if float(joined_list[i][1][1]) >= float(firstelement):
        flag = i
        break

for i in range(len(joined_list)):
    if float(joined_list[i][1][1]) >= float(joined_list[i][1][0]):
        f1.append(joined_list[i][0])
    if flag >= 0:
        if float(joined_list[i][1][1]) >= float(joined_list[flag][1][0]):
            l.append(joined_list[i][0])


i = 0
## Applying 'must_have' constraints and removing from F1
if must_have == []:
    pass #Do Nothing
else:
    while i < len(f1):
        if f1[i] in must_have:
            pass  #Do Nothing
        else:
            f1.pop(i)
            i = i - 1
        i = i + 1

for f1_item in f1:
    count = 0
    for transaction in lines:
        if f1_item in transaction:
            count = count + 1
    f2.append([f1_item,count])
f.append(f2)

## Outermost For-Loop in MSApriori Algorithm is implemented using While-Loop below:
k = 2
ftemp = []
while(k == 2 or len(ftemp) > 1):
    if k == 2:
        c = C2gen(joined_list, l)
    else:
        c = Ckgen(ftemp, mis_list, support_list)

    # Checking subset count
    count,temp_mis = 0,0
    ffinal,ftemp,freqcount = [],[],[]
    for can_list in c:
        for transaction in lines:
            if set(can_list) < set(transaction):
                count = count + 1
        for i in range(len(mis_list)):
            if can_list[0] in mis_list[i]:
                temp_mis = mis_list[i][1]
                break
        if count/len(lines) >= temp_mis:
            ftemp.append(can_list)
            freqcount.append([can_list,count])
        count = 0
    
    # Applying 'can_not_be_together' constraint for frequent items
    if not_together == []:
        pass
    else:
        i=0
        while i < len(ftemp):
            for r in not_together:
                if(set(r) <= set(ftemp[i])):
                    ftemp.pop(i)
                    freqcount.pop(i)
                    i = i - 1
                    break
            i = i + 1
    # Generating frequent set with tail count
    count = 0
    freqtail = []
    ftemp0 = freqcount
    for ft1 in ftemp0:
        ftemp2 = ft1[0][1:]
        ftemp3 = []
        for transaction in lines:
            if set(ftemp2) < set(transaction):
                count = count + 1
        ftemp3.append(ft1)
        ftemp3.append(count)
        freqtail.append(ftemp3)
        count = 0
    
    if(len(freqtail) > 0):
        f.append(freqtail)
    
    # Applying 'must_have' constraint for frequent items
    j = 0
    if must_have == []:
        pass
    else:
        for i in range(len(f)):
            if i == 0:
                pass
            else:
                while j < len(f[i]):
                    counter = 0
                    for subset in must_have:
                        if str(subset) in f[i][j][0][0]:
                            counter = 1
                            break
                    if counter == 0:
                        f[i].pop(j)
                        j = j - 1
                    j = j + 1
    k = k + 1
    
## Algorithm Ends Here
#############################################################################################################################################################
## Code for writing in the output-data.txt file the result obtained in the required format starts from next line
i = 0
with open("output-data.txt","w+") as op:

    while(i<len(f)):
        op.write('Frequent '+str(i+1)+'-itemsets\n')
        op.write('\n')
        if i == 0:
            j = 0
            while j < len(f[i]):
                op.write('\t'+str(f[i][j][1])+' : {'+str(f[i][j][0])+'}\n')
                j = j + 1
        else:
            j = 0
            while j < len(f[i]):
                op.write('\t'+str(f[i][j][0][1])+' : {'+str(f[i][j][0][0]).replace("[","").replace("]","").replace("'","")+'}\n')
                op.write('Tail count = '+str(f[i][j][1])+'\n')
                j = j + 1
        op.write('\n\tTotal number of frequent '+str(i+1)+'-itemsets = '+str(len(f[i]))+'\n\n\n')
        i = i + 1
clean_file('output-data.txt')
print("Please open output-data.txt file from the current working directory and compare the result")
### End of Project/Program
### Please open output-data.txt file from the current working directory and compare the result
#############################################################################################################################################################