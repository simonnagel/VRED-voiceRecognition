'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.

Scripted by Rutvik Bhatt and Simon Nagel. Supported by Marcus Fritzen.

Make sure to install pyaudio and speech_recognition

Just paste the Scene in the Script Editor of VRED and press run.
Press A to enable the voice annotation mode.
Immediately start speaking after pressing A .
Take a pause after finish speaking and wait for your audio to process.
Once you see the output in the terminal start speaking again to change the current annotation.
Say 'stop' to stop working on current annotation 
Press A again to create a new annotation.
Say 'remove' to erase your current annotation.
Press S to manually disable voice annotation.

'''


import time
import PySide2.QtGui
import pyaudio
import speech_recognition as sr
from inspect import signature
from datetime import datetime
QVector3D = PySide2.QtGui.QVector3D

#--------------------------------------------------------------------------Defining Annotations----------------------------------------------------------------------
class RenderActionAnnotation(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
    def loop(self):
        annos_VoiceRecog = vrAnnotationService.getAnnotations()
        syncCollabAnnoMaterials()
        
annos_VoiceRecog = vrAnnotationService.getAnnotations()
sentence_ = ""
current_Anno_VoiceRecog = []
current_Anno_VoiceRecog.extend(annos_VoiceRecog)

'''
Intersection Method flag defines where do you want to place the annotation in the scene. 
By default the Intersection Method is set to "RenderWindow" which means the annotation will be placed at the hitpoint with the center of the renderwindow
Set the Intersection Method to "MousePointer" to set the position of the annotation to your mouse pointer
'''
intersectionMethod = "RenderWindow"     

def voiceRecogAnnotationEnable():
    global current_Anno_VoiceRecog
    global vrAnnoFlag
    global stop_listening
    global sentence
    VoiceRecogControl_audio_stop()
    if vrAnnoFlag == False:
        if intersectionMethod == "RenderWindow":
            intersection_VoiceAnno = getSceneIntersection(-1, int(getRenderWindowWidth(-1)/2), int(getRenderWindowHeight(-1)/2))
        elif intersectionMethod == "MousePointer":
            mousePos_VoiceAnno = getMousePosition(-1)
            intersection_VoiceAnno = getSceneIntersection(-1,mousePos_VoiceAnno[0],mousePos_VoiceAnno[1])
            
        interPos_VoiceAnno = intersection_VoiceAnno[1]
        annoNew = createAnnotation("My New Annotation")
        annoNew.setPosition(interPos_VoiceAnno)
   
    annos_VoiceRecog = vrAnnotationService.getAnnotations() 
    r=sr.Recognizer()
    m = sr.Microphone()
    if len(current_Anno_VoiceRecog) != len(annos_VoiceRecog):
        if vrAnnoFlag == False:
            print("You pressed 'A'\n Enabled Voice Annotation")
            def callback(recognizer, audio):
                global sentence
                print("Please wait your audio is being processed")
                try:
                    print("YOU SAID: " + recognizer.recognize_google(audio))
                    #English is default language 'en-US'
                    #use 'fr-FR' for French; 'de-DE' for German etc
                    voice_data = recognizer.recognize_google(audio, language='en-US')
                    sentence = sentence + " " + voice_data
                    anno_VoiceRecog = annos_VoiceRecog[-1]
                    localUser = vrSessionService.getUser()
                    localUserID = vrdSessionUser.getUserId(localUser)
                    UserName = vrdSessionUser.getUserName(localUser)
                    now = datetime.now() 
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    if "stop" in voice_data:
                        voiceRecogAnno_audio_stop()
                    elif "remove" in voice_data:
                        sentence = ""
                    anno_VoiceRecog.setText("User: " +UserName+ "\nTime and Date: " +dt_string+ "\nNote: " +sentence)
                    
                except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        
            stop_listening = r.listen_in_background(m, callback)
            vrAnnoFlag = True
            sentence = ""
            annos_VoiceRecog = vrAnnotationService.getAnnotations()
            del current_Anno_VoiceRecog[:]
            current_Anno_VoiceRecog.extend(annos_VoiceRecog)

def voiceRecogAnno_audio_stop():
    global vrAnnoFlag
    if vrAnnoFlag == True:
        print("You said 'Stop' or pressed 'S' Stopping Annotation\n  Press 'A' again to create a new annotation")
        stop_listening(wait_for_stop=False)
        vrAnnoFlag = False 
        
def VoiceRecogControl_audio_stop():
    global VRCKeyFlag
    try:
        if VRCKeyFlag == True:
            print("You pressed 'B'\n   Stopped Voice Recognition")
            stop_listening(wait_for_stop=False)
            VRCKeyFlag = False
    except:
        print("Please enable the Voice Recognition first")
                
def syncCollabAnnoMaterials():
    allUsers = vrSessionService.getUsers()
    amountAllUsers = len(allUsers)
    localUser = vrSessionService.getUser()
    localUserID = vrdSessionUser.getUserId(localUser)
    localUserColor = vrdSessionUser.getUserColor(localUser)
    vrAnnotationService.setDefaultLineColor(localUserColor)
    
    if vrSessionService.isConnected() != 1:
        # change to a foldername on your PC
        foldername = "c:/tempe/"
        vrAnnotationService.saveAnnotations(vrAnnotationService.getAnnotations(),foldername + "mVoiceAnno2data.xml")
        
key3 = vrKey(Key_S)
key3.connect(voiceRecogAnno_audio_stop)        
renderAnno = RenderActionAnnotation()
vrAnnoFlag = False
key4 = vrKey(Key_A)
key4.connect(voiceRecogAnnotationEnable)

vrLogInfo("Welcome to Voice Annotation!\nPress A to enable the voice Annotation mode\nImmediately start speaking after pressing A \nTake a pause after finish speaking and wait for your audio to process\nOnce you see the output in the terminal start speaking again to change the current annotation\nSay 'stop' to stop working on current annotation and press A again to create a new annotation\nSay 'remove' to erase your current annotation\nPress S to manually disable voice recognition")


