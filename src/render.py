#!/usr/bin/python
# -*- coding:utf-8 -*-
'''!Fichier de rendu
'''
import time
import socket
import struct
import os
import configparser
import pygame
#custom imports
import qrcode
import logger

class Render:
    '''!Classe de génération du qrcode
    '''
    def __init__(self):
        '''!Initialisation
        '''
        self.curdir = os.path.split(os.path.realpath(__file__))[0]
        conf = configparser.ConfigParser()
        conf.read(os.path.join(self.curdir, 'photomaton.conf'))
        self.temppath = conf.get('CONF', 'temppath')

    @staticmethod
    def get_default_gateway_linux():
        '''!Read the default gateway directly from /proc
        @return L'adresse IP de la gateway
        '''
        with open('/proc/net/route') as routefile:
            for line in routefile:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
                return socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))

    def get_ip(self):
        '''!Récupère mon adresse IP
        @return L'adresse IP
        '''
        try:
            return [(s.connect((self.get_default_gateway_linux(), 67)),
                     s.getsockname()[0], s.close())
                    for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        except:
            return '127.0.0.1'

    def genqrcode(self, filename):
        '''!Générer un qrcode pointant vers filename
        @param filename La cible du lien
        '''
        url = 'http://{}/img/{}'.format(self.get_ip(), os.path.split(filename)[-1])
        print('url:', url)
        logger.logger.logEvent(logger.LOG_INFO, 'Image générée: {}'.format(filename))
        myqr = qrcode.QRCode(version=2, border=1)
        myqr.add_data(url)
        myqr.make(fit=True)
        image = myqr.make_image()
        image.save(os.path.join(self.temppath, 'qrcode.png'))

    @staticmethod
    def generate_render(piclist):
        '''!Générer l'image finale a partir des photos.
        @param piclist La liste des chemins complets des images.
        @return Le chemin complet vers l'image générée.
        '''
        print('on render, courage!')
        time1 = time.time()
        assembler = Assemble(piclist)
        out = assembler.filename()
        time2 = int(time.time() - time1)
        print(out, 'fait en', time2, 'secondes')
        logger.logger.logEvent(logger.LOG_INFO, 'Rendu effectué en {} secondes'.format(time2))
        return out

    def gen(self, piclist):
        '''!Génère une image et un qrcode à partir des images.
        @return Le chemin complet vers le qrcode généré
        '''
        filename = self.generate_render(piclist)
        del piclist
        self.genqrcode(filename)
        return filename

class Assemble:
    '''!Assemble les photos pour le résultat final
    '''
    def __init__(self, photolist):
        '''!Constructeur
        '''
        self.curdir = os.path.split(os.path.realpath(__file__))[0]
        conf = configparser.ConfigParser()
        conf.read(os.path.join(self.curdir, 'photomaton.conf'))
        ##Résolution du rendu
        self.resolution = (5700, 8500)
        ##Résolution des photos en sortie de webcam
        self.photoscale = (2592, 1952)
        ##Image de la banderole pied de page
        self.banderole = conf.get('RENDU', 'banderole')
        ##Largeur de la banderole (ratio de la largeur totale)
        self.banderolewidth = float(conf.get('RENDU', 'banderolewidth'))
        ##Images du pied de page
        self.piedpage1 = conf.get('RENDU', 'piedpage1')
        ##Couleur fond d'écran
        bgcolor = conf.get('RENDU', 'bgcolor')
        self.bgcolor = (int(bgcolor[:2], 16), int(bgcolor[2:4], 16), int(bgcolor[4:6], 16))
        ##Largeur du pied de page
        self.piedpage1width = int(conf.get('RENDU', 'piedpage1width'))
        ##Largeur de la police
        self.fontsize = int(conf.get('RENDU', 'fontsize'))
        ##Initialisation de la fonte
        self.font = pygame.font.Font(os.path.join(self.curdir,
                                                  conf.get('RENDU', 'font')),
                                     self.fontsize)
        ##Répertoire de destination
        self.destdir = conf.get('RENDU', 'destdir')
        ##Fichier de destination
        self.output = os.path.join(self.destdir,
                                   '{}.jpg'.format(time.strftime('%H-%M-%S-%d%m%Y')))
        ##redimentionnement des photos
        for i in range(len(photolist)):
            photolist[i] = pygame.transform.scale(photolist[i], self.photoscale)
        ##Surface utilisée pour le rendu
	##beaucoup de RAM!
        self.surface = pygame.surface.Surface(self.resolution)
        self.photoxmarge = 220
        self.photoymarge = 50
        self.photoiniymarge = 350
        self.set_bg()
        self.addphotos(photolist)
        del photolist
        self.ajoutbanderole()
        self.set_footer()
        self.save()

    def filename(self):
        '''!Récupère le fichier de destination utilisé par save
        @return Le nom du fichier
        '''
        return self.output

    def set_bg(self):
        '''!Configure le fond d'écran
        '''
        self.surface.fill(self.bgcolor)

    def ajoutbanderole(self):
        '''!Ajout de la banderole sous les photos
        '''
        if self.banderole:
            img = pygame.image.load(os.path.join(self.curdir, self.banderole)).convert_alpha()
            img = pygame.transform.scale(img, (int(self.resolution[0] * self.banderolewidth),
                                               int(img.get_height() *
                                                   ((self.resolution[0] *
                                                     self.banderolewidth)/float(img.get_width())))))
            self.surface.blit(img, (self.resolution[0]/2 - img.get_width()/2,
                                    self.photoscale[1] * 3 + 3 *
                                    self.photoymarge + 50 + self.photoiniymarge))

    def set_footer(self):
        '''!Ajout de l'image en pied de page
        '''
        ymarge = 300
        #pied de page 1
        img = pygame.image.load(os.path.join(self.curdir, self.piedpage1)).convert_alpha()
        yimg1 = int(img.get_height() *  float(self.piedpage1width) / img.get_width())
        img = pygame.transform.scale(img, (self.piedpage1width, yimg1))
        self.surface.blit(img, (self.surface.get_width()/2 - img.get_width()/2,
                                self.resolution[1] - yimg1 - ymarge))

    def save(self):
        '''!Sauver l'image générée
        '''
        print('on sauve')
        time1 = time.time()
        pygame.image.save(self.surface, self.output)
        print('sauvée en:', time.time() - time1, 'secondes')

    def addphotos(self, photolist):
        '''!Ajout des photos sur la surface
        @param photolist la liste des 6 images pygame
        '''
        xright = self.resolution[0] - self.photoxmarge - self.photoscale[0]
	    #Rendering photos
        #LIGNE 3
        yoffset = self.photoscale[1] * 2 + self.photoymarge * 3 + self.photoiniymarge
        self.surface.blit(photolist[5], (xright, yoffset))
        self.surface.blit(photolist[4], (self.photoxmarge, yoffset))
        #LIGNE 2
        yoffset = self.photoscale[1] + self.photoymarge * 2 + self.photoiniymarge
        self.surface.blit(photolist[3], (xright, yoffset))
        self.surface.blit(photolist[2], (self.photoxmarge, yoffset))
        #LIGNE 1
        yoffset = self.photoymarge + self.photoiniymarge
        self.surface.blit(photolist[1], (xright, yoffset))
        self.surface.blit(photolist[0], (self.photoxmarge, yoffset))

if __name__ == '__main__':
    '''
    Test
    '''
    pygame.init()
    pygame.display.set_mode((5700, 8500,))
    TIME1 = time.time()
    ASSEMBLER = Assemble([pygame.image.load('/tmp/tmp.GAmKy2J90o.jpg')]*6)
    print(ASSEMBLER.filename(), 'généré en', time.time() - TIME1, 'secondes')
