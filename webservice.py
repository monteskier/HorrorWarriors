__author__ = 'joaquin'

import cherrypy
import json
import pymongo
from bson.objectid import ObjectId
import datetime
import hashlib
from hashlib import md5

class HorrorWarriors:

    exposed = True
    def __init__(self):

        self.client = pymongo.MongoClient()
        self.db = self.client.hw
        self.jugadors = self.db.jugadors
        self.personatges = self.db.personatges
        self.bestiari = self.db.bestiari
        self.heroes = self.db.heroes
        self.partida = self.db.partida
        self.combat = self.db.combat
        self.terreny = self.db.terreny
        self.item = self.db.item
        self.armes = self.db.armes
        self.armadures = self.db.armadures
        self.resposta = {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def login(self,*args,**kwargs):

        try:

            dades_in = cherrypy.request.json

            nick = str(dades_in["nick"])
            password = str(dades_in["password"])
            try:
                master = bool(dades_in["master"])
            except:
                master = False
            m = hashlib.md5()
            m.update(password.encode('utf-8'))
            password = m.hexdigest()

            print """Despres de agafar les dades"""

            try:
                nick_db = (self.jugadors.find_one({"nick":nick}))
                nick_db = str(nick_db["nick"])
                password_db = (self.jugadors.find_one({"password":password}))
                password_db = str(password_db["password"])
                print """Apunt de comprpbar el jugador"""

                if(nick_db == nick and password_db == password):
                    uid = self.jugadors.find_one({"nick":nick})
                    nick = self.jugadors.find_one({"nick":nick},{"nick":1})
                    self.resposta["status"]="Ok"
                    self.resposta["msg"]="S'ha trobat el jugador"
                    self.resposta["uid"] = str(uid["_id"])
                    self.resposta["nick"] = str(nick["nick"])
                    return json.dumps( self.resposta )

            except:
                print("""No s'ha trobat el jugadpr""")
                if (master==True):
                    uid = self.jugadors.save( {"password":password,"nick":nick,"estat":"en espera", "exp":0 ,"master":master})
                else:
                    uid = self.jugadors.save( {"password":password,"nick":nick,"estat":"en espera", "exp":0})
                jugador = self.jugadors.find_one( {"_id":uid} )
                # transformem el _id en string per que sigui JSON-serializable (si no, dona error)
                jugador["_id"] = str(uid)
                # retornem dades d'usuari
                self.resposta["status"]="Ok"
                self.resposta["msg"]="S'ha creat el jugador exitosament"
                self.resposta["uid"] = str(jugador["_id"])
                return json.dumps(self.resposta)
        except:

            self.resposta["status"]="Error"
            self.resposta["msg"]="Les dades no son correctes"
            return json.dumps(self.resposta)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def esMaster(self,*args,**kwargs):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id = str(dades_in["id"])
            master = self.jugadors.find_one({"_id":ObjectId(id)})
            if(master["master"]==True):
                self.resposta["master"] = True
                return json.dumps(self.resposta)

        except:
            self.resposta["master"] = False
            return json.dumps(self.resposta)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def createMap(self,*args,**kwargs):
        self.resposta = {}
        try:

            dades_in = cherrypy.request.json

            id = str(dades_in["id"])
            mapName = str(dades_in["mapName"])
            col = int(dades_in["col"])
            fil = int(dades_in["fil"])
            background = str(dades_in["background"])

            uid = self.terreny.save({"id_master": id, "mapName": mapName, "col": col, "fil": fil, "background": background})
            self.resposta["status"] = "Ok"
            self.resposta["msg"] = "Ha guadat el mapa amb exit"
            return json.dumps(self.resposta)
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = "El mapa no ha guardat correctament"
            return json.dumps(self.resposta)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def createBeast(self, *args, **keywargs):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_master = str(dades_in["id_master"])
            nom = str (dades_in["nom"])
            avatar = str(dades_in["avatar"])
            live = str(dades_in["live"])
            force = str(dades_in["force"])
            agility = str(dades_in["agility"])
            defense = str(dades_in["defense"])

            uid = self.bestiari.save({"id_master":id_master,"nom":nom,"avatar":avatar,"live":live,"force":force,"agility":agility,"defense":defense})
            self.resposta["status"] = """OK"""
            self.resposta["msg"] = """Les dades s'han guardat correctament"""
            return(json.dumps(self.resposta))

        except:
            self.resposta["status"] = ["Error"]
            self.resposta["msg"] = ["""No s'han passat les dades correctament"""]
            return json.dumps(self.resposta)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def loadBeast(self,*args, **keywargs):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_master = str(dades_in["id_master"])
            besties = self.bestiari.find({"id_master":id_master},{"nom":1, "_id":False})
            besties_array = []

            for best in besties:
                best["nom"] = str(best["nom"])
                besties_array.append(best)

            self.resposta["status"] = "Ok"
            self.resposta["msg"] = """S'han carregat les dades"""
            self.resposta["data"] = besties_array
            return(json.dumps(self.resposta))
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """No tens encara cap mostre disponible!"""
            return(json.dumps(self.resposta))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def listBeast(self):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_master = str(dades_in["id_master"])
            besties = self.bestiari.find({"id_master":id_master},{"_id":False})
            besties_array = []

            for best in besties:
                best["nom"] = str(best["nom"])
                besties_array.append(best)

            self.resposta["status"] = "Ok"
            self.resposta["msg"] = """S'han carregat les dades"""
            self.resposta["data"] = besties_array
            return(json.dumps(self.resposta))
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """No tens encara cap mostre disponible!"""
            return(json.dumps(self.resposta))
    
    """ Opcions del Jugador normal"""
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def createHeroe(self, *args, **keywargs):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_jugador = str(dades_in["id_jugador"])
            nom = str (dades_in["nom"])
            avatar = str(dades_in["avatar"])
            live = str(dades_in["live"])
            force = str(dades_in["force"])
            agility = str(dades_in["agility"])
            defense = str(dades_in["defense"])

            uid = self.heroes.save({"id_jugador":id_jugador,"nom":nom,"avatar":avatar,"live":live,"force":force,"agility":agility,"defense":defense})
            self.resposta["status"] = """OK"""
            self.resposta["msg"] = """Les dades s'han guardat correctament"""
            return(json.dumps(self.resposta))

        except:
            self.resposta["status"] = ["Error"]
            self.resposta["msg"] = ["""No s'han passat les dades correctament"""]
            return json.dumps(self.resposta)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def loadHeroes(self,*args, **keywargs):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_jugador = str(dades_in["id_jugador"])
            heroes = self.heroes.find({"id_jugador":id_jugador},{"nom":1, "_id":False})
            heroes_array = []

            for hero in heroes:
                hero["nom"] = str(hero["nom"])
                heroes_array.append(hero)

            self.resposta["status"] = "Ok"
            self.resposta["msg"] = """S'han carregat les dades"""
            self.resposta["data"] = heroes_array
            return(json.dumps(self.resposta))
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """No tens encara cap Heroi disponible!"""
            return(json.dumps(self.resposta))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def listHeroes(self):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_jugador = str(dades_in["id_jugador"])
            heroes = self.heroes.find({"id_jugador":id_jugador},{"_id":False})
            heroes_array = []

            for hero in heroes:
                hero["nom"] = str(hero["nom"])
                heroes_array.append(hero)

            self.resposta["status"] = "Ok"
            self.resposta["msg"] = """S'han carregat les dades"""
            self.resposta["data"] = heroes_array
            return(json.dumps(self.resposta))
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """No tens encara cap Heroi disponible!"""
            return(json.dumps(self.resposta))
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def createParty(self):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            
            id_jugador = str(dades_in["master_id"])
            nom = str(dades_in["nom"])
            pas = str(dades_in["pass"])
            maxper = int(dades_in["maxper"])
            idioma = str(dades_in["idioma"])
            print(id,nom,pas,maxper,idioma)
            
            master = self.jugadors.find_one({"_id":ObjectId(id_jugador)})
            self.partida.save({"id_master":id_jugador,"nom":nom, "pass":pas, "maxper":maxper, "idioma":idioma, "online":False})
            self.resposta["status"] = "OK"
            self.resposta["msg"] = """S'han guardat les dades d el apartida correctament"""
            return(json.dumps(self.resposta))
                
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """Aquest usuari no pot crear partida"""
            return(json.dumps(self.resposta))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def loadPartys(self,*args, **keywargs):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            id_jugador = str(dades_in["id_jugador"])
            partys = self.partida.find({"id_master":id_jugador},{"_id":False})
            partys_array = []

            for party in partys:
                party["nom"] = str(party["nom"])
                party["maxper"] = int(party["maxper"])
                party["online"] = str(party["online"])
                partys_array.append(party)

            self.resposta["status"] = "Ok"
            self.resposta["msg"] = """S'han carregat les dades"""
            self.resposta["data"] = partys_array
            return(json.dumps(self.resposta))
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """No tens encara cap Partida disponible!"""
            return(json.dumps(self.resposta))
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def onlineParty(self):
        self.resposta = {}
        try:
            dades_in = cherrypy.request.json
            nom = str(dades_in["nom"])
            estat = str(dades_in["estat"])
            self.partida.find_one({"nom":nom})
            estat2 = None
            if(estat=="True"):
                estat2 = False
            if(estat == "False" ):
                estat2 = True
            self.partida.update({"nom":nom},{'$set':{"online":estat2}})
            self.resposta["status"] = "OK"
            self.resposta["msg"] = """El estat de la partida ara es %s""",(estat2)
            self.resposta["estat"] = estat2
            return json.dumps(self.resposta)
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = """El estat de la partida sense modificar"""
            self.resposta["estat"] = estat2
            return(json.dumps(self.resposta))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def listParty(self):
        self.resposta = {}
        try:
            valor = True
            partides = self.partida.find({"online":True},{"_id":False})
            partides_array = []
            for part in partides:
                part["nom"] = str(part["nom"])
                part["online"] = str(part["online"])
                part["maxper"] = str(part["maxper"])
                part["pass"] = str(part["pass"])
                idMaster = str(part["id_master"])
                nomMaster = self.jugadors.find_one({"_id":ObjectId(idMaster)})
                nomMaster = str(nomMaster["nick"])
                print nomMaster
                part["master"] = nomMaster
                partides_array.append(part)
                    
            self.resposta["status"] = "OK"
            self.resposta["msg"] = "Les dades s'han carregat estupendament"
            self.resposta["data"] = partides_array 
            return(json.dumps(self.resposta))
        except:
            self.resposta["status"] = "Error"
            self.resposta["msg"] = "Les dades no s'han pogut consultar"
            return(json.dumps(self.resposta))





application = cherrypy.Application(HorrorWarriors(), script_name=None, config=None)