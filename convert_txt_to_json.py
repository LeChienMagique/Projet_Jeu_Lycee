import json

level = {"tile": {"number": 0, "positions": []}, "jumper": {"number": 0, "positions": []}, "spike_n": {"number": 0, "positions": []},
         "spike_w": {"number": 0, "positions": []}, "spike_e": {"number": 0, "positions": []}, "spike_s": {"number": 0, "positions": []},
         "end": {"number": 0, "positions": []}}

with open('Levels/level_1.txt', 'rt') as f:
    raw_lvl = f.read()
    raw_lvl = raw_lvl.split('\n')
    x = 0
    y = 0
    for row in raw_lvl:
        for col in row:
            if col == '1':
                level["tile"]['number'] += 1
                level["tile"]['positions'].append((x,y))
            elif col == '2':
                level["jumper"]['number'] += 1
                level["jumper"]['positions'].append((x, y))
            elif col == '3':
                level["spike_n"]['number'] += 1
                level["spike_n"]['positions'].append((x, y))
            elif col == '4':
                level["spike_w"]['number'] += 1
                level["spike_w"]['positions'].append((x, y))
            elif col == '5':
                level["spike_e"]['number'] += 1
                level["spike_e"]['positions'].append((x, y))
            elif col == '6':
                level["spike_s"]['number'] += 1
                level["spike_s"]['positions'].append((x, y))
            elif col == '7':
                level["end"]['number'] += 1
                level["end"]['positions'].append((x, y))
            x += 1
        x = 0
        y += 1

with open('Levels/level_1.json', 'w') as j:
    json.dump(level, j, indent=0)