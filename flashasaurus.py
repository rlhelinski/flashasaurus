#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Set up flash card sets in $HOME/.flashcards/filename
# where each filename defines an array called cards, like this:
# "1", "one"
# "2", "two"
# 
# It will look for .flashcards/all as a default, or you can pass
# the filename as an argument, e.g. flashcard shortlist will
# use the cards defined in $HOME/.flashcard/shortlist.
#
# Copyright 2007 by Akkana Peck.
# This program is free software -- please share it under the terms
# of the GNU Public License.

import os, sys, random, csv, gtk

def PromptFileName():
    dialog = gtk.FileChooserDialog("Choose flash card CSV file", None, gtk.FILE_CHOOSER_ACTION_OPEN,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                   gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    filter = gtk.FileFilter()
    filter.set_name("CSV files")
    filter.add_pattern("*.csv")
    dialog.add_filter(filter)

    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    dialog.add_filter(filter)

    response = dialog.run()
    if response == gtk.RESPONSE_OK:
        filename = dialog.get_filename()

    elif response == gtk.RESPONSE_CANCEL:
        raise NameError("No file selected")
    dialog.destroy()

    return filename

def findCardFile():
    if (len (sys.argv) > 1):
        cardfile = sys.argv[1]
    else:
        tildefile = os.path.join(os.path.expanduser("~"), ".flashcards")
        if (os.path.exists(tildefile)) :
            cardfile = tildefile
        else:
            #raise NameError("No file specified and none found at %s" % tildefile)
            cardfile = PromptFileName()

    print "Using '%s' as card file" % cardfile
    return cardfile

class Dealer:
    pair = 0
    
    def __init__(self, cardfile=False):
        if (cardfile):
            self.loadCards(cardfile)
    
    def loadCards(self, cardfile):
    
        self.cards = []
        
        fileReader = csv.reader(open(cardfile), delimiter=',', quotechar='"')
        for row in fileReader:
            self.cards.append(row)
                                      
        if len(self.cards) > 0 :
            print "Read", len(self.cards), "cards from", cardfile
        
        print ""
    
    def shuffle(self):
        self.shuffledIndexes = range(0, len(self.cards))
        random.shuffle(self.shuffledIndexes)
        
    def next(self):
        if self.pair < len(self.cards) - 1:
            self.pair += 1
        else:
            self.pair = 0
        
    def prev(self):
        if self.pair > 0:
            self.pair -= 1
        else:
            self.pair = len(self.cards) - 1
        
    def current(self):
        return self.cards[self.shuffledIndexes[self.pair]]
    
    def progress(self):
        return self.pair + 1, len(self.cards)


class GtkUI:

    cards = []
    pair = 0
    showing = False
    
    def __init__(self, dealer=False):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Flashasaurus")
        #self.window.set_size_request(320, 240)
        self.window.set_border_width(10)
        self.window.set_position(gtk.WIN_POS_CENTER)
        #self.window.set_icon(pumppb)
        
        #table = gtk.Table(6, 2, False)
        #table.attach(myLabel, 1, 2, i, i + 1, ypadding=4, xpadding=8)
        vbox = gtk.VBox(False, 10)
        #vbox.set_property("padding", 10)
        
        
        self.labelWord = gtk.Label("the word")
        vbox.pack_start(self.labelWord, False, False, 0)
        
        self.labelDef = gtk.Label("the definition")
        #self.labelDef.set_size_request(320,64)
        self.labelDef.set_width_chars(48)
        self.labelDef.set_justify(gtk.JUSTIFY_CENTER)
        self.labelDef.set_alignment(0.5, 0.5)
        # still doesn't always wrap ?
        self.labelDef.set_single_line_mode(False)
        self.labelDef.set_line_wrap(True)
        vbox.add(self.labelDef)
        
        separator = gtk.HSeparator()
        vbox.add(separator)
        
        #bbox = gtk.HButtonBox()
        bbox = gtk.HBox(False, 10)
        self.buttonBack = gtk.Button(label="Back", stock=gtk.STOCK_GO_BACK)
        self.buttonBack.connect("activate", self.onClickBackward)
        self.buttonBack.connect("clicked", self.onClickBackward)
        bbox.add(self.buttonBack)
        
        self.labelIndex = gtk.Label("#")
        bbox.add(self.labelIndex)
        
        self.buttonShow = gtk.Button(label="Show", stock=gtk.STOCK_NO)
        self.buttonShow.connect("activate", self.onClickShow)
        self.buttonShow.connect("clicked", self.onClickShow)
        alignment = self.buttonShow.get_children()[0]
        hbox = alignment.get_children()[0]
        self.buttonShowImage, self.buttonShowLabel = hbox.get_children()
        self.buttonShowLabel.set_text('Show')
        bbox.add(self.buttonShow)
        
        self.buttonForward = gtk.Button(label="Forward", stock=gtk.STOCK_GO_FORWARD)
        self.buttonForward.connect("activate", self.onClickForward)
        self.buttonForward.connect("clicked", self.onClickForward)
        bbox.add(self.buttonForward)
        
        vbox.pack_end(bbox)
        
        self.window.add(vbox)
        
        self.window.connect("destroy", self.quit)
        self.window.connect('delete_event', self.quit)
        self.window.show_all()
        
        if(dealer):
            self.dealer = dealer
            self.dealer.shuffle()
            self.update()
        
    def quit(self, widget, data=None):
        gtk.main_quit()
        
    def onClickForward(self, widget):
        self.dealer.next()
        self.showing = False
        self.update()
        
    def onClickBackward(self, widget):
        self.dealer.prev()
        self.update()
        
    def onClickShow(self, widget):
        self.showing = not self.showing
        self.update()
        
    def update(self):
        word, defin = self.dealer.current()
        self.labelWord.set_markup("<span size='x-large'>%s</span>" % word)
        if (self.showing):
            #self.labelDef.set_label(defin)
            self.labelDef.set_label(defin)
            self.buttonShowLabel.set_text("Hide")
            self.buttonShowImage.set_from_stock('gtk-yes', gtk.ICON_SIZE_BUTTON)
        else:
            self.labelDef.set_markup("<span foreground='gray'>Click Show to see definition</span>")
            self.buttonShowLabel.set_text("Show")
            self.buttonShowImage.set_from_stock('gtk-no', gtk.ICON_SIZE_BUTTON) 
        self.labelIndex.set_label("%d / %d" % (self.dealer.progress()))



cardfile = findCardFile()
dealer = Dealer(cardfile)
GtkUI(dealer)

gtk.main()