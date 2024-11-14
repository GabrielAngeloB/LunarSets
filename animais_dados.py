import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import re
import random


translator = Translator()

# Lista de exemplos de nomes científicos de animais
animal_names = [
    "Panthera leo",  # Leão
    "Loxodonta africana",  # Elefante africano
    "Ailuropoda melanoleuca",  # Panda gigante
    "Balaenoptera musculus",  # Baleia azul
    "Ursus maritimus",  # Urso polar
    "Gorilla gorilla",  # Gorila
    "Carcharodon carcharias",  # Tubarão branco
    "Vulpes vulpes",  # Raposa vermelha
    "Hippopotamus amphibius",  # Hipopótamo
    "Equus caballus",  # Cavalo
    "Crocodylus porosus",  # Crocodilo de água salgada
    "Canis lupus",  # Lobo
    "Panthera onca",  # Onça-pintada
    "Felis catus",  # Gato doméstico
    "Delphinus delphis",  # Golfinho comum
    "Ursus arctos",  # Urso pardo
    "Struthio camelus",  # Avestruz
    "Aquila chrysaetos",  # Águia-real
    "Giraffa camelopardalis",  # Girafa
    "Cervus elaphus",  # Cervo-vermelho
    "Macropus rufus",  # Canguru vermelho
    "Haliaeetus leucocephalus",  # Águia-careca
    "Sphenodon punctatus",  # Tuatara
    "Chelonia mydas",  # Tartaruga verde
    "Dendrocygna bicolor",  # Pato-de-cabeça-preta
    "Lynx lynx",  # Lince-euroasiático
    "Puma concolor",  # Puma
    "Bison bison",  # Bisonte americano
    "Panthera tigris",  # Tigre
    "Bubalus bubalis",  # Búfalo de água
    "Vulpes vulpes",  # Raposa vermelha
    "Tursiops truncatus",  # Golfinho-nariz-de-garrafa
    "Leptailurus serval",  # Serval
    "Equus zebra",  # Zebra
    "Lynx pardinus",  # Lince-ibérico
    "Gavialis gangeticus",  # Gavial
    "Manis javanica",  # Pangolim
    "Okapia johnstoni",  # Okapi
    "Cacajao calvus",  # Cacajá-de-cara-preta
    "Tachyglossus aculeatus",  # Equidna
    "Cercopithecus mona",  # Macaco-mona
    "Crocodylus acutus",  # Crocodilo de nariz afilada
    "Neofelis nebulosa",  # Pantera nebulosa
    "Saimiri sciureus",  # Macaco-prego
    "Rangifer tarandus",  # Rena
    "Vombatus ursinus",  # Wombat
    "Bubulcus ibis",  # Garça-vaqueira
    "Falco peregrinus",  # Falcão-peregrino
    "Lepus europaeus",  # Lebre-europeia
    "Phascolarctos cinereus",  # Coala
    "Balaenoptera acutorostrata",  # Baleia minke
    "Equus quagga",  # Zebra
    "Pteropus giganteus",  # Morcego-da-fruta-gigante
    "Dromaius novaehollandiae",  # Emu
    "Cacatua galerita",  # Cacatua-de-crista-amarela
    "Rhea americana",  # Ema
    "Mantis religiosa",  # Louva-a-deus
    "Diomedea exulans",  # Albatroz
    "Eptesicus fuscus",  # Morcego-marrom
    "Marmota monax",  # Marmota
    "Naja naja",  # Naja
    "Anas platyrhynchos",  # Pato-mergulhão
    "Aptenodytes patagonicus",  # Pinguim-imperador
    "Elephas maximus",  # Elefante asiático
    "Phoca vitulina",  # Foca-comum
    "Gorilla beringei",  # Gorila-das-montanhas
    "Chamaeleo chamaeleon",  # Camaleão comum
    "Dendroaspis polylepis",  # Cobra-de-cobertura
    "Lophophorus impejanus",  # Faisão-de-imperador
    "Hydrurga leptonyx",  # Leão-marinho-de-weddell
    "Vulpes vulpes",  # Raposa
    "Pelecanus onocrotalus",  # Pelicano-comum
    "Xenopus laevis",  # Rã-comum
    "Spheniscus demersus",  # Pinguim-de-pintinhas
    "Hippocampus comes",  # Cavalo-marinho
    "Carcharhinus leucas",  # Tubarão-tigre
    "Gavialis gangeticus",  # Gavial
    "Viverra zibetha",  # Civeta
    "Tupinambis teguixin",  # Teiú
    "Canis lupus familiaris",  # Cachorro
    "Hylobates lar",  # Gibão
    "Antilocapra americana",  # Antílopes
    "Cranes",  # Gruas
    "Ctenophora",  # Ctenóforos (medusas)
    "Arctocephalus pusillus",  # Leão-marinho-sul-africano
    "Oryctolagus cuniculus",  # Coelho-europeu
    "Grampus griseus",  # Grampo
    "Naja haje",  # Cobra egípcia
    "Dugong dugon",  # Dugongo
    "Gallus gallus domesticus",  # Galinha
    "Neotoma floridana",  # Rato-almiscarado
    "Dasyurus hallucatus",  # Marsupial
    "Ailurus fulgens",  # Panda vermelho
    "Dendrocygna autumnalis",  # Pato do mato
    "Crocodylus niloticus",  # Crocodilo-do-nilo
    "Ocelot",  # Ocelote
    "Geochelone gigantea",  # Tartaruga-gigante
    "Caracal caracal",  # Caracal
    "Turdus migratorius",  # Sabiá-americano
    "Syrmaticus reevesii",  # Faisão-de-Reeves
    "Ctenophora",  # Ctenóforos (medusas)
    "Zalophus californianus",  # Leão-marinho-da-califórnia
    "Brachiosaurus brancai",  # Brachiossauro
    "Archaeopteryx lithographica",  # Archaeopteryx
    "Pygocentrus nattereri",  # Piranha
    "Chaetodon auriga",  # Peixe-borboleta-de-auriga
    "Bubalus mindorensis",  # Búfalo-de-mindoro
    "Chinchilla lanigera",  # Chinchila
    "Lissotriton vulgaris",  # Tritão-comum
    "Panthera pardus",  # Leopardo
    "Ailuropoda melanoleuca",  # Panda
    "Zalophus californianus",  # Leão-marinho-da-califórnia
    "Tyrannosaurus rex",  # Tyrannossauro
    "Megalodon",  # Megalodon
    "Hippocampus reidi",  # Cavalo-marinho-de-fantasia
    "Chelonia mydas",  # Tartaruga verde
    "Octopus vulgaris",  # Polvo-comum
    "Platanista gangetica",  # Golfinho-do-ganges
    "Anguilla anguilla",  # Enguia-europeia
    "Carcharhinus melanopterus",  # Tubarão-de-pontas-negras
    "Papio anubis",  # Mandril
    "Ceratotherium simum",  # Rinoceronte-branco
    "Diomedea epomophora",  # Albatroz-de-pescoço-de-fios
    "Melursus ursinus",  # Urso-melroso
    "Pinguinus impennis",  # Pinguim-imperador
    "Ailuropoda melanoleuca",  # Panda gigante
    "Naja naja",  # Naja indiana
    "Pteropus vampyrus",  # Morcego-de-fruta-de-grande-portão
    "Sphenodon punctatus",  # Tuatara
    "Tachyglossus aculeatus",  # Equidna de bico longo
    "Vulpes vulpes",  # Raposa vermelha
    "Dendroaspis polylepis",  # Cobra-de-cobertura
    "Vombatus ursinus",  # Wombat
    "Manis javanica",  # Pangolim
    "Neofelis nebulosa",  # Pantera nebulosa
    "Cervus elaphus",  # Cervo-vermelho
    "Lynx lynx",  # Lince-euroasiático
    "Gorilla beringei",  # Gorila-das-montanhas
    "Lynx pardinus",  # Lince-ibérico
    "Okapia johnstoni",  # Okapi
    "Saimiri sciureus",  # Macaco-prego
    "Tarsius syrichta",  # Tarsier
    "Eptesicus fuscus",  # Morcego marrom
    "Orcinus orca",  # Orca
    "Marmota monax",  # Marmota
    "Felis nigripes",  # Gato-de-patas-negras
    "Atelocynus microtis",  # Lobo-de-pico-pequeno
    "Bison bison",  # Bisonte americano
    "Ailuropoda melanoleuca",  # Panda vermelho
    "Ursus maritimus",  # Urso polar
    "Cacatua galerita",  # Cacatua-de-crista-amarela
    "Cacajao calvus",  # Cacajá-de-cara-preta
    "Puma concolor",  # Puma
    "Geochelone gigantea",  # Tartaruga-gigante
    "Tarsius syrichta",  # Tarsier
    "Vulpes vulpes",  # Raposa
    "Xenopus laevis",  # Rã-comum
    "Dromaius novaehollandiae",  # Emu
    "Alces alces",  # Alce
    "Balaenoptera acutorostrata",  # Baleia minke
    "Alectoris rufa",  # Perdiz-vermelha
    "Pygocentrus nattereri",  # Piranha
    "Cochlosoma granulata",  # Caracol-de-grãos
    "Chinchilla lanigera",  # Chinchila
    "Abyssal species",  # Espécies abissais
    "Antilocapra americana",  # Antílopes
    "Chamaeleo chamaeleon",  # Camaleão comum
    "Vespertilionidae",  # Morcego
    "Cyanistes caeruleus",  # Azulão
    "Arctocephalus pusillus",  # Leão-marinho-sul-africano
    "Acinonyx jubatus",  # Guepardo
    "Ceratotherium simum",  # Rinoceronte-branco
    "Syrmaticus reevesii",  # Faisão-de-Reeves
    "Brachiosaurus brancai",  # Brachiossauro
    "Rhacophorus leucomystax",  # Sapo-de-folha
    "Cnemidophorus sexlineatus",  # Lagarto-de-seis-linhas
    "Cochliomyia hominivorax",  # Mosca-varejeira
    "Cranes",  # Gruas
    "Peromyscus leucopus",  # Camundongo-de-cauda-branca
    "Chaetodon auriga",  # Peixe-borboleta-de-auriga
    "Archaeopteryx lithographica",  # Archaeopteryx
    "Xerus erythropus",  # Esquilo-do-deserto
    "Viverra zibetha",  # Civeta
    "Hypsilophodon foxii",  # Hipsilofodonte
    "Crocodylus niloticus",  # Crocodilo-do-nilo
    "Tyrannosaurus rex",  # Tyrannossauro
    "Geochelone elephantopus",  # Tartaruga-gigante-das-galápagos
    "Lasiurus cinereus",  # Morcego-de-cauda-longa
    "Megalodon",  # Megalodon
    "Anguilla anguilla",  # Enguia-europeia
    "Hippocampus reidi",  # Cavalo-marinho-de-fantasia
    "Zalophus californianus",  # Leão-marinho-da-califórnia
    "Dasyurus hallucatus",  # Marsupial
    "Ceratophrys ornata",  # Sapo-de-corno
    "Pelecanus occidentalis",  # Pelicano-pardo
    "Ornithorhynchus anatinus",  # Ornitorrinco
    "Grampus griseus",  # Grampo
    "Anas platyrhynchos",  # Pato-mergulhão
    "Xenopus laevis",  # Rã-comum
    "Echidna",  # Equidna
    "Vombatus ursinus",  # Wombat
    "Tupinambis teguixin",  # Teiú
    "Hylobates lar",  # Gibão
    "Aptenodytes patagonicus",  # Pinguim-imperador
    "Dendrocygna autumnalis",  # Pato do mato
    "Mandrillus sphinx",  # Mandril
    "Pygocentrus nattereri",  # Piranha
    "Tupinambis teguixin",  # Teiú
    "Aptenodytes forsteri",  # Pinguim-imperador
    "Herpestes jaguarundi",  # Jaguarundi
    "Panthera onca",  # Onça-pintada
    "Myrmecophaga tridactyla",  # Tamanduá-bandeira
    "Anodorhynchus hyacinthinus",  # Arara-azul-grande
    "Leontopithecus rosalia",  # Mico-leão-dourado
    "Pygocentrus nattereri",  # Piranha
    "Hydrochoerus hydrochaeris",  # Capivara
    "Blastocerus dichotomus",  # Cervo-do-pantanal
    "Cacicus",  # Cacique
    "Bubalus bubalis",  # Búfalo
    "Callithrix aurita",  # Mico-estrela
    "Ateles chamek",  # Caiçara
    "Sus scrofa",  # Javali
    "Caiman yacare",  # Jacaré-do-pantanal
    "Tamandua tetradactyla",  # Tamanduá-mirim
    "Ramphastos toco",  # Tucano-toco
    "Tolypeutes tricinctus",  # Tatu-bola
    "Tapirus terrestris",  # Anta
    "Alouatta caraya",  # Guariba
    "Rhea americana",  # Nandú
    "Ara ararauna",  # Arara-canindé
    "Puma concolor",  # Puma
    "Harpia harpyja",
    "Macrocercus tucumanus",  # Periquito-de-tucumã
    "Sphiggurus spinosus",  # Caviúna
    "Chaetomys subspinosus",  # Rato-do-mato
    "Maned wolf",  # Lobo-guará
    "Eira barbara",  # Irara
    "Prionailurus bengalensis",  # Gato-do-mato
    "Cuniculus paca",  # Paca
    "Dromaius novaehollandiae",  # Emu
    "Vultur gryphus",  # Condor
    "Crotalus durissus",  # Cascavel
    "Bothrops asper",  # Jararaca
    "Lonomia obliqua",  # Lonomia
    "Brachyteles arachnoides",  # Muriqui-do-sul
    "Pithecia pithecia",  # Macaco-uakari
    "Cynomys ludovicianus",  # Marmota
    "Anolis chrysolepis",  # Anolis-de-cauda-verde
    "Dendrobates tinctorius",  # Sapo-de-fogo
    "Arapaima gigas",  # Arapaima
    "Hippocampus reidi",  # Cavalo-marinho-do-brazil
    "Mastigodryas boddaerti",  # Cobra-de-duas-cabeças
    "Salminus brasiliensis",  # Dourado
    "Corydoras paleatus",  # Cascudo
    "Colossoma macropomum",  # Tambaqui
    "Tucuxi",  # Golfinho-do-rio-amazônico
    "Botos",  # Golfinho-do-amazonas
    "Erythrolamprus aesculapii",  # Cobra-de-pau
    "Agama agama",  # Lagarto-agama
    "Lepidobatrachus asper",  # Sapo-de-barriga-verde
    "Tupinambis teguixin",  # Teiú
    "Parabuteo unicinctus",  # Gavião-carijó
    "Brachyteles arachnoides",  # Muriqui
    "Felis nigripes",  # Gato-preto
    "Gallus gallus domesticus",  # Galinha
    "Ctenomys",  # Tuco-tuco
    "Microcercus pennantii",  # Calopsita
    "Dendrocygna autumnalis",  # Pato-mergulhão
    "Neotropical otter",  # Lontra
    "Pecari tajacu",  # Queixada
    "Cuniculus paca",  # Paca
    "Echymipera rufescens",  # Echymipera
    "Leptodactylus labyrinthicus",  # Sapo-labirinto
    "Ranitomeya reticulata",  # Sapo-dart-de-pontos
    "Stryphnodendron rotundifolium",  # Stryphnodendron
    "Pseudoplatystoma corruscans",  # Pintado
    "Trachemys dorbigni",  # Cágado
    "Brachycephalus ephippium",  # Sapo-de-ombro
    "Aspidoscelis lineattissima",  # Lagarto
    "Rhinella marina",  # Sapo-cururu
    "Agkistrodon piscivorus",  # Cobra-de-água
    "Erythrolamprus aesculapii",  # Cobra-de-pau
    "Geranoaetus albicaudatus"  # Gavião-real
]


iucn_translation = {
    "Extinct": "Extinto",
    "Extinct in the Wild": "Extinta na natureza",
    "Critically Endangered": "Em perigo crítico",
    "Endangered": "Em perigo",
    "Vulnerable": "Vulnerável",
    "Near Threatened": "Quase ameaçada",
    "Conservation Dependent": "Dependente de conservação",
    "Least Concern": "Pouco preocupante",
    "Data Deficient": "Deficiência de dados",
    "Not Evaluated": "Não avaliada"
}


def get_animal_data(scientific_name):
    ingles = False

    animal_data = {
        "scientific_name": scientific_name,
        "common_name": None,
        "image_url": None,
        "native_range": None,
        "iucn_status": "Não disponível",
        "description": None
    }


    wiki_url_pt = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
    wiki_response = requests.get(wiki_url_pt)

    if wiki_response.status_code == 200:
        wiki_data = wiki_response.json()
        animal_data["description"] = (wiki_data.get("extract", None))
        

        if wiki_data.get("title") == "Not found.":
            ingles = True
            wiki_url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
            wiki_response = requests.get(wiki_url_en)
            if wiki_response.status_code == 200:
                wiki_data = wiki_response.json()
            else:
                return None  
            animal_data["description"] = translator.translate(wiki_data.get("extract", None), src='en', dest='pt').text
        elif "title" not in wiki_data:
            return None  
    else:
        
        wiki_url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
        
        wiki_response = requests.get(wiki_url_en)
        if wiki_response.status_code == 200:
            wiki_data = wiki_response.json()
            animal_data["description"] = translator.translate(wiki_data.get("extract", None), src='en', dest='pt').text
        else:
            return None 
        



    animal_data["common_name"] = wiki_data.get("title")
    animal_data["image_url"] = wiki_data.get("thumbnail", {}).get("source", None)
    
    


    if animal_data["description"]:
        animal_data["description"] = animal_data["description"].replace(" ;", "; ")
        animal_data["description"] = re.sub(r';(?=\S)', '; ', animal_data["description"])
        animal_data["description"] = animal_data["description"].replace("\xa0", " ")
        


    gbif_url = "https://api.gbif.org/v1/occurrence/search"
    params = {
        "limit": 1,
        "scientificName": scientific_name
    }
    gbif_response = requests.get(gbif_url, params=params)
    if gbif_response.status_code == 200:
        gbif_data = gbif_response.json()
        if gbif_data["results"]:
            species_data = gbif_data["results"][0]
            animal_data["native_range"] = species_data.get("country", "Não disponível")
            iucn_status = species_data.get("iucnRedListCategory", "Não disponível")
            if iucn_status == "Não disponível":
                animal_data["iucn_status"] = iucn_status

    if animal_data["iucn_status"] == "Não disponível":
        wiki_page_url = f"https://pt.wikipedia.org/wiki/{scientific_name.replace(' ', '_')}"
        wiki_page_response = requests.get(wiki_page_url)
        if wiki_page_response.status_code == 200:
            soup = BeautifulSoup(wiki_page_response.content, "html.parser")
            iucn_links = soup.find_all("a", string=re.compile(".*(Vulnerável|Em perigo|Em perigo crítico|Extinta na natureza|Pouco preocupante|Deficiência de dados|Extinto|Quase ameaçada|Não avaliada|Dependente de conservação).*", re.IGNORECASE))

            if iucn_links:
                animal_data["iucn_status"] = iucn_links[0].text.strip()
            else:
                wiki_page_url = f"https://en.wikipedia.org/wiki/{scientific_name.replace(' ', '_')}"
                wiki_page_response = requests.get(wiki_page_url)
                soup = BeautifulSoup(wiki_page_response.content, "html.parser")
                iucn_links2 = soup.find_all("a", string=re.compile(".*(Extinct|Extinct in the Wild|Critically Endangered|Endangered|Near Threatened|Conservation Dependent|Least Concern|Data Deficient|Not Evaluated).*", re.IGNORECASE))
                if iucn_links2:
                    english_status = iucn_links2[0].text.strip()
                    animal_data["iucn_status"] = iucn_translation.get(english_status, english_status)

    
    return animal_data


def get_random_animal():
    return random.choice(animal_names) 


while True:
    random_animal = get_random_animal()  # Pega um animal aleatório
    print(f"Buscando informações para o animal: {random_animal}")
    animal_info = get_animal_data(random_animal)  # Obtém as informações

    if animal_info and animal_info["iucn_status"] != "Não disponível":
        print(animal_info)  # Exibe as informações se encontrar o IUCN status válido
        break  # Sai do loop quando os dados forem válidos
    else:
        print("O animal não tem status IUCN disponível. Tentando o próximo...")  # Mensagem caso o status não seja encontrado
