import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from scipy import stats
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import operator

df = pd.read_csv("D:\Academic\Python\Splitwise_ScamGang\scam-gang_2024-01-29_export.csv")


#clean up 
list1 = ['Payment','ANG', 'Settle all balances']
dfnopayments = df[df.Category.isin(list1) == False]
dfnopayments = dfnopayments[dfnopayments.Description.isin(list1) == False]
dfclean = dfnopayments[dfnopayments.Currency.isin(list1) == False]
dfclean = dfclean.reset_index(drop=True)
dfclean['Date'] = pd.to_datetime(dfclean['Date'])

df1 = df[df.Currency.isin(list1) == False]
df1['Date'] = pd.to_datetime(df1['Date'])
df1 = df1.reset_index(drop=True)

#make list of member names
listofcoloumns = list(df.columns)
del listofcoloumns[0:5]
listofnames = listofcoloumns
listofcoloumns = list(df.columns)


#make a df for each member
personaldfs = {}

for person in listofnames:
    persondf = dfclean[['Date', 'Description', 'Category', 'Cost', 'Currency', person]].copy()
    persondf['day_difference'] = (persondf['Date'] - persondf['Date'].iloc[0]).dt.days
    persondf['Owed'] = persondf[person].cumsum()
    personaldfs[person] = persondf

# personaldfs["Abhiram"]

#make a df for each member
personaldfs1 = {}

for person in listofnames:
    persondf = df1[['Date', 'Description', 'Category', 'Cost', 'Currency', person]].copy()
    persondf['day_difference'] = (persondf['Date'] - persondf['Date'].iloc[0]).dt.days
    persondf['Owed'] = persondf[person].cumsum()
    personaldfs1[person] = persondf

# personaldfs1["Abhiram"]


#make a 'paid for' and 'borrowed' total and find total days in debt
borrowedTotals = {}
lendTotals = {}
for person in listofnames:
    sumamountlend = 0
    sumanountborrow = 0
    for amount in personaldfs[person][person]:
        if amount > 0:
            sumamountlend=sumamountlend + amount
        else:
            sumanountborrow = sumanountborrow - amount
    borrowedTotals[person] = sumanountborrow
    lendTotals[person] = sumamountlend

lendTotals
borrowedTotals
BLratio = {}
BLratio1 = {}

for person in borrowedTotals:
    if lendTotals[person] == 0:
        BLratio[person] = borrowedTotals[person]
    else:
        BLratio[person] = borrowedTotals[person]/lendTotals[person]

for person in borrowedTotals:
    if lendTotals[person] == 0:
        continue
    else:
        BLratio1[person] = round((borrowedTotals[person]/lendTotals[person]),2)


BLratio
BLratio1

dflent = pd.DataFrame(list(lendTotals.items()), columns=['Person', 'Amount Lent'])
dfborrowed = pd.DataFrame(list(borrowedTotals.items()), columns=['Person', 'Amount Borrowed'])

dfLentBorrowed = dflent.merge(dfborrowed, on='Person')
dfLentBorrowed

# Set Seaborn style
sns.set(style='whitegrid')

# Create a multi-bar graph with side-by-side bars
plt.figure(figsize=(12, 6))
bar_width = 0.35  # Width of each bar
index = np.arange(len(dfLentBorrowed))

plt.bar(index, dfLentBorrowed['Amount Lent'], bar_width, color='blue', label='Lent')
plt.bar(index + bar_width, dfLentBorrowed['Amount Borrowed'], bar_width, color='orange', label='Borrowed')

plt.xlabel('Person')
plt.ylabel('Amount')
plt.title('Comparison of Lending and Borrowing')
plt.xticks(index + bar_width / 2, dfLentBorrowed['Person'], rotation=90)
plt.legend(title='Transaction')
plt.tight_layout()
#plt.show()
plt.savefig('plot1.png', dpi=300)


#calculate credit score
creditScore = {}
for person in listofnames:
    icount = 0
    count = 0
    negpoints = 0
    score = 0
    daysSinceClear = 0
    inDebt = False
    flag = False
    for amount in personaldfs1[person]['Owed']:
        if amount < 0 and count <= 2:
            count = personaldfs1[person]['day_difference'][icount] - daysSinceClear
            flag = True
            print("{}: Index is {} Count is: {} and negpoints for this transaction are {}*{}={}".format(person,icount,count,amount,count,negpoints))
        elif amount < 0 and count > 2:
            
            inDebt = True
            count = personaldfs1[person]['day_difference'][icount] - daysSinceClear
            negpoints = count*personaldfs1[person]['Owed'][icount]
            score = score + negpoints
        else:
            inDebt = False
            flag = False
            count = 0
            daysSinceClear = personaldfs1[person]['day_difference'][icount]
        icount = icount + 1
    creditScore[person] = round(((score/1000)*BLratio[person]),2)
    print("{}: {}".format(person, score))

creditScore

sortedCreditscores = sorted(creditScore.items(), key=lambda kv: kv[1])
sortedCreditscores

type(sortedCreditscores)

dfclean



#wordcloud
text_combined = ' '.join(dfclean['Description'])

# Generate word cloud
plt.rcParams['font.sans-serif'] = ['Arial']
#font_path = r'C:\Windows\Fonts\arial.ttf'
wordcloud = WordCloud(width=800, height=400, background_color='white', font_path="./arial.ttf").generate(text_combined)

# Display the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
#plt.show()
plt.savefig('plot2.png', dpi=300)

print(creditScore)

#find average days to pay back lent amount

averagePayback = {}
for person in listofnames:
    print('\n\n\n{}\n'.format(person))
    icount = 0
    count = 0
    listofdays = []
    average = 0
    sumoflist = 0
    dayofdebt = 0

    dayofdebtflag = False
    
    for icount in personaldfs1[person].index:
        if personaldfs1[person]['Owed'][icount] < 0 and dayofdebtflag == False:
            dayofdebtflag = True
            dayofdebt = personaldfs1[person]['day_difference'][icount]
        
        elif personaldfs1[person]['Owed'][icount] < 0 and dayofdebtflag == True:
            count = personaldfs1[person]['day_difference'][icount] - dayofdebt
        
        elif personaldfs1[person]['Owed'][icount] >= 0 and dayofdebtflag == True:
            count = personaldfs1[person]['day_difference'][icount] - dayofdebt
            listofdays.append(count)
            dayofdebtflag = False

        else:
            continue

    if dayofdebtflag == True:
        count = personaldfs1[person]['day_difference'].iloc[-2] - dayofdebt
        listofdays.append(count)


    for item in listofdays:
        sumoflist = sumoflist + item
    if len(listofdays) != 0:
        average = sumoflist/len(listofdays)
    else:
        print('{}: {} '.format(person, listofdays))
    print(listofdays)
    averagePayback[person] = average

averagePayback



averageGetback = {}
for person in listofnames:
    print('\n\n\n{}\n'.format(person))
    icount = 0
    count = 0
    listofdays = []
    average = 0
    sumoflist = 0
    dayofdebt = 0

    dayofdebtflag = False
    
    for icount in personaldfs1[person].index:
        if personaldfs1[person]['Owed'][icount] > 0 and dayofdebtflag == False:
            dayofdebtflag = True
            dayofdebt = personaldfs1[person]['day_difference'][icount]
        
        elif personaldfs1[person]['Owed'][icount] > 0 and dayofdebtflag == True:
            count = personaldfs1[person]['day_difference'][icount] - dayofdebt
        
        elif personaldfs1[person]['Owed'][icount] <= 0 and dayofdebtflag == True:
            count = personaldfs1[person]['day_difference'][icount] - dayofdebt
            listofdays.append(count)
            dayofdebtflag = False

        else:
            continue

    if dayofdebtflag == True:
        count = personaldfs1[person]['day_difference'].iloc[-2] - dayofdebt
        listofdays.append(count)


    for item in listofdays:
        sumoflist = sumoflist + item
    if len(listofdays) != 0:
        average = sumoflist/len(listofdays)
    else:
        print('{}: {} '.format(person, listofdays))
    print(listofdays)
    averageGetback[person] = average

averageGetback






















image_path_1 = "plot1.png"  # Replace with your image paths
image_path_2 = "plot2.png"
heading1_text = "Lend vs Borrow"
heading2_text = "Wordcloud of frequently used words"

# Create a PDF document with A4 page size
doc = SimpleDocTemplate("output.pdf", pagesize=A4)

# List to hold elements
elements = []

# Add the first image with heading 1
img1 = Image(image_path_1, width=6*inch, height=4*inch)
heading1_style = getSampleStyleSheet()["Heading1"]
heading1 = Paragraph(heading1_text, heading1_style)
elements.extend([heading1, img1])

# Add a spacer
elements.append(Spacer(1, 0.5*inch))

# Add the second image with heading 2
img2 = Image(image_path_2, width=6*inch, height=4*inch)
heading2_style = getSampleStyleSheet()["Heading2"]
heading2 = Paragraph(heading2_text, heading2_style)
elements.extend([heading2, img2])

# Build the PDF document up to this point
doc.build(elements)

# Create a new page for the dictionary data
elements1 = []

# Add the dictionary data at the start of a new page
data_style = getSampleStyleSheet()["BodyText"]
data_text = "<br/>".join(f"<b>{key}:</b> {value}" for key, value in creditScore.items())
data_paragraph = Paragraph(data_text, data_style)
elements1.append(data_paragraph)

# Add a page break
#elements1.append(PageBreak())

# Build the PDF document with the dictionary on a new page
doc.build(elements1)













# personaldfs1["Avaneesh Kulkarni"]


# with open("files.txt",'w') as f:
#     for item in creditScore.keys():
#         f.writelines(str(item) + " : " + str(creditScore[item]) + "\n")

#create pdf report
# c = canvas.Canvas('report.pdf', pagesize=A4)
# c.drawString(100, 750, "Splitwise Analysis Report")

# c.drawImage('plot1.png', 100, 500, width=400, height=300)
# c.drawImage('plot2.png', 100, 200, width=400, height=300)

# c.showPage()

# y_pos = 380
# for name, score in sortedCreditscores.items():
#     c.drawString(150, y_pos, f"{name}: {score}")
#     y_pos -= 20
    
# y_pos -= 20
# for name, score in credit_scores_2.items():
#     c.drawString(150, y_pos, f"{name}: {score}")
#     y_pos -= 20
    
# y_pos -= 20
# for name, score in credit_scores_3.items():
#     c.drawString(150, y_pos, f"{name}: {score}")
#     y_pos -= 20
    
# c.save()








# Extract names and scores from the dictionary
names = list(creditScore.keys())
raw_scores = np.array(list(creditScore.values()))

# Take the absolute value of scores
abs_scores = np.abs(raw_scores)

# Sort names based on absolute scores
sorted_indices = np.argsort(abs_scores)
sorted_names = [names[i] for i in sorted_indices]
sorted_abs_scores = abs_scores[sorted_indices]

# Set up the figure and axis
plt.figure(figsize=(10, 10))
plt.yscale('log')  # Set y-axis to be logarithmic
plt.bar(sorted_names, sorted_abs_scores, color='blue')
plt.xlabel('People')
plt.ylabel('Absolute Score (log)')
plt.title('Absolute Scores of People')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Display the plot
plt.show()

################################
# Extract names and scores from the dictionary
names = list(borrowedTotals.keys())
raw_scores = np.array(list(borrowedTotals.values()))

# Take the absolute value of scores
abs_scores = np.abs(raw_scores)

# Sort names based on absolute scores
sorted_indices = np.argsort(abs_scores)
sorted_names = [names[i] for i in sorted_indices]
sorted_abs_scores = abs_scores[sorted_indices]

# Set up the figure and axis
plt.figure(figsize=(10, 10))
#plt.yscale('log')  # Set y-axis to be logarithmic
plt.bar(sorted_names, sorted_abs_scores, color='blue')
plt.xlabel('People')
plt.ylabel('Amount (INR)')
plt.title('Total Amount Borrowed')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Display the plot
plt.show()
###########################################

# Extract names and scores from the dictionary
names = list(lendTotals.keys())
raw_scores = np.array(list(lendTotals.values()))

# Take the absolute value of scores
abs_scores = np.abs(raw_scores)

# Sort names based on absolute scores
sorted_indices = np.argsort(abs_scores)
sorted_names = [names[i] for i in sorted_indices]
sorted_abs_scores = abs_scores[sorted_indices]

# Set up the figure and axis
plt.figure(figsize=(10, 10))
#plt.yscale('log')  # Set y-axis to be logarithmic
plt.bar(sorted_names, sorted_abs_scores, color='blue')
plt.xlabel('People')
plt.ylabel('Amount (INR)')
plt.title('Total Amount Lent')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Display the plot
plt.show()
###########################################

# Extract names and scores from the dictionary
names = list(BLratio1.keys())
raw_scores = np.array(list(BLratio1.values()))

# Take the absolute value of scores
abs_scores = np.abs(raw_scores)

# Sort names based on absolute scores
sorted_indices = np.argsort(abs_scores)
sorted_names = [names[i] for i in sorted_indices]
sorted_abs_scores = abs_scores[sorted_indices]

# Set up the figure and axis
plt.figure(figsize=(10, 10))
#plt.yscale('log')  # Set y-axis to be logarithmic
plt.bar(sorted_names, sorted_abs_scores, color='blue')
plt.xlabel('People')
plt.ylabel('Borrow/Lend')
plt.title('Borrow to Lend Ratio')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Display the plot
plt.show()
###########################################

###########################################

# Extract names and scores from the dictionary
names = list(averagePayback.keys())
raw_scores = np.array(list(averagePayback.values()))

# Take the absolute value of scores
abs_scores = np.abs(raw_scores)

# Sort names based on absolute scores
sorted_indices = np.argsort(abs_scores)
sorted_names = [names[i] for i in sorted_indices]
sorted_abs_scores = abs_scores[sorted_indices]

# Set up the figure and axis
plt.figure(figsize=(10, 10))
#plt.yscale('log')  # Set y-axis to be logarithmic
plt.bar(sorted_names, sorted_abs_scores, color='blue')
plt.xlabel('People')
plt.ylabel('Days')
plt.title('Average number of days it takes to pay back all money owed')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Display the plot
plt.show()
###########################################

###########################################

# Extract names and scores from the dictionary
names = list(averageGetback.keys())
raw_scores = np.array(list(averageGetback.values()))

# Take the absolute value of scores
abs_scores = np.abs(raw_scores)

# Sort names based on absolute scores
sorted_indices = np.argsort(abs_scores)
sorted_names = [names[i] for i in sorted_indices]
sorted_abs_scores = abs_scores[sorted_indices]

# Set up the figure and axis
plt.figure(figsize=(10, 10))
#plt.yscale('log')  # Set y-axis to be logarithmic
plt.bar(sorted_names, sorted_abs_scores, color='blue')
plt.xlabel('People')
plt.ylabel('Days')
plt.title('Average number of days it takes to be owed back all money due')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Display the plot
plt.show()
###########################################




sortedBorrow = sorted(borrowedTotals.items(), key=lambda kv: kv[1])
sortedLend = sorted(lendTotals.items(), key=lambda kv: kv[1])
sortedBL = sorted(BLratio1.items(), key=lambda kv: kv[1])
sortedAveragePayback = sorted(averagePayback.items(), key=lambda kv: kv[1])
sortedAverageGetback = sorted(averageGetback.items(), key=lambda kv: kv[1])

sortedBorrow
sortedLend
sortedBL
sortedAveragePayback
sortedAverageGetback
