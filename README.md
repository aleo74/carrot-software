# carrot software

![imagen](https://i.imgur.com/aHT5bWw.jpeg)

### Only French for now

## Version
Encore en dévelopement.
A venir :
* Localisation sur la carte en fonction des points GPS recu.
* Sauvegarde dans un fichier CSV des données recu.
* Intéraction avec la [ground station](https://github.com/aleo74/carrot-groundstation), et avec l'[odb](https://github.com/aleo74/carrot_firmware).
* Afficher certains graphiques en fonction des modules installés sur l'odb.
* Utilisation des deux groupBox restante.

## Tech
*charset-normalizer==2.1.0
* folium==0.12.1.post1
* Jinja2==3.1.2
* numpy==1.23.1
* PyQt5==5.15.7
* PyQt5-Qt5==5.15.2
* PyQt5-sip==12.11.0
* PyQtChart==5.15.6
* PyQtChart-Qt5==5.15.2
* pyqtgraph==0.12.4
* PyQtWebEngine==5.15.6
* PyQtWebEngine-Qt5==5.15.2
* pyserial==3.5
* requests==2.28.1
* urllib3==1.26.11

## Installation Linux
```
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
$ python3 main.py
```

## Installation Windows
```
> virtualenv env
> \env\Scripts\activate.bat
> pip install -r requirements.txt
> python main.py
```

## Utilisation
### Pour tester l'odb :
* Installez le module [SerialWriter](https://github.com/aleo74/carrot_firmware/blob/main/modules/SerialWriter/README.md) dans l'odb.
* Lancez le logiciel.
* Selectionnez le port COM, et le baudRate du micro controller de l'odb dans le logiciel.
* Cliquez sur 'Connect'.

### Ground Station
* Branchez votre ground station en USB.
* Selectionnez le port COM, et le baudRate de la ground station dans le logiciel.
* Cliquez sur 'Connect'.

## Fonctionnement

Le logiciel se base sur un json recu via le port COM sélectionné, dont voici la struture :

```
{
    'Nom du module':
    {
       'Nom de la donnée' : valeur,
       [...]
    }
    [...]
}
```
