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
Press V to enable the voice recognition mode.
Immediately start speaking after pressing V .
Take a pause after finish speaking and wait for your audio to process.
Once you see the output in the terminal start speaking again .
Press B to manually disable voice recognition.

'''


import time
import PySide2.QtGui
import pyaudio
import speech_recognition as sr
from inspect import signature
from datetime import datetime
QVector3D = PySide2.QtGui.QVector3D

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)
    
    
    
#----------------------------------------------------------Keyword function registration---------------------------------------------------------------------------------
keywordFunctions = {}
def VoiceRecogControlEnable():
    global VRCKeyFlag
    global stop_listening
    r = sr.Recognizer()
    m = sr.Microphone()
    voiceRecogAnno_audio_stop()
    if VRCKeyFlag == False:
        def callback(recognizer, audio):
            global sentence
            global voice_data
            global voice_dataR
            global split_voice_data
            i = 0
            try:
                print("Please wait audio is being processed\n")
                # English is the default language change 'en-US' to 'de-DE' for German or 'fr-FR' for French etc
                voice_data = recognizer.recognize_google(audio, language ='en-US')
                voice_dataR = voice_data.replace(" ", "")
                print("YOU SAID: " + voice_data)

                split_voice_data = [word.lower() for word in voice_data.split()]
                print(split_voice_data)
                # Check recorded data for a keyword
                for word in split_voice_data:
                    if word in keywordFunctions:
                        print("Found matching keyword ", word)
                        nextWordIndex = split_voice_data.index(word) + 1
                        remainingWords = split_voice_data[nextWordIndex:]
                        # Test if we have sufficient remaining words for passing as args to function
                        expectedArgs = keywordFunctions[word][0]
                        #print(expectedArgs)
                        if len(remainingWords) > expectedArgs:
                            newRemainingWords = remainingWords[0:expectedArgs-1]
                            print(newRemainingWords)
                            joinedStr = ' '.join(remainingWords[expectedArgs-1:])
                            print(joinedStr)
                            newRemainingWords.append(joinedStr)
                            print(newRemainingWords)
                            keywordFunctions[word][1](*newRemainingWords)
                            break       
                        elif len(remainingWords) == expectedArgs:
                            # Take the expected arguments amount of words after the keyword and pass to function
                            keywordFunctions[word][1](*remainingWords[0:expectedArgs])
                            break
                        else:
                            print("Detected to less spoken arguments")
                            print("Expected ", expectedArgs)
                            print("Got ", len(remainingWords))

            except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            
        print("You pressed 'V'\n   Enabled Voice Recognition")
        stop_listening = r.listen_in_background(m, callback)
        VRCKeyFlag = True

def VoiceRecogControl_audio_stop():
    global VRCKeyFlag
    try:
        if VRCKeyFlag == True:
            print("You pressed 'B'\n   Stopped Voice Recognition")
            stop_listening(wait_for_stop=False)
            VRCKeyFlag = False
    except:
        print("Please enable the Voice Recognition first")

def voiceRecogAnno_audio_stop():
    global vrAnnoFlag
    if vrAnnoFlag == True:
        print("You said 'Stop' or pressed 'S' Stopping Annotation\n  Press 'A' again to create a new annotation")
        stop_listening(wait_for_stop=False)
        vrAnnoFlag = False 

def registerKeywordFunction(keywords, function):
    global keywordFunctions
    sig = signature(function)
    args = len(sig.parameters)
    print("Registered function with " + str(args) + " parameters")
    for keyword in keywords:
        keywordFunctions[keyword] = (args, function)                
   
#--------------------------------------------------------------Register and Add custom functions here----------------------------------------------------------------------------

'''
# Register custom functions here
Define the keywords first. It might make sense to add similar words in the list.
i.E. move or roof will call the function myMove

The words that are said after the keyword will be your argument.
The Amount of Arguments will be Autodetected from the function.
i.E. myMove requires two arguments: direction and valueStr

If there are more words than required arguments, the last spoken words will be taken as one last arguement.
i.E. selVar requires one argument that can consist of mulitple words (variant names tend to be more than one word)


'''
def mainKeywords():
    registerKeywordFunction(["move", "roof"], myMove)
    registerKeywordFunction(["select"], ourSelectFunction)
    registerKeywordFunction(["variant","radiants","Marion"], selVar)
    registerKeywordFunction(["rotate"], ourRotateFunction)

        
# Custom functions can be defined here
def myMove(direction, valueStr):
    node = getSelectedNode()
    pos = getTransformNodeTranslation(node, 0)
    try:
        if direction.lower() == "up" or direction.lower() == "app":
            setTransformNodeTranslation(node, pos.x(), pos.y(), pos.z() + float(valueStr), False)
            print("\n   The node '"+str(node.getName()+"' was move up by "+str(valueStr) + " mm.\n"))
        elif direction.lower() == "down":
            setTransformNodeTranslation(node, pos.x(), pos.y(), pos.z() - float(valueStr), False)
            print("\n   The node '" +str(node.getName()+ "' was move down by "+str(valueStr) + " mm.\n"))
        elif direction.lower() == "left":
            setTransformNodeTranslation(node, pos.x(), pos.y() - float(valueStr), pos.z(), False)
            print("\n   The node '"+str(node.getName()+"' was move down by "+str(valueStr) + " mm.\n"))
        elif direction.lower() == "right":
            setTransformNodeTranslation(node, pos.x(), pos.y()  + float(valueStr), pos.z(), False)
            print("\n   The node '"+str(node.getName()+"' was move right by "+str(valueStr) + " mm.\n"))
        else:
            print("\n   Please provide two valid argument after 'Move' for ex. 'Move up 500' or 'Move left 300'")
    except:
        print("Please provide an integer after 'Move up' for ex. Move up 500")
        
def ourRotateFunction(ourArgument):
    try:
        node = getSelectedNode()
        rot = getTransformNodeRotation(node)
        setTransformNodeRotation(node,rot.x(),rot.y(),float(ourArgument))
        print("\n   The node '"+str(node.getName()+"' was rotated by "+str(ourArgument) + " degrees.\n"))
    except:
        print("\n   Please provide an integer after the argument, For ex. Rotate 180")  

def ourSelectFunction(ourArgument):  
    ourArgumentCap = ourArgument.title()
    selectNode(ourArgumentCap)
    print("\n   The node '"+str(ourArgument)+"' was selected.\n")

def selVar(ourArgument):
    global voice_data
    global voice_dataR
    allVars = getVariantSets()
    variantFound = False        
    for variant in allVars:
        variantInVoiceData = variant.lower() in voice_data 
        variantInSplitVoiceData = variant.lower() in split_voice_data 
        variantInRVoiceData = variant.lower() in voice_dataR
        if variantInVoiceData or variantInSplitVoiceData or variantInRVoiceData:
            selectVariantSet(variant)
            variantFound = True
    if variantFound == False:
        print("\n   Could not find variant set'"+str(ourArgument)+"'")
    else:
        print("\n   The variant set '"+str(ourArgument)+"' was executed.\n")

mainKeywords()
key2 = vrKey(Key_B)
key2.connect(VoiceRecogControl_audio_stop)

VRCKeyFlag = False
key = vrKey(Key_V)
key.connect(VoiceRecogControlEnable)

vrLogInfo("Welcome to Voice Recognition!\nPress V to enable the voice recognition mode\nImmediately start speaking after pressing V \nTake a pause after finish speaking and wait for your audio to process\nOnce you see the output in the terminal start speaking again \nPress B to manually disable voice recognition")



