#!/usr/bin/env python
#
#Copyright (c) 2014, Philip Cass <frymaster@127001.org>
#
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#
#- Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#- Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#- Neither the name of localhost, 127001.org, eve-bot nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.

#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#
#http://frymaster.127001.org/mumble

from mumbleclient import MumbleClient
from mumbleclient import MumbleControlProtocol

import heapq
import time
import sys
import optparse
import random
import urllib
import urllib2

from twisted.internet import reactor, task


class AutoQuoteClient(MumbleClient.AutoChannelJoinClient):

    quotes = []
    lastResponse = 0
    responseDelay=30
    def loadQuotesFile(self,quotefile):
        with open(quotefile,'r') as memular:
            for quote in memular:
                if quote.strip()!="":
                    self.quotes.append(quote.strip())

    def sendRandomQuote(self):
        self.sendTextMessage(self.quotes[int(random.random()*len(self.quotes))])
        #v = task.deferLater(reactor,self.settings.delayTime,self.sendRandomQuote)
        #v.addErrback(self.errorCallback)

    def VoiceMessageReceived(self,prefix,session,data,TCP=False):
        #print(prefix,self.state.users[session].name,data)
        if self.state.users[session].name=="Norris":
            with open("recorded.aud",'ab') as norrfile:
                #self.sendVoiceMessage(prefix+data)
                print(len(prefix+data))
                norrfile.write((prefix+data)+"&*(*&")
        pass

    def TextMessageReceived(self,message):
        sender = self.state.users[message.actor].name
        if( self.channelID in message.channel_id and #we are being broadcast to
           ("mwo" in message.message.lower() or 
            "mechwarrior" in message.message.lower() or 
            "pgi" in message.message.lower() or 
            " fun" in message.message.lower() or
            "games" in message.message.lower() or
            "robots" in message.message.lower())):
            if (self.lastResponse+self.responseDelay)<time.time():
                self.lastResponse = time.time()
                self.sendTextMessage("%s, This is the Star Citizen channel." %sender)
                return

        if(message.message.lower().startswith("!help")):
                self.sendTextMessage("Usable Commands:\n!help\n!dice\n!flip\n!recipe\n!ark\n!kong\n!suggest")
        if(message.message.lower().startswith("!dice ")):
            try:
                num = int(message.message.split(" ")[1])
                self.sendTextMessage(str(int(random.random()*num+1)))
            except Exception, e: pass
        if(message.message.lower().startswith("!flip")):
            if random.random()>0.5:
                self.sendTextMessage("Heads")
            else:
                self.sendTextMessage("Tails")
        if(message.message.lower().startswith("!recipe")):
            try:
                #retrieve a random recipe and update the RSS feed if past a timer
                #http://www.eatingwell.com/eatingwell_rss_feeds
                self.sendTextMessage("Not Implemented yet...")
            except Exception, e: pass
        if(message.message.lower().startswith("!norris")):
            #try:
                with open("recorded.aud",'rb') as norrfile:
                    data = norrfile.read()
                    for line in data.split("&*(*&"):
                        #line = line.strip()
                        print(len(line))
                        self.sendVoiceMessage(line)
                        #time.sleep(0.05)
            #except Exception, e: pass

        if(message.message.lower().startswith("!meme")):
            #try:
                with open("recorded3.aud",'rb') as norrfile:
                    data = norrfile.read()
                    for line in data.split("&*(*&"):
                        #line = line.strip()
                        print(len(line))
                        self.sendVoiceMessage(line)
                        time.sleep(0.00001)

        if(message.message.lower().startswith("!move ")):
            if "dudeb" in sender.lower() or "borgdorg" in sender.lower():
                channel_name = message.message[6:]
                found=False
                print("number of channels: %s" %len(self.state.channels))
                for i,channel in self.state.channels.iteritems():
                    print(i,channel.name)
                    if channel.name.lower()==channel_name.lower():
                        channel_id_to_move=i
                        found=True
                        break
                if found:
                    newMessage = MumbleControlProtocol.UserState()
                    newMessage.session = self.sessionID
                    newMessage.channel_id=channel_id_to_move
                    self.sendMessage(newMessage)
                else:
                    self.sendTextMessage("Channel does not exist: %s" % channel_name)
                    

        if(message.message.lower().startswith("!ark ")):
            try:
                #generate server listing of people on that ark server name
                self.sendTextMessage("Not Implemented yet...")
            except Exception, e: pass
        if(message.message.lower().startswith("!kong ")):
            try:
                #show what kong is playing from steam
                self.sendTextMessage("Not Implemented yet...")
            except Exception, e: pass
        if(message.message.lower().startswith("!suggest")):
            try:
                print(message.message)
                with open("suggestions.txt",'a') as sugFile:
                    sugFile.write("%s\t%s\n"%(self.state.users[message.actor].name,message.message))
                self.sendTextMessage("Noted")
            except Exception, e: pass





        
    def ServerSyncReceived(self,message):
        self.loadQuotesFile(self.settings.quotefile)
        #v = task.deferLater(reactor,5,self.sendRandomQuote)
        #v.addErrback(self.errorCallback)

    def connectionLost(self,reason):
        if reactor.running: reactor.stop()

def main():
    p = optparse.OptionParser(description='Mumble 1.2 relaybot to relay comms from a match channel to a spectator channel, with a time delay e.g. if watching on a delayed SourceTV server. Full documentation is available at http://frymaster.127001.org/mumble',
                prog='kaelus-krew.py',
                version='%prog 2.0',
                usage='\t%prog -e \"Match Channel\" -r \"Spectator Channel\"')

    p.add_option("-c","--channel",help="Channel to start in (MANDATORY)",action="store",type="string")
    p.add_option("-s","--server",help="Host to connect to (default %default)",action="store",type="string",default="localhost")
    p.add_option("-p","--port",help="Port to connect to (default %default)",action="store",type="int",default=64738)
    p.add_option("-n","--nick",help="Nickname for the eavesdropper (default %default)",action="store",type="string",default="-Eve-")
    p.add_option("-d","--delay",help="How often to say a quote speech by in seconds (default %default)",action="store",type="float",default=90)
    p.add_option("-q","--quote",help="Which file to load quotes from (default %default)",action="store",type="string",default="quotes.txt")
    p.add_option("--password",help="Password for server, if any",action="store",type="string")

    o, arguments = p.parse_args()

    s = MumbleClient.MumbleSettings()
    s._autojoin_joinChannel = o.channel
    s.delayTime = o.delay
    s.nickname = o.nick
    s.host = o.server
    s.port = o.port
    s.password = o.password
    s.quotefile = o.quote
    eve = AutoQuoteClient(s)
    eve.connect()
    reactor.run()


if __name__ == "__main__":
    main()
