from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pokedex')
def pokedex():
    from services.pokeapi import get_all_pokemon
    
    page = int(request.args.get('page', 1))
    per_page = 70
    
    all_data = get_all_pokemon()
    if not all_data:
        return "Erro ao carregar Pokédex", 500
    
    all_pokemons = all_data['results']
    total = len(all_pokemons)
    total_pages = (total + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    pokemons_page = all_pokemons[start:end]
    
    return render_template('pokedex.html', 
                         pokemons=pokemons_page,
                         page=page,
                         total_pages=total_pages,
                         total=total)

@app.route('/pokedex/<name_or_id>')
def pokemon_detail(name_or_id):
    from services.pokeapi import get_pokemon_details, get_pokemon_species, get_evolution_chain, get_ability_description
    from services.translator import translate_to_portuguese
    
    pokemon = get_pokemon_details(name_or_id)
    if not pokemon:
        return "Pokemon not found", 404
    
    species = get_pokemon_species(name_or_id)
    
    evolution_chain = None
    if species and species.get('evolution_chain_url'):
        evolution_chain = get_evolution_chain(species['evolution_chain_url'])
    
    abilities_with_desc = []
    for ability_name in pokemon['abilities']:
        ability_data = get_ability_description(ability_name)
        ability_data['description'] = translate_to_portuguese(ability_data['description'])
        abilities_with_desc.append(ability_data)
    
    return render_template('detail.html', 
                         pokemon=pokemon, 
                         species=species,
                         evolution_chain=evolution_chain,
                         abilities=abilities_with_desc)

@app.route('/api/move/<move_name>')
def get_move_info(move_name):
    from services.pokeapi import get_move_details
    from services.translator import translate_to_portuguese
    
    move_details = get_move_details(move_name)
    if move_details:
        if move_details.get('effect'):
            move_details['effect'] = translate_to_portuguese(move_details['effect'])
        return jsonify(move_details)
    return jsonify({'error': 'Move not found'}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True)
