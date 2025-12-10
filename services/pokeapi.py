import requests
from functools import lru_cache

BASE_URL = "https://pokeapi.co/api/v2"

@lru_cache(maxsize=256)
def get_pokemon_list(limit=20, offset=0):
    try:
        url = f"{BASE_URL}/pokemon?limit={limit}&offset={offset}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=1)
def get_all_pokemon():
    try:
        url = f"{BASE_URL}/pokemon?limit=1"
        response = requests.get(url)
        response.raise_for_status()
        total_count = response.json()['count']
        
        url = f"{BASE_URL}/pokemon?limit={total_count}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=128)
def get_pokemon_details(name_or_id):
    try:
        url = f"{BASE_URL}/pokemon/{name_or_id}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        parsed_data = {
            'id': data['id'],
            'name': data['name'],
            'height': data['height'],
            'weight': data['weight'],
            'types': [t['type']['name'] for t in data['types']],
            'stats': {s['stat']['name']: s['base_stat'] for s in data['stats']},
            'abilities': [a['ability']['name'] for a in data['abilities']],
            'moves': [{'name': m['move']['name'], 'url': m['move']['url']} for m in data['moves']],
            'sprites': {
                'front_default': data['sprites']['front_default'],
                'front_shiny': data['sprites']['front_shiny'],
                'back_default': data['sprites']['back_default'],
                'back_shiny': data['sprites']['back_shiny'],
                'artwork_default': data['sprites']['other']['official-artwork']['front_default'],
                'artwork_shiny': data['sprites']['other']['official-artwork']['front_shiny'],
                'dream_world': data['sprites']['other']['dream_world']['front_default']
            }
        }
        return parsed_data
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=128)
def get_pokemon_species(name_or_id):
    try:
        url = f"{BASE_URL}/pokemon-species/{name_or_id}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        flavor_text = None
        for entry in data['flavor_text_entries']:
            if entry['language']['name'] == 'pt-BR':
                flavor_text = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                break
        
        if not flavor_text:
            for entry in data['flavor_text_entries']:
                if entry['language']['name'] == 'en':
                    flavor_text = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                    break
        
        parsed_data = {
            'id': data['id'],
            'name': data['name'],
            'flavor_text': flavor_text,
            'evolution_chain_url': data['evolution_chain']['url'] if data.get('evolution_chain') else None,
            'genera': next((g['genus'] for g in data['genera'] if g['language']['name'] == 'pt-BR'), 
                           next((g['genus'] for g in data['genera'] if g['language']['name'] == 'en'), None)),
            'varieties': data.get('varieties', [])
        }
        return parsed_data
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=64)
def get_pokemon_varieties_details(name_or_id):
    species_data = get_pokemon_species(name_or_id)
    if not species_data or not species_data.get('varieties'):
        return []

    varieties_details = []
    base_name = species_data['name']

    for variety in species_data['varieties']:
        if not variety['is_default']:
            variety_name = variety['pokemon']['name']
            details = get_pokemon_details(variety_name)
            if details:
                readable_name = variety_name.replace(base_name, '').replace('-', ' ').strip().title()
                if not readable_name:
                    readable_name = "Alternative Form"
                details['form_name'] = readable_name
                varieties_details.append(details)
    
    return varieties_details

@lru_cache(maxsize=128)
def get_evolution_chain(chain_url):
    try:
        response = requests.get(chain_url)
        response.raise_for_status()
        data = response.json()
        
        def extract_chain(chain_data):
            current = {
                'name': chain_data['species']['name'],
                'url': chain_data['species']['url']
            }
            
            evolutions = []
            for evolution in chain_data.get('evolves_to', []):
                evolutions.append(extract_chain(evolution))
            
            if evolutions:
                current['evolves_to'] = evolutions
            
            return current
        
        return extract_chain(data['chain'])
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None

@lru_cache(maxsize=256)
def get_ability_description(ability_name):
    try:
        url = f"{BASE_URL}/ability/{ability_name}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        description = None
        for entry in data.get('effect_entries', []):
            if entry['language']['name'] == 'en':
                description = entry['short_effect']
                break
        
        return {
            'name': data['name'],
            'description': description or "Descrição não disponível"
        }
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return {'name': ability_name, 'description': "Descrição não disponível"}

@lru_cache(maxsize=512)
def get_move_details(name_or_id):
    try:
        url = f"{BASE_URL}/move/{name_or_id}/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        effect = None
        for entry in data.get('effect_entries', []):
            if entry['language']['name'] == 'en':
                effect = entry['short_effect']
                break
        
        parsed_data = {
            'id': data['id'],
            'name': data['name'],
            'accuracy': data['accuracy'],
            'power': data['power'],
            'pp': data['pp'],
            'type': data['type']['name'],
            'damage_class': data['damage_class']['name'],
            'effect': effect or "No description available"
        }
        return parsed_data
    except requests.RequestException as e:
        print(f"Erro: {e}")
        return None