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

from twisted.internet import reactor, task


class AutoQuoteClient(MumbleClient.AutoChannelJoinClient):

    memes = []
    def load_memes_usa(self,memefile):
        with open(memefile,'r') as memular:
            for meme in memular:
                if meme.strip()!="":
                    self.memes.append(meme.strip())

    def memetownusa(self):
        self.sendTextMessage(self.memes[int(random.random()*len(self.memes))])
        v = task.deferLater(reactor,self.settings.delayTime,self.memetownusa)
        v.addErrback(self.errorCallback)

    def TextMessageReceived(self,message):
        if( "mwo" in message.message.lower() or 
            "mechwarrior" in message.message.lower() or 
            "pgi" in message.message.lower() or 
            "robots" in message.message.lower()):
            name = self.state.users[message.actor].name
            self.sendTextMessage("Please Leave %s, This is the Star Citizen channel. We don't talk about MWO here." %name)
        
    def ServerSyncReceived(self,message):
        self.load_memes_usa(self.settings.memefile)
        v = task.deferLater(reactor,5,self.memetownusa)
        v.addErrback(self.errorCallback)

    def connectionLost(self,reason):
        if reactor.running: reactor.stop()

def main():
    p = optparse.OptionParser(description='Mumble 1.2 relaybot to relay comms from a match channel to a spectator channel, with a time delay e.g. if watching on a delayed SourceTV server. Full documentation is available at http://frymaster.127001.org/mumble',
                prog='eve-bot2.py',
                version='%prog 2.0',
                usage='\t%prog -e \"Match Channel\" -r \"Spectator Channel\"')

    p.add_option("-e","--channel",help="Channel to start in (MANDATORY)",action="store",type="string")
    p.add_option("-s","--server",help="Host to connect to (default %default)",action="store",type="string",default="localhost")
    p.add_option("-p","--port",help="Port to connect to (default %default)",action="store",type="int",default=64738)
    p.add_option("-n","--nick",help="Nickname for the eavesdropper (default %default)",action="store",type="string",default="-Eve-")
    p.add_option("-d","--delay",help="How often to say a quote speech by in seconds (default %default)",action="store",type="float",default=90)
    p.add_option("-m","--meme",help="Which file to load memes from (default %default)",action="store",type="string",default="memes.txt")
    p.add_option("--password",help="Password for server, if any",action="store",type="string")

    o, arguments = p.parse_args()

    s = MumbleClient.MumbleSettings()
    s._autojoin_joinChannel = o.channel
    s.delayTime = o.delay
    s.nickname = o.nick
    s.host = o.server
    s.port = o.port
    s.password = o.password
    s.memefile = o.meme
    eve = AutoQuoteClient(s)
    eve.connect()
    reactor.run()


if __name__ == "__main__":
    main()
