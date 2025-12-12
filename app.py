from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from services.pokeapi import (
    get_all_pokemon, 
    get_pokemon_details, 
    get_pokemon_species, 
    get_evolution_chain, 
    get_ability_description,
    get_pokemon_varieties_details, 
    get_move_details
)
from services.translator import translate_to_portuguese

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pokedex')
def pokedex():
    page = int(request.args.get('page', 1))
    per_page = 70
    
    all_data = get_all_pokemon()
    if not all_data:
        return render_template('pokedex.html', pokemon_list=[], page=page, total_pages=0)
    
    pokemon_list = all_data['results']
    total_items = len(pokemon_list)
    total_pages = (total_items + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    page_items = []
    for p in pokemon_list[start:end]:
        p_id = p['url'].split('/')[-2]
        page_items.append({
            'name': p['name'],
            'url': p['url'],
            'id': p_id,
            'image': f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p_id}.png"
        })
        
    return render_template('pokedex.html', 
                           pokemons=page_items, 
                           page=page, 
                           total=total_items,
                           total_pages=total_pages)

def calculate_stats_range(stats_data):
    # Converte lista da API para dicionário {nome: valor} se necessário
    if isinstance(stats_data, list):
        base_stats = {item['stat']['name']: item['base_stat'] for item in stats_data}
    else:
        base_stats = stats_data

    ranges = {}
    for stat, base in base_stats.items():
        if stat == 'hp':
            min_val = 2 * base + 110
            max_val = 2 * base + 204
        else:
            min_val = int((2 * base + 5) * 0.9)
            max_val = int((2 * base + 99) * 1.1)
            
        
        if base < 60:
            color = '#ff4e4e'      # Vermelho
        elif base < 90:
            color = '#f0932b'      # Laranja
        elif base < 120:
            color = '#f1c40f'      # Amarelo
        else:
            color = '#6ab04c'      # Verde
            
        ranges[stat] = {'base': base, 'min': min_val, 'max': max_val, 'color': color}
    return ranges

@app.route('/pokemon/<name_or_id>')
def pokemon_detail(name_or_id):
    
    pokemon = get_pokemon_details(name_or_id)
    if not pokemon:
        return "Pokemon not found", 404
    
    # Calcula Ranges de Stats
    pokemon['stats_ranges'] = calculate_stats_range(pokemon['stats'])

    # Nota: Usamos name_or_id para Venusaur, mas get_pokemon_species também aceita o ID, 
    # garantindo que formas alternativas (como venusaur-mega) ainda encontrem o species correto (venusaur).
    species = get_pokemon_species(pokemon['id']) 
    
    evolution_chain = None
    if species and species.get('evolution_chain_url'):
        evolution_chain = get_evolution_chain(species['evolution_chain_url'])
    
    abilities_with_desc = []
    for ability_name in pokemon['abilities']:
        ability_data = get_ability_description(ability_name)
        
        # Tenta traduzir a descrição da habilidade
        try:
            ability_data['description'] = translate_to_portuguese(ability_data['description'])
        except:
            pass # Mantém em inglês se a tradução falhar
            
        abilities_with_desc.append(ability_data)
        
    # Se a descrição (flavor_text) veio em inglês (fallback), traduzir para PT
    if species and species.get('flavor_text'):
        try:
            species['flavor_text'] = translate_to_portuguese(species['flavor_text'])
        except:
            pass 

    # BUSCA E PASSAR VARIANTES (MEGAS, ALOLAN, ETC.) ---
   
    varieties = get_pokemon_varieties_details(species['id']) 
    


    return render_template('detail.html', 
                           pokemon=pokemon, 
                           species=species,
                           evolution_chain=evolution_chain,
                           abilities=abilities_with_desc,
                           varieties=varieties) 

@app.route('/api/move/<move_name>')
def get_move_info(move_name):
    
    move_details = get_move_details(move_name)
    if move_details:
        if move_details.get('effect'):
            try:
                move_details['effect'] = translate_to_portuguese(move_details['effect'])
            except:
                pass 
                
        return jsonify(move_details)
    return jsonify({'error': 'Move not found'}), 404

if __name__ == '__main__':
    
    from livereload import Server
    server = Server(app.wsgi_app)

    server.watch('templates/*.html')
    server.watch('static/css/*.css')
    server.watch('static/js/*.js')
    
    print("Iniciando servidor com LiveReload na porta 5000...")
    server.serve(port=5000)