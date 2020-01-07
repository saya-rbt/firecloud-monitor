
#Fonctionnement simulateur (First Step)

##Boucle de fonctionnement

Le simulateur effectue une vérification de l'état toutes les 5 secondes

##Création d'un nouveau feu

Le simulateur génère un feu toutes les 10 secondes

##Amplification d'un feu

Si aucune intervention, Up toutes les 30 sec

Si invervention, Up toutes les 60 sec

Si intervention equal puissance, pas d'évolution 

##Atténuation d'un feu

Si intervention supp à puissance du feu, reduction feu toutes les 5 secondes

##Extinction d'un feu

Si feu atteint une force de 0, feu éteint

#Fonctionnement manager

##Boucle de fonctionnement

Le manager update toutes les 10 secondes pour suivre l'évolution des interventions

##Détection d'un feu 

Insertion du feu dans la base lors de la reception par l'api. 

##Attribution des effectifs

Le manager récupère l'état des feux dans la base. Les feux sont ordonnés par puissance, les plus importants étant traités en priorité (à moduler plus tard pour optimiser l'extinction des feux)

#Besoins API 

Récupérer tous les véhicules disponibles d'une station
Récupérer tous les feux actifs 
Récupérer tous les véhicules d'un feu 
Récupérer tous les feux d'un capteur
Récupérer tous les capteurs actifs 
