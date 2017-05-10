from collections import defaultdict
import re
import pandas as pd

characters = defaultdict(list)
with open('love_actually/love_actually.txt') as f:
    for line in f:
        if re.match(r'^[A-Z]+:', line):
            colon = line.find(':')
            characters[line[:colon]].append(line[colon+1:])

characters_df = pd.DataFrame(columns = ['character', 'lines'])
for character in characters.keys():
    characters_df.loc[len(characters_df), :] = [character, len(characters[character])]

characters_df = characters_df.sort_values('lines', ascending = False)
final_characters = characters_df.iloc[:15, :]
final_characters = final_characters['character']

for character in final_characters:
    with open('love_actually/' + character + '.txt', 'a') as lines:
        lines.write('\n'.join(characters[character]))