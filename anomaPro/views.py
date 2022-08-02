# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.db import DataError
import pandas
import csv
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy
import os

class FilePath():
    def __init__(self, fichier):
        self.fichier = str(fichier)
    #
    def __str__(self):  
        absPath = os.path.abspath(__file__)
        pthDir1 = os.path.dirname(absPath)
        pthDir2 = os.path.dirname(pthDir1)
        fchPath = os.path.join(pthDir2,self.fichier)
        return(fchPath)

def createDic(max_dict, max_index):
  temp = [max_dict, max_index]
  new_dict = {}
  for k in max_dict.keys():
    new_dict[k] = tuple(new_dict[k] for new_dict in temp)
  
  return new_dict

def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

def getMax_Min(df3):
    #Enfin, retourne la valeur maximale de la ligne >> 80575                        >> 

    #Si il existe des zéros alors il se transform en NAN
    #Un problème est que chaque colonne où il existe un NAN
    #toute les colonne se transforme en float
    df3 = df3.replace(0, np.nan)


    #Récupère la ligne avec la valeur maximale      >> 2021: 80575.0, 2022: 19580.0     >> df3.max()
    #Transforme la valeur en int                    >> 2021: 80575.0, 2022: 19580.0     >> df3.max().astype()
    #Puis la transforme en dictionnaire             >> {2021: 80575, 2022: 19580}   >> df3.max().to_dict()
    max_value = df3.max().astype('int64')
    max_value = max_value.to_dict()

    min_value = df3.min().astype('int64')
    min_value = min_value.to_dict()

    #Trouve l'index avec la valeur la plus grande   >> 18  

    max_index = df3.idxmax()
    min_index = df3.idxmin()
    
    #On fusionne les deux dico qui ont la meme clé   
    max_dict = createDic(max_value, max_index)
    min_dict = createDic(min_value, min_index)

    print('max_dict', max_dict)
    print('min_dict', min_dict)

    min_key = min(min_dict, key=min_dict.get)
    min_val = min(min_dict.values())

    max_key = max(max_dict, key=max_dict.get)
    max_val = max(max_dict.values())


    print("min_key et min_val", min_key, min_val)
    print("max_key et max_val", max_key, max_val)

    return(min_key, min_val, max_key, max_val)


###################################################################################################################################################################
################################ Filtrage de la DATABASE ##########################################################################################################*


#################### IMPORT CSV ####################
#
# lecture du CSV et gestion des caractères spéciaux

# fichier local : 
# df = pandas.read_csv(r"dans-ma-rue.csv", sep=';',header = 0,encoding="utf-8") 

# on retire les colonnes inutiles :
# df2 = df.drop(['ID DECLARATION','SOUS TYPE DECLARATION','ADRESSE','CODE POSTAL', 'VILLE',
  # 'CONSEIL DE QUARTIER','DATE DECLARATION','OUTIL SOURCE','INTERVENANT','ID_DMR','geo_shape'], axis=1)

# # transformer noms de col en minuscules :
# df2.columns = df2.columns.str.lower()
# # remplacer espaces par _ :
# df2.columns = df2.columns.str.replace(" ","_") # remplacer espaces dans les noms de colonnes par _
# df2['type_declaration'] = df2['type_declaration'].replace(['Éclairage / Électricité'],'Éclairage ou Électricité')

#################### LOAD PICKLE ####################
#
# New
# build df2 from pickled file
# 1 : load all data files into variables (dataframes)
with open('data_2021.dat', 'rb') as file:
  df2_1 = pandas.read_pickle(file)
  print(df2_1.shape)
with open('data_2022.dat', 'rb') as file:
  df2_2 = pandas.read_pickle(file)
  print(df2_2.shape)

# 2 : concatenate both df into one df called df2
df2 = pandas.concat([df2_1,df2_2])
print(df2.shape)



#Liste des Types d'Anomalies pour crée les menu déroulants
list_anomalie= ['Objets abandonnés', 'Graffitis, tags, affiches et autocollants',
       'Autos, motos, vélos...', 'Mobiliers urbains', 'Propreté',
       'Éclairage ou Électricité', 'Voirie et espace public',
       'Activités commerciales et professionnelles', 'Eau',
       'Arbres, végétaux et animaux']

list_months = {'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet','Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'}

list_arr = { "1er arrondissement", "2ème arrondissement" ,"3ème arrondissement","4ème arrondissement","5ème arrondissement","6ème arrondissement","7ème arrondissement","8ème arrondissement",
        "9ème arrondissement","10ème arrondissement","11ème arrondissement","12ème arrondissement","13ème arrondissement",
        "14ème arrondissement","15ème arrondissement","16ème arrondissement","17ème arrondissement" ,"18ème arrondissement" ,"19ème arrondissement" ,"20ème arrondissement"}


def home(request):
  #Première page vue par le client
  #il a 3 choix : accéder à l'interface des Question 1 , 2 et 3
  return render(request, 'home.html' )

#Question 1 : Quelles sont les année pour lesquelles il y a + ou - d'anom par arrondissement

def question1(request):
#affichage d'une vue global des data et des graphs pour la 1ere question :
  

  ########################################################################
  #PIE GRAPH - commande pour crée le diag circulaire par année et par arr
  Q1_Niv0_Pie = "./static/img/Q1_Niv0_Pie.png"
  Q1_Niv0_Pie2 = "/static/img/Q1_Niv0_Pie.png"
  
  # croiser par arrondissement et année :
  # résultat : 1 df dont l'index correspond aux arrondissements, avec 1 colonne par année
  df_q1 = pandas.crosstab(df2['arrondissement'],df2['annee_declaration'])

  # préparer données pour graph : 
  years=[]
  years_values=[]
  arrondissements = []
  arrondissements_values = []
  arrondissements_max = [] #liste de booléen : true pour la valeur max, false pour les autres
  explode = []
  explode_factor=0.2

  for column in df_q1.columns:
      # 1. années et valeurs totales par année
      years_values.append(df_q1[column].sum())
      years.append(column)
      
      # 2. arrondissements et valeurs par arrondissement 
      
      for index, row in df_q1.iterrows():
          arrondissements.append(index)
          arrondissements_values.append(row[column])
          arrondissements_max.append(1 if (row[column] == np.max(df_q1[column])) else 0)

  # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
  explode = [explode_factor * i for i in arrondissements_max]

  # Definir les couleurs avec la map tab20 : 
  # couleur principale (indexes pairs) pour les annees
  # couleurs secondaires (indexes impairs ) pour les arrondissements correspondants.

  cmap = plt.get_cmap("tab20c")
  inner_colors = cmap(np.arange(10)*4)
  outer_colors = cmap(np.array([1 + 4 * j for j in range(0,len(years)) for i in range(0,20)]))

  fig1, ax1 = plt.subplots()
  ax1.pie(arrondissements_values
      ,colors = outer_colors
      ,explode= explode
      ,labels = arrondissements
      ,labeldistance = 0.9
      ,radius = 1.5
      ,wedgeprops=dict(width=0.8, edgecolor='w')
      )
  ax1.pie(years_values
      ,textprops={'fontsize': 14}
      ,labeldistance = 0.5
      ,colors = inner_colors
      ,labels = years
      ,radius = 1)

  ax1.axis()

  ax1.set(aspect="equal")
  plt.title(f"anomalies par année et arrondissement.", pad = 50)
  plt.savefig(Q1_Niv0_Pie,bbox_inches="tight")
  plt.close()

  ########################################################################
  #BAR GRAPH - commande pour crée l'histogramme par arr et type anomalies
  pandas.crosstab(df2['arrondissement'],df2['annee_declaration']).plot.bar(title="Anomalies par arrondissement, par année.")
  Q1_Niv0_Bar = './static/img/Q1_Niv0_Bar.png'
  Q1_Niv0_Bar2 ='/static/img/Q1_Niv0_Bar.png'
  plt.savefig(str(Q1_Niv0_Bar),bbox_inches="tight")
  plt.close()

  ########################################################################
  #DATA - commande pour générer la tableau de données (global)
  df3 = pandas.crosstab(df2['arrondissement'],df2['annee_declaration'])
  print("df3", df3)

  json_records = df3.to_json(orient ='index')
  data = []
  data = json.loads(json_records)
  
  min_key, min_val, max_key, max_val = getMax_Min(df3)

  context = {'img': [Q1_Niv0_Bar2, Q1_Niv0_Pie2], 'data': data, 'min_val' : min_val, 'min_key' : min_key, 'max_key' : max_key, 'max_val' : max_val} 
  
  return render(request, 'question1.html', context)


#Quels sont les mois pour lesquels il y a le plus / le moins d’anomalie signalées,par type d’anomalie ?
def question2(request):

  #Affichage d'une vue global des data et des graphs pour la 2e question :

  
  ########################################################################
  ##PIE GRAPH - Nombre d'anomalies par mois et par années
  Q2_Niv0_Pie = "./static/img/Q2_Niv0_Pie.png"
  Q2_Niv0_Pie2 = "/static/img/Q2_Niv0_Pie.png"
  
  # croiser par mois et année :
  # résultat : 1 df dont l'index correspond aux mois, avec 1 colonne par année
  df_q2 = pandas.crosstab(df2['mois_declaration'],df2['annee_declaration'])

  # préparer données pour graph : 
  years=[]
  years_values=[]
  mois = []
  mois_values = []
  mois_max = [] #liste de booléen : true pour la valeur max, false pour les autres
  explode = []
  explode_factor=0.2

  for column in df_q2.columns:
      # 1. années et valeurs totales par année
      years_values.append(df_q2[column].sum())
      years.append(column)
      
      # 2. arrondissements et valeurs par arrondissement 
      
      for index, row in df_q2.iterrows():
          mois.append(index)
          mois_values.append(row[column])
          mois_max.append(1 if (row[column] == np.max(df_q2[column])) else 0)

  # replace months with 0 data with empty str "" and other months with complete months name in labels list
  mois_dict = {1:"janvier",2:"fevrier",3:"mars",4:"avril",5:"mai",6:"juin",7:"juillet",8:"août",9:"septembre",10:"octobre",11:"novembre",12:"décembre"}
  mois = [mois_dict[mois] if (mois_values[i]!=0) else "" for i,mois in enumerate(mois) ]


  # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
  explode = [explode_factor * i for i in mois_max]

  # Definir les couleurs avec la map tab20 : 
  # couleur principale (indexes pairs) pour les annees
  # couleurs secondaires (indexes impairs ) pour les arrondissements correspondants.

  cmap = plt.get_cmap("tab20c")
  inner_colors = cmap(np.arange(10)*4)
  outer_colors = cmap(np.array([1 + 4 * j for j in range(0,len(years)) for i in range(0,12)]))

  fig1, ax1 = plt.subplots()
  ax1.pie(mois_values
      ,colors = outer_colors
      ,explode= explode
      ,labels = mois
      ,rotatelabels = True
      ,labeldistance = 0.7
      ,radius = 1.5
      ,wedgeprops=dict(width=0.8, edgecolor='w')
      )
  ax1.pie(years_values
      ,textprops={'fontsize': 14}
      ,labeldistance = 0.5
      ,colors = inner_colors
      ,labels = years
      ,radius = 1)

  ax1.axis()
  ax1.set(aspect="equal")
  plt.title(f"anomalies par année et par mois.", pad = 50)
  plt.savefig(Q2_Niv0_Pie,bbox_inches="tight")
  plt.close()

  ########################################################################
  #BAR GRAPH - Nombre d'anomalies par mois et par années
  Q2_Niv0_Bar = "./static/img/Q2_Niv0_Bar.png"
  Q2_Niv0_Bar2 = "/static/img/Q2_Niv0_Bar.png"
  pandas.crosstab(df2['mois_declaration'],df2['annee_declaration']).plot.bar()
  plt.savefig(Q2_Niv0_Bar,bbox_inches="tight")
  plt.close()

  ########################################################################
  #DATA - Nombre d'anomalies par mois et par années
  df3 = pandas.crosstab(df2['mois_declaration'],df2['annee_declaration'])
  df3 = df3.rename(index={ 1: 'Janvier', 2 : 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'})
  json_records = df3.to_json(orient ='index')
  data = []
  data = json.loads(json_records)

  min_key, min_val, max_key, max_val = getMax_Min(df3)



  context = {'img': [Q2_Niv0_Pie2, Q2_Niv0_Bar2], 'data': data, 'min_val' : min_val, 'min_key' : min_key, 'max_key' : max_key, 'max_val' : max_val}

  return render(request, 'question2.html', context)


###Quel(s) arrondissement(s) comportent le plus / le moins d’anomalies signalées, par type d’anomalies ?
def question3(request):

  request_get = request.GET
  if request_get:
    #Niveau 2 de détails pour la question 2
    #Affichage du nombre d'anomalie et les graphs par type d'anomalie sélectionné dans le menu déroulant

    #on sélectionne dans le QueryDict 'Objets abandonnés'
    #exemple : <QueryDict: {'anomalie': ['Objets abandonnés']}>
    op = request_get["anomalie"].encode('utf8')

    print("op", str(op.decode()))

    df3 = df2.loc[df2['type_declaration']==str(op.decode())]
    
    ########################################################################
    ## PIE - Nombre d'anomalies pour le type d'anomalie selectionne pour tout les arrondissement
    Q3_Niv1_Pie = "./static/img/Q3_Niv1_Pie.png"
    Q3_Niv1_Pie2 = "/static/img/Q3_Niv1_Pie.png"
  
    # croiser par arrondissement et année :
    # résultat : 1 df dont l'index correspond aux arrondissements, avec 1 colonne par année
    df_q1 = pandas.crosstab(df3['arrondissement'],df3['annee_declaration'])

    # préparer données pour graph : 
    years=[]
    years_values=[]
    arrondissements = []
    arrondissements_values = []
    arrondissements_max = [] #liste de booléen : true pour la valeur max, false pour les autres
    explode = []
    explode_factor=0.2

    for column in df_q1.columns:
        # 1. années et valeurs totales par année
        years_values.append(df_q1[column].sum())
        years.append(column)
        
        # 2. arrondissements et valeurs par arrondissement 
        
        for index, row in df_q1.iterrows():
            arrondissements.append(index)
            arrondissements_values.append(row[column])
            arrondissements_max.append(1 if (row[column] == np.max(df_q1[column])) else 0)

    # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
    explode = [explode_factor * i for i in arrondissements_max]

    # Definir les couleurs avec la map tab20 : 
    # couleur principale (indexes pairs) pour les annees
    # couleurs secondaires (indexes impairs ) pour les arrondissements correspondants.

    cmap = plt.get_cmap("tab20c")
    inner_colors = cmap(np.arange(10)*4)
    outer_colors = cmap(np.array([1 + 4 * j for j in range(0,len(years)) for i in range(0,20)]))

    fig1, ax1 = plt.subplots()
    ax1.pie(arrondissements_values
        ,colors = outer_colors
        ,explode= explode
        ,labels = arrondissements
        ,labeldistance = 0.9
        ,radius = 1.5
        ,wedgeprops=dict(width=0.8, edgecolor='w')
        )
    ax1.pie(years_values
        ,textprops={'fontsize': 14}
        ,labeldistance = 0.5
        ,colors = inner_colors
        ,labels = years
        ,radius = 1)

    ax1.axis()
    plt.title(f"{request_get['anomalie']} par année et arrondissement.", pad = 50)
    # ax1.set(aspect="equal")
    plt.savefig(Q3_Niv1_Pie, bbox_inches="tight")
    plt.close()

    ########################################################################
    ## HIST - Nombre d'anomalies par type d'anomalie pour tout les arrondissement
    pandas.crosstab(df3['arrondissement'],df3['type_declaration']).plot.bar()
    Q3_Niv1_Bar = "./static/img/Q3_Niv1_Bar.png"
    Q3_Niv1_Bar2 = "/static/img/Q3_Niv1_Bar.png"
    plt.savefig(Q3_Niv1_Bar,bbox_inches="tight")
    plt.close()

    ########################################################################
    ### DATA - Nombre d'anomalies par type d'anomalie pour tout les arrondissement
    df4 = pandas.crosstab(df3['arrondissement'],df3['annee_declaration'])
    df3 = df3.replace(0, np.nan)


    #Récupère la ligne avec la valeur maximale      >> 2021: 80575.0, 2022: 19580.0     >> df3.max()
    #Transforme la valeur en int                    >> 2021: 80575.0, 2022: 19580.0     >> df3.max().astype()
    #Puis la transforme en dictionnaire             >> {2021: 80575, 2022: 19580}   >> df3.max().to_dict()
    max_value = df4.max().astype('int64')
    max_value = max_value.to_dict()

    min_value = df4.min().astype('int64')
    min_value = min_value.to_dict()

    #Trouve l'index avec la valeur la plus grande   >> 18  

    max_index = df4.idxmax()
    min_index = df4.idxmin()
    
    #On fusionne les deux dico qui ont la meme clé   
    max_dict = createDic(max_value, max_index)
    min_dict = createDic(min_value, min_index)
    print('max_dict', max_dict)
    print('min_dict', min_dict)


    json_records = df4.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    anomalie = str(op.decode())
    context = {'img' : [Q3_Niv1_Bar2, Q3_Niv1_Pie2], 'data' : data, 'list_anomalie' : list_anomalie, 'id' : 0, 'anomalie' : anomalie, 'max_dict' : max_dict, 'min_dict' : min_dict}

    return render(request, 'question3.html', context)


  ##Niveau 0 de détails pour la question 3
  else:

    ########################################################################
    ## PIE GRAPH - Nombre d'anomalies pour tout les arr et pour tout les types
    Q3_Niv0_Pie = "./static/img/Q3_Niv0_Pie.png"
    Q3_Niv0_Pie2 = "/static/img/Q3_Niv0_Pie.png"
    
    df_q3 = pandas.crosstab(df2['type_declaration'],df2['annee_declaration'])

    # manage data to plot and explode parameter :
    years = []
    years_values = []
    type_declaration = []
    type_decalaration_values = []
    type_declaration_max = []
    explode_factor=0.1

    for column in df_q3.columns:
        years_values.append(df_q3[column].sum())
        years.append(column)
        for index, row in df_q3.iterrows():
            type_declaration.append(index)
            type_decalaration_values.append(row[column])
            type_declaration_max.append(1 if (row[column] == np.max(df_q3[column])) else 0)

    # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
    explode = [explode_factor * i for i in type_declaration_max]

    # Definir les couleurs 
    # couleurs annee_declaration :
    cmap = plt.get_cmap("tab20c")
    inner_colors = cmap(np.arange(10)*4)

    # couleurs type_declaration : 
    categories = df_q3.index
    n = len(categories)
    cmap = plt.get_cmap('twilight')
    # cmap = plt.get_cmap('winter')
    outer_colors = [cmap(i/n) for i in range(0,n)]

    # graph :
    fig1, ax1 = plt.subplots()
    pie  = ax1.pie(type_decalaration_values
        ,colors = outer_colors
        # raccourcir les etiquettes aux premiers caractères uniquement, afficher seulement pour les max
        ,labels = [(f"{label[:7]}..." if type_declaration_max[i] else "") for i , label in enumerate(type_declaration)]
        ,rotatelabels =True
        ,explode= explode
        ,labeldistance = 0.6
        ,radius = 1.5
        ,wedgeprops=dict(width=0.8, edgecolor='w')
        )
    ax1.pie(years_values
        ,textprops={'fontsize': 14}
        ,labeldistance = 0.5
        ,colors = inner_colors
        ,labels = years
        ,wedgeprops=dict(width=1, edgecolor='w')
        ,radius = 1)

    ax1.legend(pie[0],categories, bbox_to_anchor=(1.45,0.5), loc="center right", fontsize=10, 
              bbox_transform=plt.gcf().transFigure)

    plt.title(f"anomalies par année et arrondissement.", pad = 50)
    plt.savefig(Q3_Niv0_Pie, bbox_inches="tight")
    plt.close()
  

    ####################################################################################
    #BAR GRAPH - Nombre d'anomalies pour tout les arr et pour tout les types
    Q3_Niv0_Bar = "./static/img/Q3_Niv0_Bar.png"
    Q3_Niv0_Bar2 = "/static/img/Q3_Niv0_Bar.png"
    pandas.crosstab(df2['arrondissement'],df2['annee_declaration']).plot.bar()
    plt.savefig(Q3_Niv0_Bar,bbox_inches="tight")
    plt.close()


    ####################################################################################
    #DATA - Nombre d'anomalies pour tout les arr et pour tout les types
    df3 = pandas.crosstab(df2['arrondissement'],df2['type_declaration'])
    json_records = df3.to_json(orient ='index')
    data = []
    data = json.loads(json_records)

    df3 = df3.replace(0, np.nan)


    #Récupère la ligne avec la valeur maximale      >> 2021: 80575.0, 2022: 19580.0     >> df3.max()
    #Transforme la valeur en int                    >> 2021: 80575.0, 2022: 19580.0     >> df3.max().astype()
    #Puis la transforme en dictionnaire             >> {2021: 80575, 2022: 19580}   >> df3.max().to_dict()
    max_value = df3.max().astype('int64')
    max_value = max_value.to_dict()

    min_value = df3.min().astype('int64')
    min_value = min_value.to_dict()

    #Trouve l'index avec la valeur la plus grande   >> 18  

    max_index = df3.idxmax()
    min_index = df3.idxmin()
    
    #On fusionne les deux dico qui ont la meme clé   
    max_dict = createDic(max_value, max_index)
    min_dict = createDic(min_value, min_index)

    
    context = {'img' : [Q3_Niv0_Bar2, Q3_Niv0_Pie2], 'data': data, 'list_anomalie' : list_anomalie, 'id' : 1, 'max_dict' : max_dict, 'min_dict' : min_dict}

  return render(request, 'question3.html', context)


def Q1_ParAnnée(request, pk):

  #Get le type d'anomalie choisi afin d'afficher correctement le nveau de détail
  request_get = request.GET

  #Niveau 2 de détails pour la question 1
  #Affiche le nombre d'anomalie et les graphs par le type d'anomalie sélectionné dans le menu déroulant
  
  #Si le client selectionne un type dans le menu déroulant :
  if request_get:

    #on sélectionne dans le QueryDict 'Objets abandonnés'
    #<QueryDict: {'anomalie': ['Objets abandonnés']}>
    op = request_get["anomalie"].encode('utf8')


    ####################################################################################
    #PIE GRAPH - Nb d'Anomalies sur l'arrondissement et par type selectionné par le client 
    df2.loc[df2['arrondissement']==pk,:].loc[df2['type_declaration']==str(op.decode()),:].groupby(['annee_declaration'])['type_declaration'].value_counts().plot.pie()
    Q1_Niv2_Pie = './static/img/Q1_Niv2_{}_{}_Pie.png'.format(str(op.decode()),pk)
    Q1_Niv2_Pie2 ='/static/img/Q1_Niv2_{}_{}_Pie.png'.format(str(op.decode()),pk)
    plt.title(f"{request_get['anomalie']} dans l'arrondissement n°{pk}", pad = 50)
    plt.savefig(str(Q1_Niv2_Pie),bbox_inches="tight")
    plt.close()

    ####################################################################################    
    #BAR GRAPH - Nb d'Anomalies sur l'arrondissement et par type selectionné par le client 
    df2.loc[df2['arrondissement']==pk,:].loc[df2['type_declaration']==str(op.decode()),:].groupby(['annee_declaration'])['type_declaration'].value_counts().plot.bar()
    Q1_Niv2_Bar = './static/img/Q1_Niv2_{}_{}_Bar.png'.format(str(op.decode()),pk)
    Q1_Niv2_Bar2 ='/static/img/Q1_Niv2_{}_{}_Bar.png'.format(str(op.decode()),pk)
    plt.savefig(str(Q1_Niv2_Bar),bbox_inches="tight")
    plt.close()

    ####################################################################################
    #DATAFRAME - Nb d'Anomalies sur l'arrondissement et par type selectionné par le client 
    df4 = df2.loc[df2['arrondissement']==pk,:].loc[df2['type_declaration']==str(op.decode()),:].groupby(['annee_declaration'])['type_declaration'].count().reset_index(name="count")

    json_records2 = df4.to_json(orient = 'records')
    data_type = []
    data_type = json.loads(json_records2)
  
    ####################################################################################
    # Data for mapping
    # data_to_map = df
    data_to_map = df2.loc[df2['arrondissement']==pk,:].loc[df2['type_declaration']==str(op.decode()),:]['geo_point_2d']
    data_to_map = data_to_map.to_json()
    data_to_map = json.loads(data_to_map)


    #####
    df5 = df2.loc[df2['arrondissement']==pk,:].loc[df2['type_declaration']==str(op.decode()),:].groupby(['annee_declaration'])['type_declaration'].count()
    anomalie = str(op.decode())


    min_dict = df5.to_dict()
    max_dict = df5.to_dict()

    min_key = min(min_dict, key=min_dict.get)
    max_key = max(max_dict, key=max_dict.get)

    min_value = min_dict[min_key]
    max_value = max_dict[max_key]
    print('max_key in ', max_key)
    print('min_key in ', min_key)
    print("min dict", min_dict)
    #Dict à retourner si le client à selectionné le détails de niveau 2
    context = {'img_type' : [Q1_Niv2_Bar2, Q1_Niv2_Pie2], 'data_type': data_type , 'pk':pk, 'id':0, 'anomalie' : anomalie, 'data_to_map':data_to_map} 



  else:

    #Niveau 1 de détails pour la question 1
    #Affiche le nombre d'anomalie par arr et par type d'ano sélectionné dans le menu déroulant

    def absolute_value(val):
      a  = numpy.round(val/100.*df2.loc[df2['arrondissement']==pk,:].groupby(['annee_declaration'])['annee_declaration'].count().sum(), 0)

    ####################################################################################
    #PIE CHART - Nb d'Anomalies par type dans l'arrondissement selectionné par le client  
    Q1_Niv1_Pie = "./static/img/Q1_Niv1_{}_Pie.png".format(pk)
    Q1_Niv1_Pie2 = "/static/img/Q1_Niv1_{}_Pie.png".format(pk)
    
    df_q1_1 = df2.loc[df2['arrondissement']==pk,:]
    df_q1_1 = pandas.crosstab(df_q1_1['type_declaration'],df_q1_1['annee_declaration'])

    # manage data to plot and explode parameter :
    years = []
    years_values = []
    type_declaration = []
    type_decalaration_values = []
    type_declaration_max = []
    explode_factor=0.1

    for column in df_q1_1.columns:
        years_values.append(df_q1_1[column].sum())
        years.append(column)
        for index, row in df_q1_1.iterrows():
            type_declaration.append(index)
            type_decalaration_values.append(row[column])
            type_declaration_max.append(1 if (row[column] == np.max(df_q1_1[column])) else 0)

    # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
    explode = [explode_factor * i for i in type_declaration_max]

    # Definir les couleurs 
    # couleurs annee_declaration :
    cmap = plt.get_cmap("tab20c")
    inner_colors = cmap(np.arange(10)*4)

    # couleurs type_declaration : 
    categories = df_q1_1.index
    n = len(categories)
    cmap = plt.get_cmap('twilight')
    # cmap = plt.get_cmap('winter')
    outer_colors = [cmap(i/n) for i in range(0,n)]

    # graph :
    fig1, ax1 = plt.subplots()
    pie  = ax1.pie(type_decalaration_values
        ,colors = outer_colors
        # raccourcir les etiquettes aux premiers caractères uniquement, afficher seulement pour les max
        ,labels = [(f"{label[:15]}..." if type_declaration_max[i] else "") for i , label in enumerate(type_declaration)]
        ,rotatelabels =True
        ,explode= explode
        ,labeldistance = 0.6
        ,radius = 1.5
        ,wedgeprops=dict(width=0.8, edgecolor='w')
        )
    ax1.pie(years_values
        ,textprops={'fontsize': 14}
        ,labeldistance = 0.5
        ,colors = inner_colors
        ,labels = years
        ,wedgeprops=dict(width=1, edgecolor='w')
        ,radius = 1)

    ax1.legend(pie[0],categories, bbox_to_anchor=(1.45,0.5), loc="center right", fontsize=10, 
              bbox_transform=plt.gcf().transFigure)
    plt.title(f"Anomalies dans l'arrondissement n°{pk}", pad = 50)
    
    ax1.axis()  
    plt.savefig(str(Q1_Niv1_Pie),bbox_inches='tight')
    plt.close()


    ####################################################################################
    # BAR CHART -  Nb d'Anomalies par type dans l'arrondissement selectionné par le client
    # Definir les couleurs : idem pie chart.
    #

    ax = df2.loc[df2['arrondissement']==pk,:].groupby(['annee_declaration'])['type_declaration'].value_counts().unstack().plot.bar(
        stacked=True
        ,color = outer_colors)

    ax.legend(pie[0],categories, bbox_to_anchor=(1.45,0.5), loc="center right", fontsize=10, 
           bbox_transform=plt.gcf().transFigure)    

    Q1_Niv1_Bar = './static/img/Q1_Niv1_{}_Bar.png'.format(pk)
    Q1_Niv1_Bar2 ='/static/img/Q1_Niv1_{}_Bar.png'.format(pk)
    plt.savefig(str(Q1_Niv1_Bar),bbox_inches='tight')
    plt.close()
    
    ####################################################################################
    ##DATAFRAME - Nb d'Anomalies par type dans l'arrondissement selectionné par le client  
    df3 = df2.loc[df2['arrondissement']==pk,:].groupby(['annee_declaration'])['type_declaration'].count().reset_index(name="count")
    json_records = df3.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)

    df4 = df2.loc[df2['arrondissement']==pk,:].groupby(['annee_declaration'])['type_declaration'].count()

    min_dict = df4.to_dict()
    max_dict = df4.to_dict()

    min_key = min(min_dict, key=min_dict.get)
    max_key = max(max_dict, key=max_dict.get)

    min_value = min_dict[min_key]
    max_value = max_dict[max_key]
    print('max_key in ', max_key)
    print('min_key in ', min_key)
    
    #Dict à renvoyer 
    context = {'img' : [Q1_Niv1_Bar2, Q1_Niv1_Pie2], 'data': data,'pk':pk, 'id': 1} 
 

  print('max_key out', max_key)
  print('min_key out ', min_key)
  return render(request, 'Q1_ParAnnée.html', {'min_key' : min_key, 'max_key' : max_key, 'min_value' : min_value, 'max_value' : max_value , 'context' : context, 'list_anomalie' : list_anomalie})


def Q2_ParMois(request, pk):

  #Get le type d'anomalie choisi afin d'afficher correctement le nveau de détail
  request_get = request.GET


  #Niveau 2 de détails pour la question 2
  #Affiche le nombre d'anomalie et les graphs par mois et pour le type d'anomalie sélectionné dans le menu déroulant
  
  #Définition de l'arrondissement et quelle type d'anomalie recherché 
  
  #Si le client selectionne un type dans le menu déroulant :
  if request_get:
    op = request_get["anomalie"].encode('utf8')
    df3 = df2.loc[df2['arrondissement']==pk,:].loc[df2['type_declaration']==str(op.decode())]

    ########################################################################
    ## PIE - Nombre d'anoamlie pour un arrondissement et un type d'ano selectionnée
    Q2_Niv2_Pie = './static/img/Q2_Niv2_{}_{}_Pie.png'.format(str(op.decode()), pk)
    Q2_Niv2_Pie2 = '/static/img/Q2_Niv2_{}_{}_Pie.png'.format(str(op.decode()), pk)

    # croiser par mois et année :
    # résultat : 1 df dont l'index correspond aux mois, avec 1 colonne par année
    df_q2 = pandas.crosstab(df3['mois_declaration'],df3['annee_declaration'])

    # préparer données pour graph : 
    years=[]
    years_values=[]
    mois = []
    mois_values = []
    mois_max = [] #liste de booléen : true pour la valeur max, false pour les autres
    explode = []
    explode_factor=0.2

    for column in df_q2.columns:
        # 1. années et valeurs totales par année
        years_values.append(df_q2[column].sum())
        years.append(column)
        
        # 2. arrondissements et valeurs par arrondissement 
        
        for index, row in df_q2.iterrows():
            mois.append(index)
            mois_values.append(row[column])
            mois_max.append(1 if (row[column] == np.max(df_q2[column])) else 0)

    # replace months with 0 data with empty str "" and other months with complete months name in labels list
    mois_dict = {1:"janvier",2:"fevrier",3:"mars",4:"avril",5:"mai",6:"juin",7:"juillet",8:"août",9:"septembre",10:"octobre",11:"novembre",12:"décembre"}
    mois = [mois_dict[mois] if (mois_values[i]!=0) else "" for i,mois in enumerate(mois) ]


    # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
    explode = [explode_factor * i for i in mois_max]

    # Definir les couleurs avec la map tab20 : 
    # couleur principale (indexes pairs) pour les annees
    # couleurs secondaires (indexes impairs ) pour les arrondissements correspondants.

    cmap = plt.get_cmap("tab20c")
    inner_colors = cmap(np.arange(10)*4)
    outer_colors = cmap(np.array([1 + 4 * j for j in range(0,len(years)) for i in range(0,12)]))

    fig1, ax1 = plt.subplots()
    ax1.pie(mois_values
        ,colors = outer_colors
        ,explode= explode
        ,labels = mois
        ,rotatelabels = True
        ,labeldistance = 0.7
        ,radius = 1.5
        ,wedgeprops=dict(width=0.8, edgecolor='w')
        )
    ax1.pie(years_values
        ,textprops={'fontsize': 14}
        ,labeldistance = 0.5
        ,colors = inner_colors
        ,labels = years
        ,radius = 1)

    ax1.axis()
    plt.title(f"{request_get['anomalie']} dans l'arrondissement n°{pk}")
    ax1.set(aspect="equal")


    plt.savefig(str(Q2_Niv2_Pie),bbox_inches='tight')
    plt.close()

    ########################################################################
    ## HIST - Nombre d'anoamlie pour un arrondissement et un type d'ano selectionnée
    Q2_Niv2_Bar = './static/img/Q2_Niv2_{}_{}_Bar.png'.format(str(op.decode()),pk)
    Q2_Niv2_Bar2 ='/static/img/Q2_Niv2_{}_{}_Bar.png'.format(str(op.decode()), pk)

    df4 = pandas.crosstab(df3['mois_declaration'],df3['annee_declaration']).plot.bar()
    plt.savefig(str(Q2_Niv2_Bar),bbox_inches='tight')
    plt.close()

    ########################################################################
    ## DATA - Nombre d'anoamlie pour un arrondissement et un type d'ano selectionnée
    df4 = pandas.crosstab(df3['mois_declaration'],df3['annee_declaration'])
    df4 = df4.rename(index={ 1: 'Janvier', 2 : 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'})

    json_records2 = df4.to_json(orient = 'index')
    data_type = []
    data_type = json.loads(json_records2)
    anomalie = str(op.decode())
    min_key, min_val, max_key, max_val = getMax_Min(df4)
    print('list_arr', list_arr)
    context = {'list_arr' : list_arr, 'min_key' : min_key, 'max_key' : max_key, 'min_val' : min_val, 'max_val' : max_val , 'pk' : pk, 'anomalie' : anomalie, 'img' : [Q2_Niv2_Bar2, Q2_Niv2_Pie2], 'data_type' : data_type, 'id' : 0, 'list_anomalie' : list_anomalie}

  else :

    df3 = df2.loc[df2['arrondissement']==pk,:]
    ########################################################################
    # PIE  : Nombre total d'anomalie par mois dans un arrondissement
    Q2_Niv1_Pie = './static/img/Q2_Niv1_{}_Pie.png'.format(pk)
    Q2_Niv1_Pie2 ='/static/img/Q2_Niv1_{}_Pie.png'.format(pk)
    
    # croiser par mois et année :
    # résultat : 1 df dont l'index correspond aux mois, avec 1 colonne par année
    df_q2 = df2.loc[df2['arrondissement']==pk,:]
    df_q2 = pandas.crosstab(df_q2['mois_declaration'],df_q2['annee_declaration'])

    # préparer données pour graph : 
    years=[]
    years_values=[]
    mois = []
    mois_values = []
    mois_max = [] #liste de booléen : true pour la valeur max, false pour les autres
    explode = []
    explode_factor=0.2

    for column in df_q2.columns:
        # 1. années et valeurs totales par année
        years_values.append(df_q2[column].sum())
        years.append(column)
        
        # 2. arrondissements et valeurs par arrondissement 
        
        for index, row in df_q2.iterrows():
            mois.append(index)
            mois_values.append(row[column])
            mois_max.append(1 if (row[column] == np.max(df_q2[column])) else 0)

    # replace months with 0 data with empty str "" and other months with complete months name in labels list
    mois_dict = {1:"janvier",2:"fevrier",3:"mars",4:"avril",5:"mai",6:"juin",7:"juillet",8:"août",9:"septembre",10:"octobre",11:"novembre",12:"décembre"}
    mois = [mois_dict[mois] if (mois_values[i]!=0) else "" for i,mois in enumerate(mois) ]


    # paramètre explode du graph pie pour gérer identification de l'arrondissement max:
    explode = [explode_factor * i for i in mois_max]

    # Definir les couleurs avec la map tab20 : 
    # couleur principale (indexes pairs) pour les annees
    # couleurs secondaires (indexes impairs ) pour les arrondissements correspondants.

    cmap = plt.get_cmap("tab20c")
    inner_colors = cmap(np.arange(10)*4)
    outer_colors = cmap(np.array([1 + 4 * j for j in range(0,len(years)) for i in range(0,12)]))

    fig1, ax1 = plt.subplots()
    ax1.pie(mois_values
        ,colors = outer_colors
        ,explode= explode
        ,labels = mois
        ,rotatelabels = True
        ,labeldistance = 0.7
        ,radius = 1.5
        ,wedgeprops=dict(width=0.8, edgecolor='w')
        )
    ax1.pie(years_values
        ,textprops={'fontsize': 14}
        ,labeldistance = 0.5
        ,colors = inner_colors
        ,labels = years
        ,radius = 1)

    ax1.axis()

    plt.title(f"Anomalies dans l'arrondissement n°{pk}")
    plt.savefig(str(Q2_Niv1_Pie),bbox_inches='tight')
    plt.close()

    ########################################################################
    # HIST : Nombre total d'anomalie par mois dans un arrondissement
    Q2_Niv1_Bar = './static/img/Q2_Niv1_{}_Hist.png'.format(pk)
    Q2_Niv1_Bar2 ='/static/img/Q2_Niv1_{}_Hist.png'.format(pk)
    
    pandas.crosstab(df2['mois_declaration'],df2['annee_declaration']).plot.bar()
    plt.savefig(str(Q2_Niv1_Bar),bbox_inches='tight')
    plt.close()


    ########################################################################
    #DATA : Nombre total d'anomalie par mois dans un arrondissement
    df4 = pandas.crosstab(df3['mois_declaration'],df3['annee_declaration'])
    df4 = df4.rename(index={ 1: 'Janvier', 2 : 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'})
    json_records = df4.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)

    min_key, min_val, max_key, max_val = getMax_Min(df4)

    context = {'min_key' : min_key, 'max_key' : max_key, 'min_val' : min_val, 'max_val' : max_val , 'img' : [Q2_Niv1_Bar2, Q2_Niv1_Pie2], 'data' : data, 'pk' : pk, 'id' : 1, 'list_anomalie' : list_anomalie}
  
  return render(request, 'Q2_ParMois.html', context) 