#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''!Fichier main
'''
import syslog
import sys
import os
import time
import io
import ConfigParser
import cups
import RPi.GPIO as GPIO
import pygame
import render
import picamera

TEMPPATH = '/dev/shm/'

JOYBUTTONA = 1
JOYBUTTONB = 2
JOYBUTTONUP = 10
JOYBUTTONDOWN = 11
JOYBUTTONLEFT = 12
JOYBUTTONRIGHT = 13
JOYBUTTONSELECT = 8
JOYBUTTONSTART = 9

class Photomaton:
    '''!Classe du menu photomaton
    '''
    def __init__(self):
        '''!Initialisation
        '''
        os.environ['DISPLAY'] = ':0.0'
        pygame.init()
        self.curdir = os.path.split(os.path.realpath(__file__))[0]
        conf = ConfigParser.ConfigParser()
        conf.read(os.path.join(self.curdir, 'photomaton.conf'))
        self.conf = conf
        self.sleeptime = int(conf.get('MENU', 'sleeptime'))
        self.printtime = int(conf.get('MENU', 'printtime'))
        self.gpioport = int(conf.get('MENU', 'gpioport'))
        self.flash = int(conf.get('MENU', 'flash'))
        ftcolor = conf.get('MENU', 'fontcolor')
        self.fontcolor = (int(ftcolor[:2], 16), int(ftcolor[2:4], 16), int(ftcolor[4:6], 16))
        ##La webcam: PiCamera class
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpioport, GPIO.OUT, initial=GPIO.HIGH)
        pygameinfo = pygame.display.Info()
        size = (pygameinfo.current_w, pygameinfo.current_h)
        self.destdir = conf.get('RENDU', 'destdir')
        self.testmode = int(conf.get('DEV', 'testmode'))
        ##Largeur de l'écran
        self.width = pygameinfo.current_w
        ##Hauteur de l'écran
        self.height = pygameinfo.current_h
        ##Taille de la police
        self.fontsize = int(conf.get('MENU', 'fontsize'))
        ##Choix de la police
        self.font = pygame.font.Font(os.path.join(self.curdir, conf.get('MENU', 'font')), self.fontsize)
        ##Surface pygame
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        ##Nombre de photos à prendre. Attention à vérifier que Assemble gère ce nombre de photos
        self.nbphotos = 6
        self.check_erreurs(check_cam=True)
        self.camera = picamera.PiCamera()
        pygame.joystick.Joystick(0).init()
        self.run()

    def prendre_photo(self, highres=True, flash=True):
        '''! Prendre une photo en raw via la webcam raspberry V1.2
        @param highres shoot en 2592x1944 si vrai, 640x480 sinon
        @param flash Alume le flash au moment de la photo
        @return Pygame image data
        '''
        if flash:
            self.flash_on()
        image = io.BytesIO()
        time1 = time.time()
        if highres:
            self.camera.resolution = (2592, 1944)
            self.camera.capture(image, format='rgba', use_video_port=False)
            resolution = (2592, 1952)#Note: Resolution trick!! C'est hyper crade, pas trouvé mieux.
        else:
            self.camera.resolution = (640, 480)
            self.camera.capture(image, format='rgba', use_video_port=True)
            resolution = (640, 480)
        img = pygame.image.fromstring(image.getvalue(), resolution, 'RGBA').convert()
        if highres and img.get_at((10, 10))[:3] == (0, 0, 0):
            #Bug de la picam 1.2. Elle renvoie une image noire. Dans ce cas, on reprends
            print('image noire, on reprends')
            img = self.prendre_photo(highres, flash)
        self.flash_off()
        if highres:
            print('photo prise en', time.time() - time1, 'secondes')
        syslog.syslog(syslog.LOG_INFO, 'Photo prise')
        return img

    def flash_on(self):
        '''!Allumer les spots
        '''
        print('flash ON')
        #délai de mise en marche
        #time.sleep(0.2)
        GPIO.output(self.gpioport, GPIO.LOW)

    def flash_off(self):
        '''!Eteindre les spots
        '''
        print('flash OFF')
        GPIO.output(self.gpioport, GPIO.HIGH)

    def check_erreurs(self, check_cam=False):
        '''!Vérifier que tout fonctionne. Bloque jusqu'à ce que tout soit OK
        '''
        while not self._check_erreurs(check_cam):
            time.sleep(1)

    def _get_image_path(self, imagename):
        imgdir = os.path.join(self.curdir, 'images')
        return os.path.join(imgdir, imagename)

    def _check_erreurs(self, check_cam=False):
        if check_cam:
            try:
                cam = picamera.PiCamera()
                cam.close()
            except picamera.exc.PiCameraError:
                self.showtext(u'Erreur: Webcam absente!', color=(255, 0, 0), fill=True, flip=False)
                img = pygame.image.load(self._get_image_path('ErrorWebcam.png')).convert_alpha()
                self.screen.blit(img, (self.screen.get_width() - img.get_width() - 10, 10))
                pygame.display.flip()
                syslog.syslog(syslog.LOG_INFO, 'Webcam absente')
                return False
        if pygame.joystick.get_count() != 1:
            self.showtext(u'Erreur: Joystick absent!', color=(255, 0, 0), fill=True, flip=False)
            img = pygame.image.load(self._get_image_path('ErrorManette.png')).convert_alpha()
            self.screen.blit(img, (self.screen.get_width() - img.get_width() - 10, 10))
            pygame.display.flip()
            syslog.syslog(syslog.LOG_INFO, 'Joystick absent')
            return False
        if (os.statvfs(self.destdir).f_bavail * os.statvfs(self.destdir).f_frsize)/1024 < 4000:
            self.showtext(u'Erreur: Espace disque insuffisant!', color=(255, 0, 0), fill=True, flip=False)
            img = pygame.image.load(self._get_image_path('ErrorDisk.png')).convert_alpha()
            self.screen.blit(img, (self.screen.get_width() - img.get_width() - 10, 10))
            pygame.display.flip()
            syslog.syslog(syslog.LOG_INFO, 'Espace disque insuffisant')
            return False
        if render.Render().get_ip() == '127.0.0.1':
            self.showtext(u'Erreur: Erreur réseau!', color=(255, 0, 0), fill=True, flip=False)
            img = pygame.image.load(self._get_image_path('ErrorNetwork.png')).convert_alpha()
            self.screen.blit(img, (self.screen.get_width() - img.get_width() - 10, 10))
            pygame.display.flip()
            syslog.syslog(syslog.LOG_INFO, 'Erreur de configuration réseau')
            return False
        try:
            #Bus 001 Device 006: ID 04a9:327a Canon, Inc.
            conn = cups.Connection()
            printers = conn.getPrinters()
            if len(printers) != 1:
                self.showtext(u'Erreur: Imprimante non connectée!', color=(255, 0, 0), fill=True, flip=False)
                img = pygame.image.load(self._get_image_path('ErrorPrinter.png')).convert_alpha()
                self.screen.blit(img, (self.screen.get_width() - img.get_width() - 10, 10))
                pygame.display.flip()
                syslog.syslog(syslog.LOG_INFO, 'Imprimante non connectee')
                return False
        except RuntimeError as erreur:
            print(erreur)
            self.showtext(u'Erreur: Erreur de connexion au serveur CUPS', color=(255, 0, 0), fill=True, flip=False)
            img = pygame.image.load(self._get_image_path('ErrorPrinter.png')).convert_alpha()
            self.screen.blit(img, (self.screen.get_width() - img.get_width() - 10, 10))
            pygame.display.flip()
            syslog.syslog(syslog.LOG_INFO, 'Impossible de se connecter au serveur d\'impression')
            return False
        return True

    def run(self):
        '''!Démarre l'interface graphique
        '''
        pygame.key.set_repeat(35, 65)
        pygame.mouse.set_visible(False)
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.JOYBUTTONDOWN])
        while True:
            if self.testmode:
                self.prendre_photos()
                continue
            self.check_erreurs()
            self.showtext('Appuyer sur A ou B', color=self.fontcolor, offset=160-self.height/2, fill=True, flip=False)
            img = pygame.image.load(self._get_image_path('NES.png')).convert_alpha()
            img = pygame.transform.smoothscale(img, (int(458), int(280)))
            self.screen.blit(img, (self.width/2 - 230, 250))
            pygame.event.clear()
            pygame.display.flip()
            print('wait...')
            event = pygame.event.wait()
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                print('À la prochaine!')
                pygame.quit()
                syslog.syslog(syslog.LOG_INFO, 'Sortie à la demande de l\'utilisateur')
                sys.exit(0)
            elif event.type == pygame.JOYBUTTONDOWN:
                print('bouton pressé:', event.button)
                if event.button in [JOYBUTTONA, JOYBUTTONB]:
                    self.prendre_photos()
                elif event.button == JOYBUTTONSTART:
                    self.admin_menu()

    @staticmethod
    def _reboot():
        syslog.syslog(syslog.LOG_INFO, 'Redémarrage à la demande de l\'utilisateur')
        os.system('sudo reboot')

    def _activer_flash(self):
        self.flash = True

    def _desactiver_flash(self):
        self.flash = False

    @staticmethod
    def _shutdown():
        os.system('sudo shutdown -h now')

    @staticmethod
    def _quit():
        syslog.syslog(syslog.LOG_INFO, 'Sortie à la demande de l\'utilisateur')
        sys.exit(0)

    @staticmethod
    def get_event():
        '''!Récupère un évènement de console NES
        '''
        pygame.event.clear()
        while True:
            if pygame.joystick.Joystick(0).get_axis(0) > 0:
                return JOYBUTTONRIGHT
            if pygame.joystick.Joystick(0).get_axis(0) < 0:
                return JOYBUTTONRIGHT
            if pygame.joystick.Joystick(0).get_axis(1) < 0:
                return JOYBUTTONUP
            if pygame.joystick.Joystick(0).get_axis(1) > 0:
                return JOYBUTTONDOWN
            myevent = pygame.event.poll()
            if myevent != pygame.NOEVENT:
                if myevent.type == pygame.JOYBUTTONDOWN:
                    return myevent.button

    def admin_menu(self):
        '''!Menu d'administration du photomaton. Déclanché par la touche start sur le menu de base
        '''
        if self.flash:
            commands = {u'Redémarrer le photomaton': self._reboot, 'Arreter le photomaton': self._shutdown, u'Quitter le programme': self._quit, u'Annuler': None, u'Désactiver le flash': self._desactiver_flash}
        else:
            commands = {u'Redémarrer le photomaton': self._reboot, 'Arreter le photomaton': self._shutdown, u'Quitter le programme': self._quit, u'Annuler': None, u'Activer le flash': self._activer_flash}

        arrow = pygame.image.load(self._get_image_path('arrow.png')).convert_alpha()
        arrow = pygame.transform.smoothscale(arrow, (arrow.get_width()/5, arrow.get_height()/5))
        current = commands.keys().index(u'Annuler')
        #Boucle de contrôle
        self.background()
        while True:
            yoffset = 5
            #Affichage des options
            for i in range(len(commands)):
                text = commands.keys()[i]
                img = self.font.render(text, 1, (255, 255, 255))
                self.screen.blit(img, (arrow.get_width() + 50, yoffset))
                if i == current:
                    self.screen.blit(arrow, (10, yoffset + img.get_height() / 2 - arrow.get_height() / 2))
                yoffset += 20 + img.get_height()
            pygame.display.flip()
            #Traitement des entrées utilisateur
            bouton = self.get_event()
            if bouton in [JOYBUTTONA, JOYBUTTONB]:
                text = commands.keys()[current]
                if text == u'Annuler':
                    return
                commands[text]()
                if 'le flash' in text:
                    return
            elif bouton == JOYBUTTONUP:
                current -= 1
                self.background()
            elif bouton == JOYBUTTONDOWN:
                current += 1
                self.background()
            current = current % len(commands)

    def background(self):
        '''!Selection du fond d'écran
        '''
        img = pygame.image.load(os.path.join(self.curdir, self.conf.get('MENU', 'background'))).convert()
        self.screen.blit(img, (0, 0))

    def prendre_photos(self):
        '''!Prendre une série de self.nbphotos photos et demande une impression
        '''
        self.check_erreurs()
        photolist = []
        for photonb in range(0, self.nbphotos):
            time1 = time.time()
            self.background()
            pygame.display.flip()
            #Affiche le compte à rebours et l'aperçu
            self.screen.blit(self.font.render('photo {} sur {}'.format(photonb + 1, self.nbphotos), 2, self.fontcolor), (0, 0))
            while self.sleeptime - int(time.time()-time1) > 0:
                print('capture photo:', photonb)
                counter = self.sleeptime - int(time.time()-time1)
                img = pygame.image.load(self._get_image_path('{}.png'.format(counter))).convert()
                self.screen.blit(img, (self.width/2 - 36, 50))
                preview = self.prendre_photo(highres=False, flash=False)
                preview = pygame.transform.smoothscale(preview, (320, 240))
                self.screen.blit(preview, (self.width/2 - 160, 200))
                pygame.display.flip()
            #Affichage de l'image
            self.screen.fill((255, 255, 255))
            pygame.display.flip()
            img = self.prendre_photo(highres=True, flash=self.flash)
            photolist.append(img)
            img = pygame.transform.smoothscale(img, (self.width, self.height))
            self.screen.blit(img, (0, 0))
            pygame.display.flip()
            time.sleep(2)
        #Pour patienter pendant le traitement de l'image
        self.background()
        img = pygame.image.load(self._get_image_path('coyote_rocket_by_mreiof-d5va4sl.jpg')).convert_alpha()
        img = pygame.transform.smoothscale(img, (self.screen.get_width(), self.screen.get_height()))
        self.screen.blit(img, (0, 0))
        self.showtext(u'Génération en cours, patientez!!', color=self.fontcolor, fill=False, flip=True, scale=3)
        #Photo rendering. Voir render.py
        filename = render.Render().gen(photolist)
        #Ecran d'impression
        self.background()
        img = pygame.image.load(filename).convert()
        img = pygame.transform.smoothscale(img, (int(img.get_width() * (float(self.height)/img.get_height())), self.height))
        self.screen.blit(img, (self.screen.get_width() / 2 - img.get_width() / 2, 0))
        self.showtext('Valider pour imprimer', color=self.fontcolor, fill=False, flip=False)
        #Afficher le qrcode à droite
        img = pygame.image.load(os.path.join(TEMPPATH, 'qrcode.png')).convert()
        img = pygame.transform.smoothscale(img, (166, 166))
        self.screen.blit(img, (self.screen.get_width() - img.get_width(), 0))
        #Images imprimer OUI/NON FLECHE??
        img = pygame.image.load(self._get_image_path('KO.png')).convert_alpha()
        img = pygame.transform.smoothscale(img, (self.width/4 - 14, self.height/4 + 20))
        self.screen.blit(img, (0, self.height/2))
        img = pygame.image.load(self._get_image_path('OK.png')).convert_alpha()
        img = pygame.transform.smoothscale(img, (self.width/4 - 14, self.height/4 + 20))
        self.screen.blit(img, (self.width - img.get_width(), self.height/2))
        pygame.display.flip()
        #En attente de choix utilisateur
        pygame.event.clear()
        if self.testmode:
            return
        while True:
            event = pygame.event.wait()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == JOYBUTTONA:
                    self.imprimer(filename)
                return

    def imprimer(self, filename):
        '''!Envoie la photo à l'imprimante. Génère un QRCode.
        @param filename Le fichier à imprimer
        '''
        self.check_erreurs()
        syslog.syslog(syslog.LOG_INFO, 'Impression')
        #impression sauvage
        self.showtext('Impression en cours..', color=self.fontcolor, flip=False, fill=True)
        img = pygame.image.load(os.path.join(TEMPPATH, 'qrcode.png')).convert()
        img = pygame.transform.smoothscale(img, (200, 200))
        self.screen.blit(img, (0, 0))
        pygame.display.flip()
        conn = cups.Connection()
        print('impression demandée!!')
        conn.printFile(conn.getPrinters().keys()[0], filename, title='IMG', options={'StpBorderless': 'True'})
        #temporisation avec barre de chargement
        for i in range(self.printtime * 10, 0, -1):
            #TODO -> cups status guttenprint
            progress = (self.printtime * 10.0 - i)/(self.printtime * 10)
            pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(0, 400, int((self.width - 20) * progress), 30))
            pygame.display.flip()
            time.sleep(.1)
        #attente d'action utilisateur
        self.showtext('Appuyer sur une touche...', color=self.fontcolor, offset=100, fill=False)
        pygame.event.clear()
        pygame.event.wait()
        #nettoyage
        #Vide la file d'impression. Evite les bugs en cas de fin de papier ou remplacement cartouche
        conn.cancelAllJobs(conn.getPrinters().keys()[0])

    def showtext(self, text, color=(255, 255, 255), fill=True, offset=0, flip=True, scale=1):
        '''!Affiche un texte sur la surface
        @param text Le texte a afficher
        @param color La couleur du texte
        @param fill Ecraser avec le fond d'écran
        @param offset L'offset y par rapport au centre de l'écran
        @param flip Rafraichir l'affichage
        '''
        if fill:
            self.background()
        img = self.font.render(text, int(scale), color)
        coordx = self.width / 2 - img.get_width() / 2
        coordy = self.height / 2 - img.get_height() + offset
        self.screen.blit(img, (coordx, coordy))
        if flip:
            pygame.display.flip()

if __name__ == '__main__':
    syslog.syslog(syslog.LOG_INFO, 'Demarrage du photomaton')
    while True:
        Photomaton()
        try:
            syslog.syslog(syslog.LOG_INFO, 'Lancement')
            Photomaton()
        except Exception as error:
            print('Erreur:', str(error))
            syslog.syslog('Erreur: ' + str(error))
        time.sleep(1)
