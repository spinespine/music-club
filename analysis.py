import csv
import matplotlib.pyplot as plt
import numpy as np
import random
import sys

class member: # a person with their name and data
    def __init__(self, name):
        self.name = name
        self.data_points = 0

rows = [] # raw data
with open('rankings.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        rows.append(row)

albums = rows.pop(0) # remove header row
rows.pop(0) # remove week # row
number_of_weeks = len(rows[0])
albums.pop(0)
albums.pop(14)

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
        multiplier = number_of_weeks - instances
        multiplier *= 0.025
        member.deltas[friend.name] = avg_delta * (1 + multiplier)
        if member.name == 'Jaxson' and friend.name == 'Peter':
            print(sum_of_differences, instances)

weeks = [] # 2D array of scores
week = 1
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

plt.figure(figsize=(25, 6))
for member in members: # get average deviation
    deviation_total = 0
    weeks_rated = 0
    member_timeline = []
    has_rated = False
    current_deviation = -2.1
    for week, rating in enumerate(member.ratings):
        if rating == '': 
            member_timeline.append(current_deviation)
            continue
        weeks_rated += 1
        rating = int(rating)
        deviation = rating - week_averages[week]
        deviation_total += deviation
        avg_deviation = deviation_total / weeks_rated
        current_deviation = avg_deviation

        if current_deviation > 2: current_deviation = 2

        member_timeline.append( current_deviation )
        print(avg_deviation)
    
    plt.plot(member_timeline, label = member.name)
    avg_deviation = deviation_total / weeks_rated
    member.avg_deviation = avg_deviation

plt.xticks(ticks=range(len(albums)), labels=albums, rotation=45, ha="right")
plt.ylim(-2.05, 2)
plt.legend()
plt.savefig('deviation_timeline.png', bbox_inches='tight')

# print results
class stat:
    value = 0
    member = ''
    friend = ''

most_compatible = stat()
most_compatible.value = float('inf')

most_incompatible = stat()

print('\nCompatibility Map')
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
        formatted_delta = round(delta * 10, 1)
        friend_total += 1

        if formatted_delta == -10:
            continue
        
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
        if formatted_delta > -1:
            print(delta.friend + tab + str(formatted_delta))

    # stats stuff
    member.avg_agreeability = round(member.disagreement_points / member.data_points, 2)

    member_most_compatible.value = str( round(member_most_compatible.value * 10, 2) )
    member_least_compatible.value = str( round(member_least_compatible.value * 10, 2) )
    print('most compatible with', member_most_compatible.friend, '(' + 
          member_most_compatible.value + ')')
    print('least compatible with', member_least_compatible.friend, '(' + 
          member_least_compatible.value + ')')
    
print("\n(Compatibility is calculated from the average rating differece between you and another club member, multiplied by 10 for legibility)")

print('\n' + 'most compatible pair:', 
      most_compatible.member, 'and', 
      most_compatible.friend, 'with',
      most_compatible.value, 'disagreement points.' )
print("Over 24 meetings, Jaxson and Peter's rating differences total 16.")

print('\n' + 'most incompatible pair:', 
      most_incompatible.member, 'and', 
      most_incompatible.friend, 'with',
      most_incompatible.value, 'disagreement points.' )
print("Over 3 meetings, Alex and Habibi's rating differences total 11.")

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
plt.savefig('heatmap.png', bbox_inches='tight')

members_and_ratings = {}

plt.figure(figsize=(25, 15))

albumLabels = []
for album in albums:
    albumLabels.append(album)

for member in members:
    members_and_ratings[member.name] = []

    for i, rating in enumerate(member.ratings):
        members_and_ratings[member.name].append(rating)

# plot lines
i = 0
for (member, ratings) in members_and_ratings.items():
    for week, rating in enumerate(ratings):
        if rating == '':
            ratings[week] = None
        else:
            ratings[week] = int(rating) + i

    i += 0.05
    plt.plot(ratings, label = member)

plt.xticks(ticks=range(len(albums)), labels=albumLabels, rotation=45, ha="right")
plt.legend()
plt.savefig('timeline.png', bbox_inches='tight')

for member in members:

    print(member.name)

    top3 = []
    for delta in member.sortedDeltas:
        print(delta.value)
        if delta.value != -1:
            top3.append(delta.friend)
            if len(top3) == 3:
                break

    bottom3 = [member.sortedDeltas[-1].friend, member.sortedDeltas[-2].friend, member.sortedDeltas[-3].friend]

    print(top3)
    print(bottom3)

    plt.figure(figsize=(25, 6))
    for topFriend in top3:
        relevantPoints = []
        for i, rating in enumerate(members_and_ratings[member.name]):
            if rating == None:
                relevantPoints.append(None)
            else:
                relevantPoints.append(members_and_ratings[topFriend][i])

        plt.plot( relevantPoints, label = topFriend, marker='o' )

    plt.title(member.name + ' and their most compatible friends')
    plt.plot(members_and_ratings[member.name], label = member.name, marker='*', color = 'black')
    plt.xticks(ticks=range(len(albums)), labels=albumLabels, rotation=45, ha="right")
    plt.ylim(-4.5, 5.5)  # Limit Y axis from -4 to 5
    plt.yticks(range(-4, 6))  # Set Y ticks as integers from -4 to 5
    plt.legend()
    plt.savefig('member timelines/{name}-close.png'.format(name = member.name), bbox_inches='tight')

    plt.figure(figsize=(25, 6))
    for bottomFriend in bottom3:
        relevantPoints = []
        for i, rating in enumerate(members_and_ratings[member.name]):
            if rating == None:
                relevantPoints.append(None)
            else:
                relevantPoints.append(members_and_ratings[bottomFriend][i])

        plt.plot( relevantPoints, label = bottomFriend, marker='x')

    plt.title(member.name + ' and their least compatible friends')
    plt.plot(members_and_ratings[member.name], label = member.name, marker='*', color = 'black')
    plt.xticks(ticks=range(len(albums)), labels=albumLabels, rotation=45, ha="right")
    plt.ylim(-4.5, 5.5)  # Limit Y axis from -4 to 5
    plt.yticks(range(-4, 6))  # Set Y ticks as integers from -4 to 5
    plt.legend()
    plt.savefig('member timelines/{name}-far.png'.format(name = member.name), bbox_inches='tight')


