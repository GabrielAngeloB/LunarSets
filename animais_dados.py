import gevent.monkey
gevent.monkey.patch_all()
from gevent import monkey
monkey.patch_all(ssl=False)
import requests
from bs4 import BeautifulSoup
from db_connection import create_connection, close_connection
from googletrans import Translator
from flask import session, flash, redirect, url_for
from conquistas import Conquistas
import re
import random
import ssl
from urllib3.poolmanager import PoolManager
from urllib3 import HTTPSConnectionPool
import sys


context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # Força ciphers mais fracos, caso necessário
sys.setrecursionlimit(2000)


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
    "Zalophus californianus",  # Leão-marinho-da-califórnia
    "Chaetodon auriga",  # Peixe-borboleta-de-auriga
    "Bubalus mindorensis",  # Búfalo-de-mindoro
    "Chinchilla lanigera",  # Chinchila
    "Lissotriton vulgaris",  # Tritão-comum
    "Panthera pardus",  # Leopardo
    "Ailuropoda melanoleuca",  # Panda
    "Megalodon",  # Megalodon
    "Hippocampus reidi",  # Cavalo-marinho-de-fantasia
    "Octopus vulgaris",  # Polvo-comum
    "Platanista gangetica",  # Golfinho-do-ganges
    "Anguilla anguilla",  # Enguia-europeia
    "Carcharhinus melanopterus",  # Tubarão-de-pontas-negras
    "Papio anubis",  # Mandril
    "Ceratotherium simum",  # Rinoceronte-branco
    "Diomedea epomophora",  # Albatroz-de-pescoço-de-fios
    "Melursus ursinus",  # Urso-melroso
    "Pinguinus impennis",  # Pinguim-imperador
    "Naja naja",  # Naja indiana
    "Pteropus vampyrus",  # Morcego-de-fruta-de-grande-portão
    "Tachyglossus aculeatus",  # Equidna de bico longo
    "Tarsius syrichta",  # Tarsier
    "Eptesicus fuscus",  # Morcego marrom
    "Orcinus orca",  # Orca
    "Felis nigripes",  # Gato-de-patas-negras
    "Atelocynus microtis",  # Lobo-de-pico-pequeno
    "Ailuropoda melanoleuca",  # Panda vermelho
    "Alces alces",  # Alce
    "Alectoris rufa",  # Perdiz-vermelha
    "Cochlosoma granulata",  # Caracol-de-grãos
    "Abyssal species",  # Espécies abissais
    "Vespertilionidae",  # Morcego
    "Cyanistes caeruleus",  # Azulão
    "Acinonyx jubatus",  # Guepardo
    "Rhacophorus leucomystax",  # Sapo-de-folha
    "Cnemidophorus sexlineatus",  # Lagarto-de-seis-linhas
    "Cochliomyia hominivorax",  # Mosca-varejeira
    "Peromyscus leucopus",  # Camundongo-de-cauda-branca
    "Xerus erythropus",  # Esquilo-do-deserto
    "Hypsilophodon foxii",  # Hipsilofodonte
    "Tyrannosaurus rex",  # Tyrannossauro
    "Geochelone elephantopus",  # Tartaruga-gigante-das-galápagos
    "Lasiurus cinereus",  # Morcego-de-cauda-longa
    "Ceratophrys ornata",  # Sapo-de-corno
    "Pelecanus occidentalis",  # Pelicano-pardo
    "Ornithorhynchus anatinus",  # Ornitorrinco
    "Echidna",  # Equidna
    "Mandrillus sphinx",  # Mandril
    "Aptenodytes forsteri",  # Pinguim-imperador
    "Herpestes jaguarundi",  # Jaguarundi
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
    "Harpia harpyja",
    "Macrocercus tucumanus",  # Periquito-de-tucumã
    "Sphiggurus spinosus",  # Caviúna
    "Chaetomys subspinosus",  # Rato-do-mato
    "Eira barbara",  # Irara
    "Prionailurus bengalensis",  # Gato-do-mato
    "Cuniculus paca",  # Paca
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
    "Parabuteo unicinctus",  # Gavião-carijó
    "Brachyteles arachnoides",  # Muriqui
    "Felis nigripes",  # Gato-preto
    "Ctenomys",  # Tuco-tuco
    "Microcercus pennantii",  # Calopsita
    "Dendrocygna autumnalis",  # Pato-mergulhão
    "Neotropical otter",  # Lontra
    "Pecari tajacu",  # Queixada
    "Echymipera rufescens",  # Echymipera
    "Leptodactylus labyrinthicus",  # Sapo-labirinto
    "Ranitomeya reticulata",  # Sapo-dart-de-pontos
    "Pseudoplatystoma corruscans",  # Pintado
    "Trachemys dorbigni",  # Cágado
    "Brachycephalus ephippium",  # Sapo-de-ombro
    "Aspidoscelis lineattissima",  # Lagarto
    "Rhinella marina",  # Sapo-cururu
    "Agkistrodon piscivorus",  # Cobra-de-água
    "Geranoaetus albicaudatus",
    "Equus ferus przewalskii",  # Cavalo-de-przewalski
    "Bison bonasus",  # Bisonte-europeu
    "Panthera leo persica",  # Leão asiático
    "Lycaon pictus",  # Mabeco
    "Ursus arctos horribilis",  # Urso-pardo-de-kodiak
    "Acipenser transmontanus",  # Esturjão-branco
    "Phoenicopterus roseus",  # Flamingo
    "Pygocentrus cariba",  # Piranha-negra
    "Phocoena phocoena",  # Toninha-comum
    "Tachyglossus aculeatus",  # Equidna-de-bico-curto
    "Mesocricetus auratus",  # Hamster-sírio
    "Eleutherodactylus coqui",  # Coqui
    "Alces alces americanus",  # Alce-americano
    "Cygnus atratus",  # Cisne-negro
    "Phoebastria albatrus",  # Albatroz-de-cauda-curta
    "Potos flavus",  # Jupará
    "Phyllobates terribilis",  # Sapo-dourado-venenoso
    "Desmodus rotundus",  # Morcego-vampiro-comum
    "Tremarctos ornatus",  # Urso-de-óculos
    "Vicugna vicugna",  # Vicuña
    "Castor canadensis",  # Castor-americano
    "Hippocampus kuda",  # Cavalo-marinho-de-focinho-curto
    "Mustela putorius furo",  # Furão-doméstico
    "Dasypus novemcinctus",  # Tatu-galinha
    "Nasua nasua",  # Quati
    "Choloepus hoffmanni",  # Preguiça-de-dois-dedos
    "Condylura cristata",  # Toupeira-de-estrela
    "Ambystoma mexicanum",  # Axolote
    "Sarcophilus harrisii",  # Diabo-da-tasmânia
    "Cervus nippon",  # Cervo-do-sika
    "Psittacus erithacus",  # Papagaio-cinzento
    "Lagopus lagopus",  # Lagópode-do-sapinho
    "Equus africanus asinus",  # Jumento
    "Pecari maximus",  # Queixada
    "Oryx dammah",  # Órix-do-saara
    "Hydrodamalis gigas",  # Vaca-marinha-de-steller
    "Atelopus zeteki",  # Sapo-dourado-do-panamá
    "Tursiops aduncus",  # Golfinho-pontilhado
    "Diceros bicornis",  # Rinoceronte-negro
    "Oncorhynchus tshawytscha",  # Salmão-rei
    "Acinonyx jubatus venaticus",  # Guepardo-asiático
    "Felis margarita",  # Gato-do-deserto
    "Sphenodon guntheri",  # Tuatara-broda
    "Pan troglodytes schweinfurthii",  # Chimpanzé-oriental
    "Delphinus capensis",  # Golfinho-de-bico-comprido
    "Spheniscus humboldti",  # Pinguim-de-humboldt
    "Vicugna pacos",  # Alpaca
    "Alouatta pigra",  # Bugio-preto
    "Lemur catta",  # Lêmure-de-cauda-anelada
    "Pan paniscus",  # Bonobo
    "Physeter macrocephalus",  # Cachalote
    "Condor californianus",  # Condor-da-califórnia
    "Bradypus tridactylus",  # Preguiça-de-três-dedos
    "Canis lupus arctos",  # Lobo-do-ártico
    "Chlamyphorus truncatus",  # Tatu-rosa
    "Pygoscelis papua",  # Pinguim-gentoo
    "Brachyteles hypoxanthus",  # Muriqui-do-norte
    "Antidorcas marsupialis",  # Springbok
    "Thalassarche melanophrys",
    "Panthera pardus orientalis",  # Leopardo-de-amur
    "Phocoena phocoena",  # Boto-comum
    "Alouatta seniculus",  # Bugio-vermelho
    "Arctocephalus forsteri",  # Lobo-marinho-neozelandês
    "Capra ibex",  # Ibex alpino
    "Anser caerulescens",  # Ganso-das-neves
    "Corvus corax",  # Corvo-comum
    "Eulemur fulvus",  # Lêmure-marrom
    "Tarsius tarsier",  # Tarsius indonésio
    "Lutra lutra",  # Lontra-europeia
    "Delphinapterus leucas",  # Beluga
    "Arctictis binturong",  # Binturong
    "Caluromys philander",  # Cuíca-das-palmeiras
    "Ardea alba",  # Garça-branca-grande
    "Ailurus fulgens",  # Panda-vermelho
    "Melursus ursinus",  # Urso-beiçudo
    "Glyptemys insculpta",  # Tartaruga-esculpida
    "Bison bonasus",  # Bisão-europeu
    "Apteryx mantelli",  # Kiwi-da-ilha-norte
    "Cacatua sulphurea",  # Cacatua-de-crista-amarela
    "Marmota marmota",  # Marmota alpina
    "Procyon lotor",  # Guaxinim
    "Chelonoidis nigra",  # Tartaruga-de-galápagos
    "Cervus nippon",  # Veado-sika
    "Cervus canadensis",  # Alce-americano
    "Potorous tridactylus",  # Potoroo-de-cabeça-preta
    "Ovis aries",  # Carneiro
    "Aepyceros melampus",  # Impala
    "Panthera uncia",  # Leopardo-das-neves
    "Odobenus rosmarus",  # Morsa
    "Spheniscus demersus",  # Pinguim-africano
    "Chaetophractus villosus",  # Tatu-peludo
    "Hystrix cristata",  # Porco-espinho-africano
    "Ctenomys mendocinus",  # Tuco-tuco-das-andes
    "Orcaella brevirostris",  # Golfinho-de-irrawaddy
    "Lagostomus maximus",  # Viscacha
    "Procavia capensis",  # Daman-do-cabo
    "Alouatta caraya",  # Bugio-preto
    "Monodon monoceros",  # Narval
    "Syncerus caffer",  # Búfalo-africano
    "Pteropus vampyrus",  # Morcego-gigante
    "Cervus canadensis nelsoni",  # Alce-das-rochosas
    "Macropus rufus",  # Canguru-vermelho
    "Castor fiber",  # Castor-europeu
    "Panthera leo persica",  # Leão-asiático
    "Vulpes lagopus",  # Raposa-do-ártico
    "Saimiri sciureus",  # Macaco-de-cara-branca
    "Echinosorex gymnura",  # Musaranho-da-malásia
    "Canis lupus arctos",  # Lobo-ártico
    "Anas acuta",  # Marreco-rabudo
    "Bison bison athabascae",  # Bisão-da-floresta
    "Papio hamadryas",  # Babuíno-hamadryas
    "Canis lupus signatus",  # Lobo-ibérico
    "Carcharhinus longimanus",  # Tubarão-oceânico-de-pontas-brancas
    "Manis gigantea",  # Pangolim-gigante
    "Amazona aestiva",  # Papagaio-verdadeiro
    "Pongo abelii",  # Orangotango-de-sumatra
    "Ailurus fulgens styani",  # Panda-vermelho-do-styan
    "Ursus thibetanus",  # Urso-do-himalaia
    "Crocuta crocuta",  # Hiena-malhada
    "Pteropus giganteus",  # Morcego-das-frutas-indiano
    "Eulemur coronatus",  # Lêmure-coroado
    "Ateles paniscus",  # Macaco-aranha
    "Gallus gallus domesticus",  # Galinha-doméstica
    "Mustela putorius furo",  # Furão
    "Nanger dama",  # Gazela-dama
    "Ursus americanus",  # Urso-negro-americano
    "Saimiri boliviensis",  # Macaco-esquilo
    "Eunectes murinus",  # Sucuri
    "Lepus americanus",  # Lebre-americana
    "Camelus bactrianus",  # Camelo-bactriano
    "Anser anser",  # Ganso-comum
    "Gymnogyps californianus",  # Condor-da-califórnia
    "Nasua nasua",  # Quati-de-cauda-anelada
    "Phoenicopterus roseus",  # Flamingo-rosa
    "Oreamnos americanus",  # Cabra-das-montanhas
    "Acerodon jubatus",  # Raposa-voadora-das-filipinas
    "Panthera leo melanochaita",  # Leão-do-kalahari
    "Ailuropoda melanoleuca",  # Panda-gigante
    "Lontra canadensis",  # Lontra-do-norte
    "Phoebastria immutabilis",  # Albatroz-de-pés-pretos
    "Gorilla beringei beringei",  # Gorila-das-montanhas
    "Eubalaena australis",  # Baleia-franca-austral
    "Rhinoceros unicornis",  # Rinoceronte-indiano
    "Falco sparverius",  # Gaviãozinho
    "Phoca groenlandica",  # Foca-do-gelo
    "Pan troglodytes verus",  # Chimpanzé-ocidental
    "Hydrurga leptonyx",  # Foca-leopardo
    "Canis lupus lycaon",  # Lobo-oriental
    "Spheniscus mendiculus",  # Pinguim-das-galápagos
    "Crocodylus porosus",  # Crocodilo-de-água-salgada
    "Equus quagga burchellii",  # Zebra-de-burchell
    "Cercopithecus neglectus",  # Macaco-de-braços-brancos
    "Macaca sylvanus",  # Macaco-de-gibraltar
    "Cebus apella",  # Macaco-prego
    "Ursus maritimus",  # Urso-polar
    "Ursus arctos horribilis",  # Urso-pardo-da-américa-do-norte
    "Neofelis nebulosa",  # Pantera-nebulosa
    "Elephas maximus",
    "Euphractus sexcinctus",  # Tatu-peba
    "Lutra longicaudis",  # Lontra-neotropical
    "Megaptera novaeangliae",  # Baleia-jubarte
    "Capra aegagrus hircus",  # Cabra-doméstica
    "Ornithorhynchus anatinus",  # Ornitorrinco
    "Phacochoerus africanus",  # Javali-africano
    "Atheris hispida",  # Víbora-arborícola
    "Cebus apella",  # Macaco-prego
    "Sarcophilus harrisii",  # Diabo-da-tasmânia
    "Canis lupus signatus",  # Lobo-ibérico  # Albatroz-de-sobrancelha-preta  # Gavião-real
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

translator = Translator()

iucn_english = [
    "Extinct",
    "Extinct in the Wild",
    "Critically Endangered",
    "Endangered",
    "Vulnerable",
    "Near Threatened",
    "Conservation Dependent",
    "Least Concern",
    "Data Deficient",
    "Not Evaluated"
]

iucn_portuguese = [
    "Extinto",
    "Extinta na natureza",
    "Em perigo crítico",
    "Em perigo",
    "Vulnerável",
    "Quase ameaçada",
    "Dependente de conservação",
    "Pouco preocupante",
    "Deficiência de dados",
    "Não avaliada"
]


class dadosAnimal():

    
    def get_random_animal():
        return random.choice(animal_names) 

    

# Lista de exemplos de nomes científicos de animais



    def get_animal_data(scientific_name):
        animal_data = {
            "scientific_name": scientific_name,
            "common_name": None,
            "image_url": None,
            "native_range": None,
            "iucn_status": "Não disponível",
            "description": None
        }
        

        wiki_url_pt = f"http://pt.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
        wiki_response = requests.get(wiki_url_pt, verify=False)

        if wiki_response.status_code == 200:
            wiki_data = wiki_response.json()
            animal_data["description"] = (wiki_data.get("extract", None))


            if wiki_data.get("title") == "Not found.":
                wiki_url_en = f"http://en.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
                wiki_response = requests.get(wiki_url_en, verify=False)
                if wiki_response.status_code == 200:
                    wiki_data = wiki_response.json()
                    animal_data["description"] = translator.translate(wiki_data.get("extract", None), src='en', dest='pt').text
                    animal_data["common_name"] = wiki_data.get("title")
                else:
                    print("erro") 


            elif "title" not in wiki_data:
                print("Titulo não encontrado")
        else:
            
            wiki_url_en = f"http://en.wikipedia.org/api/rest_v1/page/summary/{scientific_name.replace(' ', '_')}"
            
            wiki_response = requests.get(wiki_url_en, verify=False)
            if wiki_response.status_code == 200:
                wiki_data = wiki_response.json()
                animal_data["description"] = translator.translate(wiki_data.get("extract", None), src='en', dest='pt').text
            else:
                animal_data["description"] = "Não disponível"
            



        animal_data["common_name"] = wiki_data.get("title")
        animal_data["image_url"] = wiki_data.get("thumbnail", {}).get("source", None)
        
        


        if animal_data["description"]:
            animal_data["description"] = animal_data["description"].replace(" ;", "; ")
            animal_data["description"] = re.sub(r';(?=\S)', '; ', animal_data["description"])
            animal_data["description"] = animal_data["description"].replace("\xa0", " ")
            


        gbif_url = "http://api.gbif.org/v1/occurrence/search"
        params = {
            "limit": 1,
            "scientificName": scientific_name
        }
        gbif_response = requests.get(gbif_url, params=params, verify=False)
        if gbif_response.status_code == 200:
            gbif_data = gbif_response.json()
            if gbif_data["results"]:
                species_data = gbif_data["results"][0]
                animal_data["native_range"] = species_data.get("country", "Não disponível")
                iucn_status = species_data.get("iucnRedListCategory", "Não disponível")
                if iucn_status == "Não disponível":
                    animal_data["iucn_status"] = iucn_status

        if animal_data["iucn_status"] == "Não disponível":
            wiki_page_url = f"http://pt.wikipedia.org/wiki/{scientific_name.replace(' ', '_')}"
            wiki_page_response = requests.get(wiki_page_url, verify=False)
            if wiki_page_response.status_code == 200:
                soup = BeautifulSoup(wiki_page_response.content, "html.parser")
                iucn_links = soup.find_all("a", string=re.compile(".*(Vulnerável|Em perigo|Em perigo crítico|Extinta na natureza|Pouco preocupante|Deficiência de dados|Extinto|Quase ameaçada|Não avaliada|Dependente de conservação).*", re.IGNORECASE))

                if iucn_links:
                    animal_data["iucn_status"] = iucn_links[0].text.strip()
                else:
                    wiki_page_url = f"http://en.wikipedia.org/wiki/{scientific_name.replace(' ', '_')}"
                    wiki_page_response = requests.get(wiki_page_url, verify=False)
                    soup = BeautifulSoup(wiki_page_response.content, "html.parser")
                    iucn_links2 = soup.find_all("a", string=re.compile(".*(Extinct|Extinct in the Wild|Critically Endangered|Endangered|Near Threatened|Conservation Dependent|Least Concern|Data Deficient|Not Evaluated).*", re.IGNORECASE))
                    if iucn_links2:
                        english_status = iucn_links2[0].text.strip()
                        animal_data["iucn_status"] = iucn_translation.get(english_status, "Status desconhecido")


        return animal_data






    