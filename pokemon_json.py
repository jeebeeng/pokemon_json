import json
import requests
import string
from typing import TypedDict, List
from collections import Counter


# Type aliases
Id = int
PokemonName = str
PokemonType = str


class Pokemon(TypedDict):
    id: Id
    name: PokemonName
    type: List[PokemonType]
    weaknesses: List[PokemonType]
    resistances: List[PokemonType]
    immunities: List[PokemonType]


class Type(TypedDict):
    name: PokemonType
    weaknesses: List[PokemonType]
    resistances: List[PokemonType]
    immunities: List[PokemonType]


MAX_ID = 1008
URL = r'https://pokeapi.co/api/v2/pokemon/'

# Load JSON files
__f_pokemon = open('./pokemon.json', 'r')
__f_types = open('./types.json', 'r')
__poke_data = json.load(__f_pokemon)
__type_data = json.load(__f_types)

pokemon_data: List[Pokemon] = __poke_data['pokemon']
types_data: List[Type] = __type_data['types']


def __url(id: Id) -> str:
    return URL + str(id)


# Creates a new JSON file with the updated list of Pokemon
def create_updated_file() -> None:
    updated_list = get_updated_list()
    with open('updated_pokemon.json', 'w') as f:
        json_string = json.dumps(updated_list, indent=4)
        f.write(json_string)
        print('Created file \'updated_pokemon.json\'')


# Updates the incorrect entries and adds missing Pokemon to pokemon_data.
# Returns an updated list of all the Pokemon.
def get_updated_list() -> List[Pokemon]:
    pokemon = check_pokemon()
    ids = get_missing_ids()

    for id in ids:
        r = requests.get(url=__url(id))
        data = r.json()

        name: PokemonName = data['name']
        types: List[PokemonType] = [i['type']['name'] for i in data['types']]

        pokemon.append(generate_entry(
            id, string.capwords(name.replace("-", " ")), types))

    print(f"{len(ids)} entries added")

    return pokemon


# Finds missing entries in the list of Pokemon.
# Returns a list of the IDs of missing Pokemon.
def get_missing_ids() -> List[Id]:
    ids: List[Id] = []
    curr = 1

    for entry in pokemon_data:
        if abs(entry['id'] - curr) > 1:
            ids += list(range(curr+1, entry['id']))
        curr = entry['id']

    ids += list(range(curr+1, MAX_ID+1))

    return ids


# Checks each Pokemon to make sure the typings are correct.
# Returns the corrected list of Pokemon.
def check_pokemon() -> List[Pokemon]:
    checked: List[Pokemon] = []
    for entry in pokemon_data:
        checked.append(correct_entry(entry))

    return checked


# Checks the entry to make sure the typings are correct.
# Returns the correct Pokemon
def correct_entry(entry: Pokemon) -> Pokemon:
    id = entry['id']
    name = entry['name']
    types = entry['type']
    weaknesses = sorted(entry['weaknesses'])
    resistances = sorted(entry['resistances'])
    immunities = sorted(entry['immunities'])

    good_entry = generate_entry(id, name, types)
    w = good_entry['weaknesses']
    r = good_entry['resistances']
    i = good_entry['immunities']

    corrected = (weaknesses != w) or (resistances != r) or (immunities != i)
    print(f"({id}) {name} was updated\n" if corrected else "", end="")

    return good_entry


# Generates a Pokemon entry with the correct typings given the id, name, and types.
# Returns a Pokemon.
def generate_entry(id: int, name: str, types: List[PokemonType]) -> Pokemon:
    weaknesses: List[PokemonType] = []
    resistances: List[PokemonType] = []
    immunities: List[PokemonType] = []

    type1 = get_type(types[0])
    weaknesses += type1['weaknesses']
    resistances += type1['resistances']
    immunities += type1['immunities']

    if len(types) > 1:
        type2 = get_type(types[1])
        weaknesses += type2['weaknesses']
        resistances += type2['resistances']
        immunities += type2['immunities']

        # Remove any conflicting typings
        w_set = set(weaknesses)
        r_set = set(resistances)
        i_set = set(immunities)

        weaknesses = list(w_set - (r_set | i_set))
        resistances = list(r_set - (w_set | i_set))

    entry: Pokemon = {"id": id, "name": name, "type": types, "weaknesses": sorted(weaknesses),
                      "resistances": sorted(resistances), "immunities": sorted(immunities)}
    return entry


def get_by_id(id: int) -> Pokemon:
    return next(x for x in pokemon_data if x['id'] == id)


def get_type(name: PokemonType) -> Type:
    return next(x for x in types_data if x['name'] == name)


if __name__ == '__main__':
    create_updated_file()
