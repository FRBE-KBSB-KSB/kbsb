WARNING � ATTENTION � ACHTUNG - PAS OP!

R�pertoire d'installation
=========================
Lors de l�installation, l'utilisateur peut changer la partition d'installation de Chess Manager. Le chemin d'installation par d�faut est C:\ChessMan. Pour diverses raisons, il n'est pas souhaitable de modifier ce chemin, � la rigueur, la partition de destination, soit D:\ChessMan, E:\ChessMan, etc.,... peuvent convenir. En somme, ChessMan doit �tre install� � la racine d'une partition du disque dur.

Durant l'installation
=====================
Accepter la cr�ation du r�pertoire destin� � accueillir le BDE. En cas de probl�mes il peut �tre n�cessaire de supprimer manuellement ce r�pertoire et de renouveller l'installation.

Configuration du BDE
====================
Apr�s l�installation de Chess Manager, le BDE doit �tre configur� correctement, sinon une erreur s'affichera lors du lancement de Chess Manager.
Le BDE, c�est le moteur de recherche en base de donn�es utilis� par Chess Manager.

1) Un premier param�tre, l'alias <ChessMan> dont le chemin est par d�faut d�fini � C:\ChessMan, le r�pertoire d'installation initial n'a besoin d'aucune intervention SAUF SI l'intallation a �t� r�alis�e sur une autre partition, dans ce cas le path de cet alias doit �tre ajust� en cons�quence - voir proc�dure de configuration manuelle ci-dessous. 

2) Le pilote natif DBase n'a pas besoin d'�tre configur� par d�faut. Si n�cessaire, voir proc�dure de configuration manuelle ci-dessous.

Configuration manuelle du BDE
=============================

En cas de probl�me, la configuration peut �galement se faire avec l�"Administrateur BDE", situ� dans le r�pertoire C:\Program Files\Fichiers communs\Borland Shared\BDE ou C:\ProgramFiles\Commons Files\Borland Shared\BDE (suivant la langue de votre syst�me d�exploitation). Pour lancer cet administreur, parcourir les r�pertoires indiqu�s et faire un clic droit sur l'ex�cutable <bdeadmin.exe>, opter pour "Ex�cuter en tant qu'administrateur", effectuer les r�glages comme indiqu�s ici:

1) Onglet Bases de Donn�es: d�finition de l'ALIAS: dans la colonne de gauche, cliquer sur le + de Bases de donn�es de fa�on � d�ployer l'arborescence. L'alias ChessMan doit y �tre pr�sent. Si cet alias ChessMan est absent il faut le cr�er en cliquant avec le bouton droit de la souris dans la colonne de gauche et cliquer Nouveau. Une petite boite "Nouvel alias base de donn�es" apparait, cliquer sur OK sans rien changer. Un nouvel ALIAS est maintenant pr�sent dans la colonne de gauche et il faut le renommer en "ChessMan". Une fois l'alias ChessMan cr��, le s�lecter et dans la partie droite de la fen�tre ajuster les param�tres de cet alias ChessMan, comme ceci:

    Type:               STANDARD
    DEFAULT DRIVER:     DBASE
    ENABLE BCD:         FALSE
    PATH:               C:\ChessMan

2) Onglet Configuration: d�ployer l'arborescence en cliquant sur le + de Configuration, sur le + de Pilotes, sur le + de Natif et cliquer sur DBASE. Ajustez les param�tres de DBASE comme ceci:

    VERSION:              4.0
    TYPE:                 FILE
    LANGDRIVER:           dBASE FRA cp850
    LEVEL:                4
    MDX BLOCK SIZE:       1024
    MEMO FILE BLOCK SIZE: 1024

Accepter l�enregistrement des modifications en quittant l�administrateur BDE, en cliquant directement sur la croix X dans le coin sup�rieur droit de la fen�tre. La sauvegarde est automatique. Notez que l'on peut aussi acc�der � cet outil de configuration du BDE par le � panneau de configuration �, cet acc�s n'est pas recommand� puisque non ex�cut� en mode administrateur. 

Fichier d'aide
==============
Windows Vista et 7 ne prennent pas en charge l'affichage des fichiers d'aide .HLP.�Pout y rem�dier, ex�cutez l'un des 2 fichiers du r�pertoire WinHlp32 suivant que votre syst�me d'exploitation est en 32 bits ou en 64 bits.

En cas de doute, me contacter au 0497/23.43.64 ou 085/31.43.03 ou par mail Halleux.Daniel@gmail.com