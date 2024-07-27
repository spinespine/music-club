import csv
import matplotlib.pyplot as plt
import numpy as np

class member: # a person with their name and data
    def __init__(self, name):
        self.name = name
        self.data_points = 0

rows = [] # raw data
with open('rankings.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        rows.append(row)

rows.pop(0) # remove header row
rows.pop(0) # remove week row

members = [] # everyone in music club as a member object
for row in rows:
    name = row[0]
    person = member(name)
    person.ratings = row[1:]
    members.append(person)

for member in members: # remove season 2 spacer
    member.ratings.pop(14)

for member in members: # calculate compatibility
    member.deltas = {}
    member.disagreement_points = 0
    for friend in members:
        if friend.name == member.name: continue
        sum_of_differences = instances = 0
        for week, friend_rating in enumerate(friend.ratings):
            member_rating = member.ratings[week]
            friend_rating = friend.ratings[week]
            if member_rating == '' or friend_rating == '': continue
            member.data_points += 1
            member_rating = int(member_rating)
            friend_rating = int(friend_rating)
            sum_of_differences += abs(member_rating - friend_rating)
            instances += 1

        member.disagreement_points += sum_of_differences

        if instances == 0:
            member.deltas[friend.name] = -1
            continue

        avg_delta = sum_of_differences / instances
        member.deltas[friend.name] = avg_delta

weeks = [] # 2D array of scores
week = 1
number_of_weeks = len(rows[0])
while week < number_of_weeks:
    weeks.append([])
    for row in rows:
        rating = row[week]
        weeks[-1].append(rating)
    week += 1

weeks.pop(14) # remove season 2 spacer

week_averages = [] # just realized this shit was already in the csv...
for week in weeks:
    total = 0
    count = 0
    for score in week:
        if score == '': continue
        score = int(score)
        total += score
        count += 1
    week_averages.append( round(total / count, 2) )

for member in members: # get average deviation
    deviation_total = 0
    weeks_rated = 0
    for week, rating in enumerate(member.ratings):
        if rating == '': continue
        weeks_rated += 1
        rating = int(rating)
        deviation = rating - week_averages[week]
        deviation_total += deviation
    avg_deviation = deviation_total / weeks_rated
    member.avg_deviation = avg_deviation

# print results
class stat:
    value = 0
    member = ''
    friend = ''

most_compatible = stat()
most_compatible.value = float('inf')

most_incompatible = stat()

print('\nCompatability Map')
print('person\t\tdisagreement points')

for member in members:
    print('\n--', member.name, '--' )
    member_least_compatible = stat()
    member_most_compatible = stat()
    member_most_compatible.value = float('inf')
    friend_total = 0
    member.sortedDeltas = []
    for (friend, delta) in member.deltas.items():
        newDelta = stat()
        newDelta.value = delta
        newDelta.friend = friend
        member.sortedDeltas.append(newDelta)

        # stats stuff
        formatted_delta = round(delta * 10)
        friend_total += 1
        
        if delta < member_most_compatible.value:
            member_most_compatible.value = delta
            member_most_compatible.friend = friend
        
        if delta > member_least_compatible.value:
            member_least_compatible.value = delta
            member_least_compatible.friend = friend

        if formatted_delta > most_incompatible.value: 
            most_incompatible.value = formatted_delta
            most_incompatible.member = member.name
            most_incompatible.friend = friend

        if formatted_delta < most_compatible.value and formatted_delta != 0:
            most_compatible.value = formatted_delta
            most_compatible.member = member.name
            most_compatible.friend = friend
    
    member.sortedDeltas.sort(key=lambda d: d.value)
    for delta in member.sortedDeltas:
        formatted_delta = round(delta.value * 10, 1)
        tab = '\t'
        if len(delta.friend) < 8: tab += '\t'
        print(delta.friend + tab + 'tab.' + str(formatted_delta))

    # stats stuff
    member.avg_agreeability = round(member.disagreement_points / member.data_points, 2)

    member_most_compatible.value = str( round(member_most_compatible.value * 10, 1) )
    member_least_compatible.value = str( round(member_least_compatible.value * 10, 1) )
    print('most compatible with', member_most_compatible.friend, '(' + 
          member_most_compatible.value + ')')
    print('least compatible with', member_least_compatible.friend, '(' + 
          member_least_compatible.value + ')')
    
print("\n(Compatability is calculated from the average rating differece between you and another club member, multiplied by 10 for legibility)")

print('\n' + 'most compatible pair:', 
      most_compatible.member, 'and', 
      most_compatible.friend, 'with',
      most_compatible.value, 'disagreement points.' )

print("Over 18 meetings, Jaxson and Peter's rating differences total a mere 13. I'm excluding Midnight & Disconnect whose total was 0 as they only rated the same album once.")

print('\n' + 'most incompatible pair:', 
      most_incompatible.member, 'and', 
      most_incompatible.friend, 'with',
      most_incompatible.value, 'disagreement points.' )
print("Over 6 meetings, Yumi and Disconnect's rating differences total 19. Oof.")

print('\n' + "members by typical deviation from average score:")
for member in sorted(members, key=lambda m: m.avg_deviation, reverse=True):
    value = round(member.avg_deviation, 2)
    result = value if value < 0 else '+' + str(value)
    print(member.name + ":", result)
print("(on average, your rating for an album will be this value relative to the group's average rating for that album)")

print('\n' + 'members from most to least disagreeable on average:')
for member in sorted(members, key=lambda m: m.avg_agreeability, reverse=True):
    print(member.name + ':', round(member.avg_agreeability * 100))
print("(you get x disagreements when your rating is x points different than someone else's. this is your total disagreement count divided by the number of times your rating can be compared to someone else's)")

print('\n' + 'members from most to least data points:')
for member in sorted(members, key=lambda m: m.data_points, reverse=True):
    print(member.name + ':', member.data_points)
print("(this is how many times your score can be compared to someone else's)")

# compatability heatmap
heatmap = []
names = []
for i, member in enumerate(members):
    row = []
    for friend, delta in member.deltas.items():
        row.append( round(float(delta) * 10) )
    row.insert(i, -1)
    heatmap.append(row)
    names.append(member.name)

result = np.array(heatmap)

fig, ax = plt.subplots(figsize=(12, 12))
im = ax.imshow(heatmap)
ax.set_xticks(np.arange(len(names)), labels=names)
ax.set_yticks(np.arange(len(names)), labels=names)

secax_x = ax.secondary_xaxis('top')
secax_x.set_xticks(np.arange(len(names)))
secax_x.set_xticklabels(names, rotation=45, ha="left", rotation_mode="anchor")

secax_y = ax.secondary_yaxis('right')
secax_y.set_yticks(np.arange(len(names)))
secax_y.set_yticklabels(names)

plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    rotation_mode="anchor")

for i in range(len(heatmap)): # add text to spots
    for j in range(len(heatmap)):
        text = ax.text(j, i, heatmap[i][j] if heatmap[i][j] >= 0 else 'X',
            ha="center", va="center", 
            color="w" if heatmap[i][j] < 25 else 'k')

im = ax.imshow(heatmap, cmap='magma')
cbar = ax.figure.colorbar(im, ax=ax, pad=0.15, shrink=0.5)
cbar.ax.yaxis.set_label_position('left')
cbar.set_label('incompatibility')

fig.tight_layout()
plt.show()
