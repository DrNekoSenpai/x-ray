from openpyxl import load_workbook
cwl_filename = 'Reddit X-ray CWL Random Distribution.xlsx'
wb = load_workbook(filename = cwl_filename)
sheet_name = wb.sheetnames[0]
sheets = wb[sheet_name]

eligible = []
already_received = []
ineligible = []

for ind,row in enumerate(sheets.iter_rows(values_only=True)): 
    if ind == 0: headers = row
    else: 
        if row[0] is not None: eligible.append(row[0])
        if row[1] is not None: already_received.append(row[1])
        if row[2] is not None: ineligible.append(row[2])

from datetime import datetime
import calendar

this_month = calendar.month_name[datetime.today().month]
this_year = datetime.today().year
    
if len(eligible) == 0 and len(ineligible) == 0: 
    print('Enter in names of participating players, with number of hits missed: ')
    for i in range(50): 
        player = input('[%i] ' % (i+1))
        if player == '': break
        player = player.rsplit(' ', 1)
        
        if player[0] in already_received: continue
        try: player[1] = int(player[1])
        except: 
            print('Invalid input for number of hits used.')
            continue
        
        missed_hits = player[1]
        if missed_hits > 2: ineligible.append(player[0])
        else: eligible.append(player[0])

    print(eligible)
    print(already_received)
    print(ineligible)
    
    from openpyxl import Workbook
    wb = Workbook()
    ws1 = wb.active
    ws1.title = sheet_name
    
    ws1.append(headers)
    for ind,val in enumerate(eligible):
        ws1['A%i' % (ind+2)] = val
    for ind,val in enumerate(already_received): 
        ws1['B%i' % (ind+2)] = val
    for ind,val in enumerate(ineligible): 
        ws1['C%i' % (ind+2)] = val
    
    wb.save(filename = cwl_filename)

else: 
    num_bonuses = int(input("How many bonuses are available this month? "))
    print('**---- %s %s CWL Random Distribution ----**' % (this_month, this_year))
    print('(%s available bonuses, total)' % num_bonuses)
    print('')
    
    print('**Eligible**: ', end = '')
    for ind,val in enumerate(eligible): 
        print(val, end = '')
        if ind != len(eligible)-1: print(', ', end = '')
    print('')
    
    print('**Ineligible (already received)**: ', end = '')
    for ind,val in enumerate(already_received): 
        print(val, end = '')
        if ind != len(already_received)-1: print(', ', end = '')
    print('')
    
    print('**Ineligible (missed hits)**: ', end = '')
    for ind,val in enumerate(ineligible): 
        print(val, end = '')
        if ind != len(ineligible)-1: print(', ', end = '')
    print('')