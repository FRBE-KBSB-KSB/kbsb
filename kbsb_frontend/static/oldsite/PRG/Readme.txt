WARNING – ATTENTION – ACHTUNG - PAS OP!

Répertoire d'installation
=========================
Lors de l’installation, l'utilisateur peut changer la partition d'installation de Chess Manager. Le chemin d'installation par défaut est C:\ChessMan. Pour diverses raisons, il n'est pas souhaitable de modifier ce chemin, à la rigueur, la partition de destination, soit D:\ChessMan, E:\ChessMan, etc.,... peuvent convenir. En somme, ChessMan doit être installé à la racine d'une partition du disque dur.

Durant l'installation
=====================
Accepter la création du répertoire destiné à accueillir le BDE. En cas de problèmes il peut être nécessaire de supprimer manuellement ce répertoire et de renouveller l'installation.

Configuration du BDE
====================
Après l’installation de Chess Manager, le BDE doit être configuré correctement, sinon une erreur s'affichera lors du lancement de Chess Manager.
Le BDE, c’est le moteur de recherche en base de données utilisé par Chess Manager.

1) Un premier paramètre, l'alias <ChessMan> dont le chemin est par défaut défini à C:\ChessMan, le répertoire d'installation initial n'a besoin d'aucune intervention SAUF SI l'intallation a été réalisée sur une autre partition, dans ce cas le path de cet alias doit être ajusté en conséquence - voir procédure de configuration manuelle ci-dessous. 

2) Le pilote natif DBase n'a pas besoin d'être configuré par défaut. Si nécessaire, voir procédure de configuration manuelle ci-dessous.

Configuration manuelle du BDE
=============================

En cas de problème, la configuration peut également se faire avec l’"Administrateur BDE", situé dans le répertoire C:\Program Files\Fichiers communs\Borland Shared\BDE ou C:\ProgramFiles\Commons Files\Borland Shared\BDE (suivant la langue de votre système d’exploitation). Pour lancer cet administreur, parcourir les répertoires indiqués et faire un clic droit sur l'exécutable <bdeadmin.exe>, opter pour "Exécuter en tant qu'administrateur", effectuer les règlages comme indiqués ici:

1) Onglet Bases de Données: définition de l'ALIAS: dans la colonne de gauche, cliquer sur le + de Bases de données de façon à déployer l'arborescence. L'alias ChessMan doit y être présent. Si cet alias ChessMan est absent il faut le créer en cliquant avec le bouton droit de la souris dans la colonne de gauche et cliquer Nouveau. Une petite boite "Nouvel alias base de données" apparait, cliquer sur OK sans rien changer. Un nouvel ALIAS est maintenant présent dans la colonne de gauche et il faut le renommer en "ChessMan". Une fois l'alias ChessMan créé, le sélecter et dans la partie droite de la fenètre ajuster les paramètres de cet alias ChessMan, comme ceci:

    Type:               STANDARD
    DEFAULT DRIVER:     DBASE
    ENABLE BCD:         FALSE
    PATH:               C:\ChessMan

2) Onglet Configuration: déployer l'arborescence en cliquant sur le + de Configuration, sur le + de Pilotes, sur le + de Natif et cliquer sur DBASE. Ajustez les paramètres de DBASE comme ceci:

    VERSION:              4.0
    TYPE:                 FILE
    LANGDRIVER:           dBASE FRA cp850
    LEVEL:                4
    MDX BLOCK SIZE:       1024
    MEMO FILE BLOCK SIZE: 1024

Accepter l’enregistrement des modifications en quittant l’administrateur BDE, en cliquant directement sur la croix X dans le coin supérieur droit de la fenètre. La sauvegarde est automatique. Notez que l'on peut aussi accéder à cet outil de configuration du BDE par le « panneau de configuration », cet accès n'est pas recommandé puisque non exécuté en mode administrateur. 

Fichier d'aide
==============
Windows Vista et 7 ne prennent pas en charge l'affichage des fichiers d'aide .HLP.¨Pout y remédier, exécutez l'un des 2 fichiers du répertoire WinHlp32 suivant que votre système d'exploitation est en 32 bits ou en 64 bits.

En cas de doute, me contacter au 0497/23.43.64 ou 085/31.43.03 ou par mail Halleux.Daniel@gmail.com