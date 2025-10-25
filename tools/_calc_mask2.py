CLASSES = [
    'Lutador','Guerreiro','Berzerker','Paladino','Titan','Templario','Cavaleiro da Morte','Cavaleiro Real','Destruidor','Cavaleiro Sagrado',
    'Cacador','Arqueiro','Ranger','Assassin','Franco Atirador','Sicario Sombrio','Mercenario','Ninja','Predador','Shinobi',
    'Acolito','Sacerdote','Clerigo','Sabio','Profeta','Mistico','Mensageiro Divino','Xama','Arcanjo','Druida',
    'Bruxo','Mago','Feiticeiro','Necromante','Arquimago','Demonologo','Arcano','Emissario dos Mortos','Shinigami',
    'Maquinista Aprendiz','Maquinista','Agressor','Demolidor','Prime','Optimus','Megatron','Galvatron','Omega','Titan Celeste',
    'Viajante','Nomade','Espadachim','Ilusionista','Samurai','Augure','Ronin','Oraculo','Mestre Dimensional','Cronos'
]
names = ['Guerreiro','Paladino','Templario','Cavaleiro Real','Cavaleiro Sagrada']
inds = [CLASSES.index(n) for n in names]
mask = 0
for i in inds:
    mask |= (1<<i)
print('names:', names)
print('indices:', inds)
print('mask hex:', hex(mask))
print('mask dec:', mask)
