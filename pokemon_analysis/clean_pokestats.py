"""
Clean the broken PokeStats.csv file into a proper CSV with columns:
ID, Name, Type1, Type2, Total, HP, Attack, Defense, Sp. Atk, Sp. Def, Speed
"""

from pathlib import Path
import csv

INPUT = Path('pokemon_analysis/PokeStats.csv')
OUTPUT = Path('pokemon_analysis/PokeStats_cleaned.csv')
TYPE_NAMES = [
    'normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 'poison',
    'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark',
    'steel', 'fairy'
]


def parse_type_line(text: str):
    text = text.strip()
    # strip leading ID
    if len(text) < 3 or not text[:3].isdigit():
        return None, None, None
    poke_id = text[:3]
    rest = text[3:].strip()
    rest_lower = rest.lower()
    # try type2 first
    for type2 in TYPE_NAMES + ['']:
        if type2:
            if rest_lower.endswith(type2):
                prefix = rest[: -len(type2)].rstrip()
                prefix_lower = rest_lower[: -len(type2)].rstrip()
            else:
                continue
        else:
            prefix = rest
            prefix_lower = rest_lower
        for type1 in TYPE_NAMES:
            if prefix_lower.endswith(type1):
                name = prefix[: -len(type1)].strip()
                if name:
                    return poke_id, name, type1, type2 or None
    return poke_id, rest, None, None


def decode_line(line: str) -> str:
    line = line.strip()
    if line.startswith("b'") and line.endswith("'"):
        line = line[2:-1]
    if line.startswith('b"') and line.endswith('"'):
        line = line[2:-1]
    return line.encode('utf-8').decode('unicode_escape')


def clean():
    rows = []
    errors = []

    with INPUT.open('r', encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\n') for l in f]

    for idx, raw in enumerate(lines):
        if not raw.strip():
            continue
        decoded = decode_line(raw)
        if idx == 0 and decoded.lower().startswith('# name'):
            continue
        parts = decoded.splitlines()
        if len(parts) < 8:
            errors.append((idx + 1, decoded))
            continue
        header = parts[0].strip()
        stats = parts[1:8]
        if len(stats) != 7:
            errors.append((idx + 1, decoded))
            continue
        poke_id, name, type1, type2 = parse_type_line(header)
        if type1 is None:
            # fallback: try splitting by spaces and last 2 tokens as types
            tokens = header.split()
            if len(tokens) >= 3 and tokens[-1].lower() in TYPE_NAMES:
                type2 = tokens[-1].lower()
                if tokens[-2].lower() in TYPE_NAMES:
                    type1 = tokens[-2].lower()
                    name = ' '.join(tokens[1:-2])
                else:
                    type1 = tokens[-1].lower()
                    type2 = None
                    name = ' '.join(tokens[1:-1])
        if poke_id is None:
            errors.append((idx + 1, decoded))
            continue
        try:
            total, hp, attack, defense, sp_attack, sp_defense, speed = [int(x.strip()) for x in stats]
        except ValueError:
            errors.append((idx + 1, decoded))
            continue
        rows.append({
            'id': poke_id,
            'name': name,
            'type1': type1.title() if type1 else '',
            'type2': type2.title() if type2 else '',
            'total': total,
            'hp': hp,
            'attack': attack,
            'defense': defense,
            'sp_attack': sp_attack,
            'sp_defense': sp_defense,
            'speed': speed,
        })

    with OUTPUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'type1', 'type2', 'total', 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'])
        writer.writeheader()
        writer.writerows(rows)

    print(f'Processed {len(rows)} rows into {OUTPUT}')
    if errors:
        print(f'Encountered {len(errors)} parse issues. First 10:')
        for err in errors[:10]:
            print(err)


if __name__ == '__main__':
    clean()
